"""
Teacher identity-verification review endpoints.

Provides:
- List pending identity verifications for a teacher's examination.
- Get a specific identity verification record for review.
- Approve or reject a pending identity verification.

All endpoints require teacher authentication and enforce examination ownership.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, Response
from sqlmodel import Session

from app.dependencies import get_db, require_teacher
from app.models.identity_verification import IdentityVerificationStatus
from app.models.user import User
from app.modules.identity_review import service as review_service
from app.modules.identity_review.schemas import (
    IdentityVerificationReviewResponse,
    IdentityVerificationListResponse,
    IdentityVerificationReviewRequest,
)
from app.modules.students.identity_storage import (
    IdentityImageStorageError,
    resolve_identity_image_path,
)

SUPPORTED_IDENTITY_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}

router = APIRouter(prefix="/teacher", tags=["teacher-identity-review"])


@router.get(
    "/tests/{test_id}/identity-verifications",
    response_model=list[IdentityVerificationListResponse],
    status_code=status.HTTP_200_OK,
)
def list_test_identity_verifications(
    test_id: int,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
) -> list[IdentityVerificationListResponse]:
    """
    List identity verification records for attempts belonging to a test
    owned by the authenticated teacher. Includes all statuses.
    """
    try:
        records = review_service.list_pending_identity_verifications(
            db, current_user.id, test_id
        )
    except review_service.IdentityReviewError as exc:
        detail = str(exc)
        lower = detail.lower()
        if "not found" in lower:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=detail
            )
        if "do not own" in lower:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=detail
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail
        )
    return [IdentityVerificationListResponse.model_validate(r) for r in records]


@router.get(
    "/identity-verifications/{verification_id}",
    response_model=IdentityVerificationReviewResponse,
    status_code=status.HTTP_200_OK,
)
def get_identity_verification_for_review(
    verification_id: int,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
) -> IdentityVerificationReviewResponse:
    """
    Get a single identity verification record for teacher review.
    Enforces examination ownership.
    """
    try:
        record = review_service.get_identity_verification_for_teacher(
            db, current_user.id, verification_id
        )
    except review_service.IdentityReviewError as exc:
        detail = str(exc)
        lower = detail.lower()
        if "not found" in lower:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=detail
            )
        if "do not own" in lower:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=detail
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail
        )
    return IdentityVerificationReviewResponse.model_validate(record)


@router.put(
    "/identity-verifications/{verification_id}",
    response_model=IdentityVerificationReviewResponse,
    status_code=status.HTTP_200_OK,
)
def review_identity_verification(
    verification_id: int,
    payload: IdentityVerificationReviewRequest,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
) -> IdentityVerificationReviewResponse:
    """
    Approve or reject a pending identity verification record.

    Only pending records can be reviewed. Records reviewer identity,
    timestamp, and optional notes.
    """
    try:
        record = review_service.review_identity_verification(
            db,
            teacher_id=current_user.id,
            verification_id=verification_id,
            new_status=payload.status,
            notes=payload.reviewer_notes,
        )
    except review_service.IdentityReviewError as exc:
        detail = str(exc)
        lower = detail.lower()
        if "not found" in lower:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=detail
            )
        if "do not own" in lower:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=detail
            )
        if "cannot review" in lower or "only pending" in lower:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=detail
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail
        )
    return IdentityVerificationReviewResponse.model_validate(record)


@router.get(
    "/identity-verifications/{verification_id}/image",
    status_code=status.HTTP_200_OK,
)
def get_identity_verification_image(
    verification_id: int,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
) -> FileResponse:
    """
    Return the identity verification image for teacher review.
    Requires teacher authentication and examination ownership.
    """
    try:
        record = review_service.get_identity_verification_for_teacher(
            db, current_user.id, verification_id
        )
    except review_service.IdentityReviewError as exc:
        detail = str(exc)
        lower = detail.lower()
        if "not found" in lower:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Identity verification image not found"
            )
        if "do not own" in lower:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=detail
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail
        )

    image_data = record.get("image_data")
    content_type = (record.get("content_type") or "").split(";")[0].strip().lower()

    if image_data:
        if content_type not in SUPPORTED_IDENTITY_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Identity verification image not found"
            )
        return Response(
            content=image_data,
            media_type=content_type,
            headers={
                "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )

    image_path = record.get("image_path")
    if not image_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Identity verification image not found"
        )

    try:
        resolved_path = resolve_identity_image_path(image_path)
    except IdentityImageStorageError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Identity verification image not found"
        )

    if content_type not in SUPPORTED_IDENTITY_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Identity verification image not found"
        )

    return FileResponse(
        str(resolved_path),
        media_type=content_type,
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )