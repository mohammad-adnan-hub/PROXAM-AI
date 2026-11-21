from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.models.proctoring_event import EventType, ReviewStatus


class ProctoringEventCreate(BaseModel):
    event_type: EventType
    description: Optional[str] = Field(default=None, max_length=1000)
    duration_seconds: Optional[float] = Field(default=None, ge=0.0, le=86400.0)
    client_timestamp: Optional[datetime] = None
    severity: Optional[str] = Field(default=None, max_length=10)

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip().lower()
            if v not in ("low", "medium", "high"):
                raise ValueError("Severity must be 'low', 'medium', or 'high'")
        return v

    model_config = {"extra": "forbid"}


class ProctoringEventResponse(BaseModel):
    id: int
    attempt_id: int
    event_type: EventType
    severity: str
    timestamp: datetime
    description: Optional[str] = None
    duration_seconds: Optional[float] = None
    review_status: ReviewStatus
    warning_count: int = 0

    model_config = {"from_attributes": True}


class ProctoringEventDetailResponse(BaseModel):
    id: int
    attempt_id: int
    event_type: EventType
    severity: str
    timestamp: datetime
    description: Optional[str] = None
    duration_seconds: Optional[float] = None
    review_status: ReviewStatus
    reviewer_id: Optional[int] = None
    reviewer_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ProctoringEventReviewRequest(BaseModel):
    review_status: ReviewStatus
    reviewer_notes: Optional[str] = Field(default=None, max_length=2000)

    model_config = {"extra": "forbid"}


class ProctoringReviewAuditResponse(BaseModel):
    id: int
    proctoring_event_id: int
    reviewer_id: int
    previous_review_status: ReviewStatus
    new_review_status: ReviewStatus
    previous_reviewer_notes: Optional[str] = None
    new_reviewer_notes: Optional[str] = None
    reviewed_at: datetime

    model_config = {"from_attributes": True}
