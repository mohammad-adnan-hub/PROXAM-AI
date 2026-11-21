from typing import Optional
from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile, status
from sqlmodel import Session

from app.dependencies import get_db, require_student
from app.models.attempt import Attempt, AttemptStatus
from app.models.test import Test, TestStatus
from app.models.user import User
from app.modules.students import service
from app.modules.students.schemas import (
    StudentTestDetailsResponse,
    StudentTestValidationResponse,
    TestCodeValidationRequest,
    AttemptResponse,
    StudentQuestionResponse,
    StudentQuestionOptionResponse,
    AnswerSaveRequest,
    StudentAnswerResponse,
    ResultResponse,
    AttemptFinalizationResponse,
    AttemptHistoryItem,
    IdentityVerificationStatusResponse,
    IdentityVerificationSubmitResponse,
)
from app.models.option import Option
from app.models.result import Result
from sqlmodel import select


router = APIRouter(prefix="/student/tests", tags=["student-tests"])

# Separate router for attempt-scoped lifecycle endpoints
attempts_router = APIRouter(prefix="/student/attempts", tags=["student-attempts"])


@router.post(
    "/validate-code",
    response_model=StudentTestValidationResponse,
    status_code=status.HTTP_200_OK,
)
def validate_test_code(
    payload: TestCodeValidationRequest,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> StudentTestValidationResponse:
    """
    Validate a student examination code and return sanitized examination details
    with a signed validation token. Only active examinations are accessible.
    Never exposes questions, options, correct answers, or teacher information.
    """
    test = service.get_test_by_code(db, payload.test_code)
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid test code",
        )

    if test.status != TestStatus.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Examination is not currently active",
        )

    question_count = service.get_question_count(db, test.id)
    details = service.build_student_test_details(test, question_count)
    token = service.create_validation_token(current_user.id, test.id)
    details["validation_token"] = token
    return StudentTestValidationResponse.model_validate(details)


def _require_validation_or_existing_attempt(
    test_id: int,
    current_user: User,
    db: Session,
    validation_token: Optional[str] = None,
) -> None:
    """
    Authorize access to test details. Accepts either a valid validation token
    bound to this student and test, or an existing attempt belonging to the
    authenticated student for this test.
    """
    if validation_token:
        payload = service.verify_validation_token(validation_token)
        if payload:
            try:
                token_student_id = int(payload.get("sub", "0"))
                token_test_id = int(payload.get("test_id", 0))
            except (TypeError, ValueError):
                token_student_id = 0
                token_test_id = 0
            if (
                token_student_id == current_user.id
                and token_test_id == test_id
            ):
                return

    existing = service.get_existing_attempt(db, current_user.id, test_id)
    if existing:
        return

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Validation token required",
    )


@router.get(
    "/{test_id}",
    response_model=StudentTestDetailsResponse,
    status_code=status.HTTP_200_OK,
)
def get_student_test_details(
    test_id: int,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
    validation_token: Optional[str] = Header(None, alias="X-Validation-Token"),
) -> StudentTestDetailsResponse:
    """
    Retrieve sanitized examination details by ID for an authenticated student.
    Requires a valid validation token bound to this student and test, or an
    existing attempt belonging to the student. Only active examinations are
    accessible. Never exposes questions, options, correct answers, or teacher
    information.
    """
    _require_validation_or_existing_attempt(test_id, current_user, db, validation_token)

    test = db.get(Test, test_id)
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Examination not found",
        )

    if test.status != TestStatus.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Examination is not currently active",
        )

    question_count = service.get_question_count(db, test.id)
    return StudentTestDetailsResponse.model_validate(
        service.build_student_test_details(test, question_count)
    )


@router.post(
    "/{test_id}/attempt",
    response_model=AttemptResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_student_attempt(
    test_id: int,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> AttemptResponse:
    """
    Create a new examination attempt for the authenticated student.
    The examination timer is NOT started: time_limit_ends_at remains None
    until the student explicitly starts the examination in a later step.
    """
    try:
        attempt = service.create_attempt(db, current_user.id, test_id)
    except ValueError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            )
        if "not currently active" in str(exc).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(exc),
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )
    return AttemptResponse.model_validate(attempt)


@attempts_router.post(
    "/{attempt_id}/start",
    response_model=AttemptResponse,
    status_code=status.HTTP_200_OK,
)
def start_student_attempt(
    attempt_id: int,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> AttemptResponse:
    """
    Start an examination attempt. Transitions status from 'created' to
    'in_progress', records server-side started_at, and calculates
    time_limit_ends_at from the examination's duration_minutes.
    Idempotent: if already in_progress, returns the existing attempt
    without resetting timestamps.
    """
    try:
        attempt = service.start_attempt(db, current_user.id, attempt_id)
    except ValueError as exc:
        detail = str(exc)
        lower = detail.lower()
        if "not found" in lower:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=detail,
            )
        if "not currently active" in lower or "do not own" in lower:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=detail,
            )
        if "identity verification photo must be submitted" in lower:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=detail,
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )

    return AttemptResponse.model_validate(attempt)


