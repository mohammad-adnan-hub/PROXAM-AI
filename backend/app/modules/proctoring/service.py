from collections import defaultdict
from datetime import datetime, timezone
from sqlalchemy import update as sql_update
import threading
import time
from typing import Optional

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.attempt import Attempt, AttemptStatus
from app.models.attempt import Attempt, AttemptStatus
from app.models.proctoring_event import EventType, ProctoringEvent, ReviewStatus
from app.modules.proctoring.schemas import ProctoringEventCreate
from app.modules.students.service import _finalize_attempt_if_expired, _finalize_attempt

# Event types that count as qualifying warnings toward the 3-warning limit.
QUALIFYING_WARNING_EVENTS: set[EventType] = {
    EventType.face_not_detected,
    EventType.multiple_faces_detected,
    EventType.looking_away,
    EventType.fullscreen_exited,
    EventType.tab_visibility_changed,
    EventType.camera_disconnected,
    EventType.microphone_unavailable,
    EventType.identity_check_failed,
    EventType.phone_detected,
}
# Severity serves as a review-priority indicator for teachers/reviewers,
# not as proof or verdict of misconduct.
DEFAULT_EVENT_SEVERITY: dict[EventType, str] = {
    EventType.face_not_detected: "medium",
    EventType.multiple_faces_detected: "high",
    EventType.looking_away: "low",
    EventType.fullscreen_exited: "medium",
    EventType.tab_visibility_changed: "medium",
    EventType.camera_disconnected: "high",
    EventType.microphone_unavailable: "low",
    EventType.network_interrupted: "low",
    EventType.identity_check_failed: "high",
    EventType.phone_detected: "high",
}


class ProctoringRateLimiter:
    """
    In-memory, thread-safe sliding window rate limiter for proctoring events.

    Limits repeated events for the same attempt and event category.
    Thread-safe within a single application process via threading.Lock.

    NOTE ON MULTI-WORKER DEPLOYMENTS:
    This rate limiter uses process-local memory. In multi-process deployments
    (e.g., Uvicorn workers > 1 or multiple container replicas), an external
    shared store such as Redis would be required for cluster-wide synchronization.
    """

    def __init__(self, max_events: int = 5, window_seconds: float = 10.0):
        self.max_events = max_events
        self.window_seconds = window_seconds
        self._lock = threading.Lock()
        self._history: dict[tuple[int, EventType], list[float]] = defaultdict(list)

    def check_limit(self, attempt_id: int, event_type: EventType) -> bool:
        """
        Check if an event submission exceeds the configured limit.
        Returns True if the event is permitted, False if rate-limited.
        """
        now = time.monotonic()
        key = (attempt_id, event_type)
        with self._lock:
            timestamps = self._history[key]
            cutoff = now - self.window_seconds
            valid_timestamps = [t for t in timestamps if t > cutoff]
            if len(valid_timestamps) >= self.max_events:
                self._history[key] = valid_timestamps
                return False
            valid_timestamps.append(now)
            self._history[key] = valid_timestamps
            return True

    def reset(self) -> None:
        """Reset internal rate limiting history, primarily for testing purposes."""
        with self._lock:
            self._history.clear()


# Global singleton instance for application process
rate_limiter = ProctoringRateLimiter(max_events=5, window_seconds=10.0)


