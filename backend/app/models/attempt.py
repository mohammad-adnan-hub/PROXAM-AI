from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel, UniqueConstraint


class AttemptStatus(str, Enum):
    created = "created"
    in_progress = "in_progress"
    submitted = "submitted"
    timed_out = "timed_out"
    terminated_by_warnings = "terminated_by_warnings"


class Attempt(SQLModel, table=True):
    __tablename__ = "attempts"
    __table_args__ = (
        UniqueConstraint("student_id", "test_id", name="uq_student_test_attempt"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    test_id: int = Field(foreign_key="tests.id", index=True)
    student_id: int = Field(foreign_key="users.id", index=True)
    status: AttemptStatus = Field(default=AttemptStatus.created)
    started_at: Optional[datetime] = Field(default=None)
    submitted_at: Optional[datetime] = Field(default=None)
    time_limit_ends_at: Optional[datetime] = Field(default=None)
    identity_verified: bool = Field(default=False)
    warning_count: int = Field(default=0)
    created_at: Optional[datetime] = Field(default=None)
