from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel


class EventType(str, Enum):
    face_not_detected = "face_not_detected"
    multiple_faces_detected = "multiple_faces_detected"
    looking_away = "looking_away"
    fullscreen_exited = "fullscreen_exited"
    tab_visibility_changed = "tab_visibility_changed"
    camera_disconnected = "camera_disconnected"
    microphone_unavailable = "microphone_unavailable"
    network_interrupted = "network_interrupted"
    identity_check_failed = "identity_check_failed"


class ReviewStatus(str, Enum):
    unreviewed = "unreviewed"
    under_review = "under_review"
    reviewed = "reviewed"
    no_concern = "no_concern"
    requires_further_review = "requires_further_review"


class ProctoringEvent(SQLModel, table=True):
    __tablename__ = "proctoring_events"

    id: Optional[int] = Field(default=None, primary_key=True)
    attempt_id: int = Field(foreign_key="attempts.id", index=True)
    event_type: EventType
    severity: str = Field(default="low", max_length=10)  # low, medium, high
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: Optional[str] = Field(default=None, max_length=1000)
    duration_seconds: Optional[float] = Field(default=None)
    review_status: ReviewStatus = Field(default=ReviewStatus.unreviewed)
    reviewer_id: Optional[int] = Field(default=None, foreign_key="users.id")
    reviewer_notes: Optional[str] = Field(default=None, max_length=2000)
    reviewed_at: Optional[datetime] = Field(default=None)
