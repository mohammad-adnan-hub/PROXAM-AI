from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel, UniqueConstraint


class AttemptStatus(str, Enum):
    in_progress = "in_progress"
    submitted = "submitted"
    timed_out = "timed_out"


class Attempt(SQLModel, table=True):
    __tablename__ = "attempts"
    __table_args__ = (
        UniqueConstraint("student_id", "test_id", name="uq_student_test_attempt"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    test_id: int = Field(foreign_key="tests.id", index=True)
    student_id: int = Field(foreign_key="users.id", index=True)
    status: AttemptStatus = Field(default=AttemptStatus.in_progress)
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    submitted_at: Optional[datetime] = Field(default=None)
    time_limit_ends_at: datetime
    identity_verified: bool = Field(default=False)
