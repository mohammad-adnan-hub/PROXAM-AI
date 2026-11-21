from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.dependencies import get_db, require_teacher_or_admin, require_admin
from app.models.user import User, UserRole
from app.modules.proctoring import service
from app.modules.proctoring.schemas import ProctoringEventDetailResponse, ProctoringEventReviewRequest

review_router = APIRouter(prefix="/proctoring", tags=["proctoring-review"])


@review_router.get(
    "/attempts/{attempt_id}/events",
    response_model=list[ProctoringEventDetailResponse],
    status_code=status.HTTP_200_OK,
)
def get_proctoring_events(
    attempt_id: int,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
) -> list[ProctoringEventResponse]:
    events = service.list_proctoring_events(
        db=db,
        attempt_id=attempt_id,
        current_user_id=current_user.id,
        is_admin=current_user.role == UserRole.admin,
    )
    return [ProctoringEventDetailResponse.model_validate(e) for e in events]

@review_router.put(
    "/attempts/{attempt_id}/events/{event_id}",
    response_model=ProctoringEventDetailResponse,
    status_code=status.HTTP_200_OK,
)
def review_proctoring_event(
    attempt_id: int,
    event_id: int,
    payload: ProctoringEventReviewRequest,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
) -> ProctoringEventDetailResponse:
    event = service.review_proctoring_event(
        db=db,
        attempt_id=attempt_id,
        event_id=event_id,
        current_user_id=current_user.id,
        is_admin=current_user.role == UserRole.admin,
        review_status=payload.review_status,
        reviewer_notes=payload.reviewer_notes,
    )
    return ProctoringEventDetailResponse.model_validate(event)
