from collections import defaultdict
from datetime import datetime, timezone
import threading
import time
from typing import Optional

from fastapi import HTTPException, status
from sqlmodel import Session

from app.models.attempt import Attempt, AttemptStatus
from app.models.proctoring_event import EventType, ProctoringEvent, ReviewStatus
from app.modules.proctoring.schemas import ProctoringEventCreate
from app.modules.students.service import _finalize_attempt_if_expired

# Centralized server-authoritative severity mapping.
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

    # Event flooding protection check
    if not rate_limiter.check_limit(attempt_id, payload.event_type):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many proctoring events reported. Please wait before submitting again.",
        )

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
    db.commit()
    db.refresh(event)
    return event
