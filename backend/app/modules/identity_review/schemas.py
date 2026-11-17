"""
Schemas for teacher identity-verification review endpoints.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

from app.models.identity_verification import IdentityVerificationStatus


class IdentityVerificationListResponse(BaseModel):
    """List item for teacher identity verification review."""
    id: int
    attempt_id: int
    student_id: int
    student_name: str
    student_email: str
    test_id: int
    test_title: str
    test_code: str
    status: str
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    reviewer_id: Optional[int] = None
    reviewer_notes: Optional[str] = None
    content_type: Optional[str] = None
    file_size_bytes: Optional[int] = None

    model_config = {"from_attributes": True}


class IdentityVerificationReviewResponse(BaseModel):
    """Full identity verification record for teacher review."""
    id: int
    attempt_id: int
    student_id: int
    student_name: str
    student_email: str
    test_id: int
    test_title: str
    test_code: str
    status: str
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    reviewer_id: Optional[int] = None
    reviewer_notes: Optional[str] = None
    image_path: Optional[str] = None
    content_type: Optional[str] = None
    file_size_bytes: Optional[int] = None

    model_config = {"from_attributes": True}


class IdentityVerificationReviewRequest(BaseModel):
    """Request to approve or reject an identity verification."""
    status: IdentityVerificationStatus
    reviewer_notes: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: IdentityVerificationStatus) -> IdentityVerificationStatus:
        if v not in (IdentityVerificationStatus.verified, IdentityVerificationStatus.rejected):
            raise ValueError(
                "Status must be 'verified' or 'rejected' for teacher review"
            )
        return v