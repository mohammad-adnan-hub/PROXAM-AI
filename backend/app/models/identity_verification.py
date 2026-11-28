from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import Column, LargeBinary
from sqlmodel import Field, SQLModel, UniqueConstraint


class IdentityVerificationStatus(str, Enum):
    not_submitted = "not_submitted"
    pending = "pending"
    verified = "verified"
    rejected = "rejected"


class AttemptIdentityVerification(SQLModel, table=True):
    __tablename__ = "attempt_identity_verifications"
    __table_args__ = (
        UniqueConstraint("attempt_id", name="uq_attempt_identity_verification_attempt"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    attempt_id: int = Field(foreign_key="attempts.id", index=True)
    student_id: int = Field(foreign_key="users.id", index=True)
    status: IdentityVerificationStatus = Field(default=IdentityVerificationStatus.not_submitted)
    image_data: Optional[bytes] = Field(default=None, sa_column=Column("image_data", LargeBinary, nullable=True))
    image_path: Optional[str] = Field(default=None, max_length=500)
    original_filename: Optional[str] = Field(default=None, max_length=255)
    content_type: Optional[str] = Field(default=None, max_length=100)
    file_size_bytes: Optional[int] = Field(default=None)
    submitted_at: Optional[datetime] = Field(default=None)
    reviewer_id: Optional[int] = Field(default=None, foreign_key="users.id")
    reviewed_at: Optional[datetime] = Field(default=None)
    reviewer_notes: Optional[str] = Field(default=None, max_length=2000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