@attempts_router.get(
    "/{attempt_id}/questions",
    response_model=list[StudentQuestionResponse],
    status_code=status.HTTP_200_OK,
)
def get_student_attempt_questions(
    attempt_id: int,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> list[StudentQuestionResponse]:
    """
    Retrieve questions for an in_progress attempt belonging to the student.
    Options are returned without is_correct to prevent answer leakage.
    Questions are ordered by order_index.
    """
    try:
        questions = service.get_attempt_questions(db, attempt_id, current_user.id)
    except ValueError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            )
        if "do not own" in str(exc).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(exc),
            )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )

    # Build student-facing response manually: options loaded separately
    # to avoid exposing Option.is_correct through model relationships.
    result = []
    for q in questions:
        options = db.exec(
            select(Option)
            .where(Option.question_id == q.id)
            .order_by(Option.label)
        ).all()
        result.append({
            "id": q.id,
            "question_text": q.question_text,
            "marks": q.marks,
            "order_index": q.order_index,
            "options": [
                {
                    "id": o.id,
                    "label": o.label,
                    "option_text": o.option_text,
                }
                for o in options
            ],
        })
    return [StudentQuestionResponse.model_validate(item) for item in result]


@attempts_router.put(
    "/{attempt_id}/answers/{question_id}",
    response_model=StudentAnswerResponse,
    status_code=status.HTTP_200_OK,
)
def save_student_answer(
    attempt_id: int,
    question_id: int,
    payload: AnswerSaveRequest,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> StudentAnswerResponse:
    """
    Save or update a student's answer for a question in an in_progress attempt.
    Creates a new answer if none exists, otherwise updates the existing one.
    Rejects if the attempt is not in_progress or the examination deadline has passed.
    """
    try:
        answer = service.save_answer(
            db,
            attempt_id,
            current_user.id,
            question_id,
            payload.selected_option_id,
            payload.is_marked_for_review,
        )
    except ValueError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            )
        if "do not own" in str(exc).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(exc),
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )
    return StudentAnswerResponse.model_validate(answer)


@attempts_router.get(
    "/{attempt_id}/answers",
    response_model=list[StudentAnswerResponse],
    status_code=status.HTTP_200_OK,
)
def get_student_answers(
    attempt_id: int,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> list[StudentAnswerResponse]:
    """
    Retrieve all saved answers for an attempt belonging to the student.
    """
    try:
        answers = service.get_answers(db, attempt_id, current_user.id)
    except ValueError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            )
        if "do not own" in str(exc).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(exc),
            )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )
    return [StudentAnswerResponse.model_validate(a) for a in answers]


@attempts_router.delete(
    "/{attempt_id}/answers/{question_id}",
    status_code=status.HTTP_200_OK,
)
def clear_student_answer(
    attempt_id: int,
    question_id: int,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    """
    Clear a student's answer for a question (deselect the option).
    Preserves is_marked_for_review and updates saved_at.
    Returns a consistent success response whether or not an answer existed.
    """
    try:
        answer = service.clear_answer(
            db,
            attempt_id,
            current_user.id,
            question_id,
        )
    except ValueError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            )
        if "do not own" in str(exc).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(exc),
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    if answer is None:
        return {
            "detail": "No answer to clear",
            "question_id": question_id,
        }
    return {
        "detail": "Answer cleared",
        "question_id": question_id,
        "answer": StudentAnswerResponse.model_validate(answer),
    }


@attempts_router.get(
    "/{attempt_id}/result",
    response_model=ResultResponse,
    status_code=status.HTTP_200_OK,
)
def get_student_attempt_result(
    attempt_id: int,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> ResultResponse:
    """
    Retrieve the result for a finalized attempt belonging to the student.
    Returns 409 if the attempt has not been finalized or no result exists.
    Never exposes another student's result.
    """
    attempt = db.get(Attempt, attempt_id)
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found",
        )

    if attempt.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this attempt",
        )

    if attempt.status not in (AttemptStatus.submitted, AttemptStatus.timed_out, AttemptStatus.terminated_by_warnings):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Attempt has not been finalized",
        )

    result = db.exec(
        select(Result).where(Result.attempt_id == attempt_id)
    ).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Result not yet available",
        )

    return ResultResponse.model_validate({
        "id": result.id,
        "attempt_id": result.attempt_id,
        "score": result.score,
        "total_marks": result.total_marks,
        "correct_count": result.correct_count,
        "incorrect_count": result.incorrect_count,
        "unanswered_count": result.unanswered_count,
        "percentage": result.percentage,
        "calculated_at": result.calculated_at,
        "status": attempt.status,
    })


