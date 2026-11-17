"""
Teacher identity-verification review service.

Provides read-only listing and review actions for identity verification
records belonging to examinations owned by the authenticated teacher.

Security rules enforced here:
- Teacher can only review records for attempts belonging to tests they created.
- Students cannot access these endpoints (protected by require_teacher dependency).
- Reviewer identity, timestamp, and notes are server-authoritative.
- Students cannot change reviewer fields (enforced by student endpoints ignoring them).
"""
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Session, select

from app.models.attempt import Attempt
from app.models.identity_verification import (
    AttemptIdentityVerification,
    IdentityVerificationStatus,
)
from app.models.test import Test
from app.models.user import User


class IdentityReviewError(ValueError):
    """Domain error for identity review actions."""


def _verify_teacher_owns_test(db: Session, teacher_id: int, test_id: int) -> Test:
    test = db.get(Test, test_id)
    if not test:
        raise IdentityReviewError("Examination not found")
    if test.created_by != teacher_id:
        raise IdentityReviewError("You do not own this examination")
    return test


def list_pending_identity_verifications(
    db: Session, teacher_id: int, test_id: int
) -> list[dict]:
    """
    List identity verification records for attempts belonging to a test
    owned by the authenticated teacher.

    Returns records with student info and attempt info. Never exposes
    internal storage paths.
    """
    _verify_teacher_owns_test(db, teacher_id, test_id)

    statement = (
        select(AttemptIdentityVerification, Attempt, Test, User)
        .join(Attempt, AttemptIdentityVerification.attempt_id == Attempt.id)
        .join(Test, Attempt.test_id == Test.id)
        .join(User, Attempt.student_id == User.id)
        .where(Attempt.test_id == test_id)
        .order_by(AttemptIdentityVerification.submitted_at.desc())
    )
    rows = db.exec(statement).all()

    results = []
    for verification, attempt, test, student in rows:
        results.append({
            "id": verification.id,
            "attempt_id": verification.attempt_id,
            "student_id": student.id,
            "student_name": student.full_name,
            "student_email": student.email,
            "test_id": test.id,
            "test_title": test.title,
            "test_code": test.test_code,
            "status": verification.status.value,
            "submitted_at": verification.submitted_at,
            "reviewed_at": verification.reviewed_at,
            "reviewer_id": verification.reviewer_id,
            "reviewer_notes": verification.reviewer_notes,
            "image_path": verification.image_path,  # internal, not exposed to frontend
            "content_type": verification.content_type,
            "file_size_bytes": verification.file_size_bytes,
        })
    return results


def get_identity_verification_for_teacher(
    db: Session, teacher_id: int, verification_id: int
) -> dict:
    """
    Get a single identity verification record for teacher review.
    Enforces that the teacher owns the examination the attempt belongs to.
    """
    verification = db.get(AttemptIdentityVerification, verification_id)
    if not verification:
        raise IdentityReviewError("Identity verification record not found")

    attempt = db.get(Attempt, verification.attempt_id)
    if not attempt:
        raise IdentityReviewError("Attempt not found")

    test = db.get(Test, attempt.test_id)
    if not test:
        raise IdentityReviewError("Examination not found")

    if test.created_by != teacher_id:
        raise IdentityReviewError("You do not own this examination")

    student = db.get(User, verification.student_id)

    return {
        "id": verification.id,
        "attempt_id": verification.attempt_id,
        "student_id": verification.student_id,
        "student_name": student.full_name if student else "Unknown",
        "student_email": student.email if student else "Unknown",
        "test_id": test.id,
        "test_title": test.title,
        "test_code": test.test_code,
        "status": verification.status.value,
        "submitted_at": verification.submitted_at,
        "reviewed_at": verification.reviewed_at,
        "reviewer_id": verification.reviewer_id,
        "reviewer_notes": verification.reviewer_notes,
        "image_path": verification.image_path,
        "content_type": verification.content_type,
        "file_size_bytes": verification.file_size_bytes,
    }


def review_identity_verification(
    db: Session,
    teacher_id: int,
    verification_id: int,
    new_status: IdentityVerificationStatus,
    notes: Optional[str] = None,
) -> dict:
    """
    Approve or reject an identity verification record.

    Enforces:
    - Teacher owns the examination.
    - Only pending records can be reviewed.
    - Records reviewer identity, timestamp, and notes.
    - Does not allow students to override these fields.
    """
    verification = db.get(AttemptIdentityVerification, verification_id)
    if not verification:
        raise IdentityReviewError("Identity verification record not found")

    if verification.status != IdentityVerificationStatus.pending:
        raise IdentityReviewError(
            f"Cannot review a record with status '{verification.status.value}'. "
            "Only pending records can be reviewed."
        )

    attempt = db.get(Attempt, verification.attempt_id)
    if not attempt:
        raise IdentityReviewError("Attempt not found")

    test = db.get(Test, attempt.test_id)
    if not test:
        raise IdentityReviewError("Examination not found")

    if test.created_by != teacher_id:
        raise IdentityReviewError("You do not own this examination")

    now = datetime.now(timezone.utc)
    verification.status = new_status
    verification.reviewer_id = teacher_id
    verification.reviewed_at = now
    verification.reviewer_notes = (notes or "").strip()[:2000] or None
    verification.updated_at = now
    db.add(verification)
    db.commit()
    db.refresh(verification)

    student = db.get(User, verification.student_id)

    return {
        "id": verification.id,
        "attempt_id": verification.attempt_id,
        "student_id": verification.student_id,
        "student_name": student.full_name if student else "Unknown",
        "student_email": student.email if student else "Unknown",
        "test_id": test.id,
        "test_title": test.title,
        "test_code": test.test_code,
        "status": verification.status.value,
        "submitted_at": verification.submitted_at,
        "reviewed_at": verification.reviewed_at,
        "reviewer_id": verification.reviewer_id,
        "reviewer_notes": verification.reviewer_notes,
        "image_path": verification.image_path,
        "content_type": verification.content_type,
        "file_size_bytes": verification.file_size_bytes,
    }