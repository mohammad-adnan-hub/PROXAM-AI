from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.dependencies import get_db, require_student
from app.models.user import User
from app.modules.proctoring.schemas import ProctoringEventCreate, ProctoringEventResponse
from app.modules.proctoring import service

router = APIRouter(prefix="/student/attempts", tags=["student-proctoring"])


@router.post(
    "/{attempt_id}/proctoring-events",
    response_model=ProctoringEventResponse,
    status_code=status.HTTP_201_CREATED,
)
def record_student_proctoring_event(
    attempt_id: int,
    payload: ProctoringEventCreate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> ProctoringEventResponse:
    """
    Record a browser-detected proctoring event for an active student attempt.
    Enforces student ownership, in_progress attempt state, authoritative server
    timestamping, centralized severity assignment, and event flooding protection.
    """
    event = service.record_student_proctoring_event(
        db=db,
        student_id=current_user.id,
        attempt_id=attempt_id,
        payload=payload,
    )
    return ProctoringEventResponse.model_validate(event)