def record_student_proctoring_event(
    db: Session,
    student_id: int,
    attempt_id: int,
    payload: ProctoringEventCreate,
) -> ProctoringEvent:
    """
    Record a browser-detected proctoring event for an active student attempt.

    Enforces:
    1. Attempt exists.
    2. Student owns the attempt.
    3. Attempt is strictly 'in_progress' and has not expired.
    4. Rate-limiting per attempt and event category.
    5. Server-authoritative receipt timestamp.
    6. Centralized server-authoritative severity determination.
    7. No student modification of reviewer fields or review status.
    """
    attempt = db.get(Attempt, attempt_id)
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found",
        )

    if attempt.student_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this attempt",
        )

    if attempt.status == AttemptStatus.created:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Attempt has not been started",
        )

    if attempt.status == AttemptStatus.submitted:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Attempt has already been submitted",
        )

    if attempt.status == AttemptStatus.timed_out:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Attempt has timed out",
        )

    if attempt.status != AttemptStatus.in_progress:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Attempt is not in progress",
        )

    if _finalize_attempt_if_expired(db, attempt):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Examination time has expired",
        )

    if attempt.status == AttemptStatus.terminated_by_warnings:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Examination has been terminated due to excessive warnings",
        )

    # Event flooding protection check
    if not rate_limiter.check_limit(attempt_id, payload.event_type):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many proctoring events reported. Please wait before submitting again.",
        )

    # Qualifying warning handling: increment count
    is_qualifying = payload.event_type in QUALIFYING_WARNING_EVENTS
    if is_qualifying:
        # Atomic increment with conditional check
        stmt = sql_update(Attempt).where(
            Attempt.id == attempt_id,
            Attempt.status == AttemptStatus.in_progress,
            Attempt.warning_count < 4,
        ).values(warning_count=Attempt.warning_count + 1)
        db.exec(stmt)
        db.commit()
        db.refresh(attempt)

    # Server-authoritative timestamp & severity
    server_now = datetime.now(timezone.utc)
    authoritative_severity = DEFAULT_EVENT_SEVERITY.get(payload.event_type, "low")

    description = payload.description
    if payload.client_timestamp:
        client_ts_str = payload.client_timestamp.isoformat()
        client_note = f"[client_ts: {client_ts_str}]"
        description = f"{description} {client_note}".strip() if description else client_note

    if description is not None:
        description = description[:1000]

    event = ProctoringEvent(
        attempt_id=attempt.id,
        event_type=payload.event_type,
        severity=authoritative_severity,
        timestamp=server_now,
        description=description,
        duration_seconds=payload.duration_seconds,
        review_status=ReviewStatus.unreviewed,
        reviewer_id=None,
        reviewer_notes=None,
        reviewed_at=None,
    )
    db.add(event)

    # Terminate on 4th qualifying warning (after persisting the event)
    if is_qualifying and attempt.warning_count >= 4:
        _finalize_attempt(
            db, attempt_id, student_id, AttemptStatus.terminated_by_warnings,
            server_now,
        )

    db.commit()
    db.refresh(event)
    db.refresh(attempt)

    if is_qualifying and attempt.warning_count >= 4:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Examination terminated due to excessive warnings",
                "warning_count": attempt.warning_count,
            },
        )

    return event


def list_proctoring_events(
    db: Session,
    attempt_id: int,
    current_user_id: int,
    is_admin: bool,
) -> list[ProctoringEvent]:
    """Return proctoring events for an attempt, ordered chronologically.

    Authorization (ownership) is enforced by the caller/router; this function
    only loads and orders events. Raises 404 if the attempt does not exist.
    """
    attempt = db.get(Attempt, attempt_id)
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found",
        )

    # Ownership check: attempt -> test -> created_by
    from app.models.test import Test

    test = db.get(Test, attempt.test_id)
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found",
        )
    if not is_admin and test.created_by != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    events = db.exec(
        select(ProctoringEvent)
        .where(ProctoringEvent.attempt_id == attempt_id)
        .order_by(ProctoringEvent.timestamp, ProctoringEvent.id)
    ).all()
    return list(events)


def review_proctoring_event(
    db: Session,
    attempt_id: int,
    event_id: int,
    current_user_id: int,
    is_admin: bool,
    review_status: ReviewStatus,
    reviewer_notes: Optional[str],
) -> ProctoringEvent:
    attempt = db.get(Attempt, attempt_id)
    if not attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")

    from app.models.test import Test

    test = db.get(Test, attempt.test_id)
    if not test or (not is_admin and test.created_by != current_user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    from app.models.proctoring_event import ProctoringEvent, ProctoringReviewAudit

    event = db.get(ProctoringEvent, event_id)
    if not event or event.attempt_id != attempt_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    previous_status = event.review_status
    previous_notes = event.reviewer_notes

    event.review_status = review_status
    event.reviewer_id = current_user_id
    event.reviewer_notes = reviewer_notes
    now = datetime.now(timezone.utc)
    event.reviewed_at = now

    audit = ProctoringReviewAudit(
        proctoring_event_id=event.id,
        reviewer_id=current_user_id,
        previous_review_status=previous_status,
        new_review_status=review_status,
        previous_reviewer_notes=previous_notes,
        new_reviewer_notes=reviewer_notes,
        reviewed_at=now,
    )

    db.add(event)
    db.add(audit)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(event)
    return event