@attempts_router.post(
    "/{attempt_id}/submit",
    response_model=AttemptFinalizationResponse,
    status_code=status.HTTP_200_OK,
)
def submit_student_attempt(
    attempt_id: int,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> AttemptFinalizationResponse:
    """
    Finalize an examination attempt. Transitions status to 'submitted' if
    finalized on or before the deadline, or 'timed_out' if the deadline
    has passed. Sets submitted_at and calculates/persists the result.

    Idempotent: if the attempt is already finalized, returns the existing
    attempt without creating a duplicate result.
    """
    try:
        attempt = service.submit_attempt(db, attempt_id, current_user.id)
    except ValueError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            )
        if "do not own" in str(exc).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(exc),
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    result = None
    existing_result = db.exec(
        select(Result).where(Result.attempt_id == attempt_id)
    ).first()
    if existing_result:
        result = ResultResponse.model_validate({
            "id": existing_result.id,
            "attempt_id": existing_result.attempt_id,
            "score": existing_result.score,
            "total_marks": existing_result.total_marks,
            "correct_count": existing_result.correct_count,
            "incorrect_count": existing_result.incorrect_count,
            "unanswered_count": existing_result.unanswered_count,
            "percentage": existing_result.percentage,
            "calculated_at": existing_result.calculated_at,
            "status": attempt.status,
        })

    return AttemptFinalizationResponse.model_validate({
        "id": attempt.id,
        "test_id": attempt.test_id,
        "student_id": attempt.student_id,
        "status": attempt.status,
        "started_at": attempt.started_at,
        "submitted_at": attempt.submitted_at,
        "time_limit_ends_at": attempt.time_limit_ends_at,
        "created_at": attempt.created_at,
        "identity_verified": attempt.identity_verified,
        "result": result,
    })


@attempts_router.post(
    "/{attempt_id}/identity-verification",
    response_model=IdentityVerificationSubmitResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_identity_verification(
    attempt_id: int,
    photo: UploadFile = File(...),
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> IdentityVerificationSubmitResponse:
    """
    Submit a one-time identity photograph for the authenticated student's own attempt.
    Stores image privately and sets status to pending review. Does not auto-verify.
    """
    content = await photo.read()
    try:
        record = service.submit_identity_verification_photo(
            db=db,
            attempt_id=attempt_id,
            student_id=current_user.id,
            content=content,
            claimed_content_type=photo.content_type,
            filename=photo.filename,
        )
    except ValueError as exc:
        detail = str(exc)
        lower = detail.lower()
        if "not found" in lower:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        if "do not own" in lower:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
        if "already been submitted" in lower or "cannot be submitted" in lower or "rejected" in lower:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
        if "unsupported" in lower or "invalid" in lower or "malformed" in lower or "empty" in lower or "exceeds" in lower or "match" in lower:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
        if "not currently active" in lower:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    return IdentityVerificationSubmitResponse.model_validate(
        {
            "attempt_id": record.attempt_id,
            "status": record.status,
            "submitted_at": record.submitted_at,
            "can_start_examination": True,
            "message": "Identity photo submitted and pending manual review.",
        }
    )


@attempts_router.get(
    "/{attempt_id}/identity-verification",
    response_model=IdentityVerificationStatusResponse,
    status_code=status.HTTP_200_OK,
)
def get_identity_verification_status(
    attempt_id: int,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> IdentityVerificationStatusResponse:
    """
    Retrieve identity verification status for the authenticated student's own attempt.
    Never exposes image bytes, filesystem paths, or internal storage locations.
    """
    try:
        data = service.get_identity_verification_status(db, attempt_id, current_user.id)
    except ValueError as exc:
        detail = str(exc)
        lower = detail.lower()
        if "not found" in lower:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        if "do not own" in lower:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    return IdentityVerificationStatusResponse.model_validate(data)


@attempts_router.get(
    "",
    response_model=list[AttemptHistoryItem],
    status_code=status.HTTP_200_OK,
)

def get_student_attempts(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> list[AttemptHistoryItem]:
    """
    Retrieve the authenticated student's examination attempts with
    associated results where available.

    Returns only records belonging to the authenticated student, ordered
    by creation date descending (newest first). Includes attempts of all
    statuses. Includes historical examination titles even if the
    examination is now closed or inactive.

    For unfinished attempts, result fields are null. For finalized
    attempts, persisted Result fields are returned without recalculation.
    """
    history = service.get_student_attempts_history(db, current_user.id)
    return [AttemptHistoryItem.model_validate(item) for item in history]
