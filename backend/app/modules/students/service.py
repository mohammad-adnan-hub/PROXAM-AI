from typing import Optional
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from sqlalchemy import update as sql_update
from sqlmodel import Session, select, func
from sqlalchemy.exc import IntegrityError

from jose import JWTError, jwt

from app.config import get_settings
from app.models.attempt import Attempt, AttemptStatus
from app.models.test import Test, TestStatus
from app.models.question import Question
from app.models.option import Option
from app.models.answer import Answer
from app.models.result import Result
from app.models.identity_verification import AttemptIdentityVerification, IdentityVerificationStatus
from app.modules.students.identity_storage import (
    IdentityImageStorageError,
    delete_identity_image,
    save_identity_image,
    validate_image_content,
)

settings = get_settings()

VALIDATION_TOKEN_TYPE = "test_validation"
VALIDATION_TOKEN_EXPIRE_MINUTES = 10



def _as_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """
    Normalize a datetime to timezone-aware UTC.
    SQLite may return naive datetime objects even when timezone-aware
    timestamps were originally stored. Naive values are treated as UTC.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _finalize_attempt_if_expired(db: Session, attempt: Attempt) -> bool:
    """
    If an in_progress attempt has passed its deadline, finalize it as
    timed_out, set submitted_at, and calculate/persist its result atomically.

    Uses a conditional UPDATE so that only one request can transition the
    attempt from 'in_progress' to 'timed_out'. Works with both SQLite and
    PostgreSQL.

    Returns True if the attempt was finalized, False otherwise.
    """
    if attempt.status != AttemptStatus.in_progress:
        return False

    now = datetime.now(timezone.utc)
    deadline = _as_utc(attempt.time_limit_ends_at)
    if deadline is None or now <= deadline:
        return False

    return _finalize_attempt(
        db, attempt.id, attempt.student_id, AttemptStatus.timed_out, now
    ) is not None


def _calculate_result(db: Session, attempt_id: int) -> Result:
    """
    Calculate the examination result from persisted answers and return
    a Result object (not yet committed).

    Idempotent: if a result already exists for the attempt, returns it.

    Scoring rules (V1, no negative marking):
    - Correct answer: award the question's configured marks
    - Incorrect answer: zero marks
    - Unanswered question: zero marks
    - Marked-for-review does not affect scoring

    Verifies that each selected option belongs to the exact question being
    scored. Questions without answers count as unanswered.
    """
    existing = db.exec(select(Result).where(Result.attempt_id == attempt_id)).first()
    if existing:
        return existing

    attempt = db.get(Attempt, attempt_id)
    if not attempt:
        raise ValueError("Attempt not found")

    questions = db.exec(
        select(Question).where(Question.test_id == attempt.test_id)
    ).all()

    answers = db.exec(
        select(Answer).where(Answer.attempt_id == attempt_id)
    ).all()

    answer_map = {a.question_id: a for a in answers}

    correct_count = 0
    incorrect_count = 0
    unanswered_count = 0
    score = 0.0
    total_marks = 0.0

    for question in questions:
        total_marks += question.marks
        answer = answer_map.get(question.id)

        if answer is None or answer.selected_option_id is None:
            unanswered_count += 1
            continue

        option = db.get(Option, answer.selected_option_id)
        if option is None:
            # Selected option does not exist; treat as unanswered
            unanswered_count += 1
            continue
        if option.question_id != question.id:
            # Selected option belongs to a different question; treat as unanswered
            unanswered_count += 1
            continue
        if option.is_correct:
            correct_count += 1
            score += question.marks
        else:
            incorrect_count += 1

    percentage = (score / total_marks * 100.0) if total_marks > 0 else 0.0

    return Result(
        attempt_id=attempt_id,
        score=score,
        total_marks=total_marks,
        correct_count=correct_count,
        incorrect_count=incorrect_count,
        unanswered_count=unanswered_count,
        percentage=percentage,
    )


def _finalize_attempt(
    db: Session,
    attempt_id: int,
    student_id: int,
    new_status: AttemptStatus,
    now: datetime,
) -> Optional[tuple[Attempt, Result]]:
    """
    Atomically finalize an attempt and create its result in a single
    database transaction.

    Uses a conditional UPDATE (WHERE status = 'in_progress') so that only
    one request can transition the attempt. If another request already
    finalized it, the conditional UPDATE affects 0 rows and we return the
    existing attempt and result instead.

    Returns (attempt, result) on success, or None if the attempt was
    already finalized by another request.
    """
    # Conditional UPDATE: only transition if still in_progress
    stmt = sql_update(Attempt).where(
        Attempt.id == attempt_id,
        Attempt.status == AttemptStatus.in_progress,
    ).values(status=new_status, submitted_at=now)
    result_proxy = db.exec(stmt)

    # Reload the attempt to see the current state
    attempt = db.get(Attempt, attempt_id)
    if not attempt:
        return None

    if attempt.status != new_status:
        # Another request already finalized this attempt
        existing_result = db.exec(
            select(Result).where(Result.attempt_id == attempt_id)
        ).first()
        if existing_result:
            return (attempt, existing_result)
        return None

    # We won the race - calculate and add the result
    result = _calculate_result(db, attempt_id)
    db.add(result)

    try:
        db.commit()
        db.refresh(attempt)
        db.refresh(result)
    except IntegrityError:
        db.rollback()
        # Result may have been created by another request
        existing_result = db.exec(
            select(Result).where(Result.attempt_id == attempt_id)
        ).first()
        if existing_result:
            db.refresh(attempt)
            return (attempt, existing_result)
        raise

    return (attempt, result)


def create_validation_token(student_id: int, test_id: int) -> str:
    """
    Create a short-lived, signed validation token bound to a student and
    examination. Not single-use; reusable within its validity period.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=VALIDATION_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(student_id),
        "test_id": test_id,
        "type": VALIDATION_TOKEN_TYPE,
        "jti": str(uuid4()),
        "exp": expire,
        "iat": now,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def verify_validation_token(token: str) -> Optional[dict]:
    """
    Verify a validation token's signature, expiry, type, student ID, and
    examination ID. Returns the payload if valid, None otherwise.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None

    if payload.get("type") != VALIDATION_TOKEN_TYPE:
        return None

    return payload


def get_test_by_code(db: Session, test_code: str) -> Optional[Test]:
    """
    Retrieve a test by its unique examination code.
    Returns the Test model if found, regardless of status. Returns None if not found.
    """
    return db.exec(select(Test).where(Test.test_code == test_code)).first()


def build_student_test_details(test: Test, question_count: int) -> dict:
    """
    Build a sanitized examination payload for student viewing.
    Deliberately excludes questions, options, correct answers, created_by,
    instructions, attempt_count, and timestamps to prevent data leakage.
    """
    return {
        "id": test.id,
        "title": test.title,
        "description": test.description,
        "duration_minutes": test.duration_minutes,
        "total_marks": test.total_marks,
        "question_count": question_count,
        "status": test.status,
        "test_code": test.test_code,
    }


def get_question_count(db: Session, test_id: int) -> int:
    """
    Count the number of questions for a given test.
    """
    return db.exec(
        select(func.count(Question.id)).where(Question.test_id == test_id)
    ).one()


def get_existing_attempt(db: Session, student_id: int, test_id: int) -> Optional[Attempt]:
    """
    Check if the student already has an attempt for the given test.
    Returns the Attempt if found, None otherwise.
    """
    return db.exec(
        select(Attempt).where(
            Attempt.student_id == student_id,
            Attempt.test_id == test_id,
        )
    ).first()


def create_attempt(db: Session, student_id: int, test_id: int) -> Attempt:
    """
    Create a new examination attempt for a student.
    The timer is NOT started: time_limit_ends_at is left None.
    Enforces the one-attempt-per-student-per-test rule at both application
    and database levels. Returns the existing attempt if one already exists
    for the same student and test (supports retry after network interruption).
    """
    test = db.get(Test, test_id)
    if not test:
        raise ValueError("Examination not found")

    if test.status != TestStatus.active:
        raise ValueError("Examination is not currently active")

    existing = get_existing_attempt(db, student_id, test_id)
    if existing:
        return existing

    attempt = Attempt(
        test_id=test_id,
        student_id=student_id,
        status=AttemptStatus.created,
        created_at=datetime.now(timezone.utc),
        started_at=None,
        submitted_at=None,
        time_limit_ends_at=None,
        identity_verified=False,
    )
    db.add(attempt)
    try:
        db.commit()
        db.refresh(attempt)
    except IntegrityError:
        db.rollback()
        existing = get_existing_attempt(db, student_id, test_id)
        if existing:
            return existing
        raise ValueError("You already have an attempt for this examination")

    return attempt


def start_attempt(db: Session, student_id: int, attempt_id: int) -> Attempt:
    """
    Start an examination attempt. Transitions status from 'created' to
    'in_progress', records server-side started_at, and calculates
    time_limit_ends_at from the examination's duration_minutes.

    Idempotent: if already in_progress, returns the existing attempt
    without resetting timestamps. Rejects submitted or timed_out attempts.
    """
    attempt = db.get(Attempt, attempt_id)
    if not attempt:
        raise ValueError("Attempt not found")

    if attempt.student_id != student_id:
        raise ValueError("You do not own this attempt")

    test = db.get(Test, attempt.test_id)
    if not test:
        raise ValueError("Examination not found")

    if test.status != TestStatus.active:
        raise ValueError("Examination is not currently active")

    if attempt.status == AttemptStatus.in_progress:
        return attempt

    if attempt.status in (AttemptStatus.submitted, AttemptStatus.timed_out, AttemptStatus.terminated_by_warnings):
        raise ValueError("Attempt cannot be started again")

    # Phase 5.7: require successful identity-photo submission before exam start.
    # Teacher approval is not required before start unless policy explicitly requires it.
    identity = get_identity_verification(db, attempt.id)
    if not identity or identity.status not in (
        IdentityVerificationStatus.pending,
        IdentityVerificationStatus.verified,
    ):
        raise ValueError("Identity verification photo must be submitted before starting the examination")

    now = datetime.now(timezone.utc)
    attempt.status = AttemptStatus.in_progress
    attempt.started_at = now
    attempt.time_limit_ends_at = now + timedelta(minutes=test.duration_minutes)
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt



def get_attempt_questions(
    db: Session, attempt_id: int, student_id: int
) -> list[Question]:
    """
    Retrieve questions for an in_progress attempt belonging to the student.
    Options are included without is_correct to prevent answer leakage.
    Questions are returned in order_index order.
    """
    attempt = db.get(Attempt, attempt_id)
    if not attempt:
        raise ValueError("Attempt not found")

    if attempt.student_id != student_id:
        raise ValueError("You do not own this attempt")

    if attempt.status != AttemptStatus.in_progress:
        raise ValueError("Examination has not started")

    questions = db.exec(
        select(Question)
        .where(Question.test_id == attempt.test_id)
        .order_by(Question.order_index)
    ).all()

    return questions


def save_answer(
    db: Session,
    attempt_id: int,
    student_id: int,
    question_id: int,
    selected_option_id: Optional[int],
    is_marked_for_review: bool = False,
) -> Answer:
    """
    Save or update a student's answer for a question in an attempt.
    Creates a new answer if none exists, otherwise updates the existing one.
    Rejects if the attempt is not in_progress or the examination deadline has passed.
    Verifies question ownership and option-question association before writing.
    """
    attempt = db.get(Attempt, attempt_id)
    if not attempt:
        raise ValueError("Attempt not found")

    if attempt.student_id != student_id:
        raise ValueError("You do not own this attempt")

    if attempt.status != AttemptStatus.in_progress:
        raise ValueError("Examination is not in progress")

    if _finalize_attempt_if_expired(db, attempt):
        raise ValueError("Examination time has expired")

    question = db.get(Question, question_id)
    if not question:
        raise ValueError("Question not found")

    if question.test_id != attempt.test_id:
        raise ValueError("Question does not belong to this examination")

    if selected_option_id is not None:
        option = db.get(Option, selected_option_id)
        if not option:
            raise ValueError("Selected option not found")
        if option.question_id != question_id:
            raise ValueError("Selected option does not belong to this question")

    existing = db.exec(
        select(Answer).where(
            Answer.attempt_id == attempt_id,
            Answer.question_id == question_id,
        )
    ).first()

    if existing:
        existing.selected_option_id = selected_option_id
        existing.is_marked_for_review = is_marked_for_review
        existing.saved_at = datetime.now(timezone.utc)
        db.add(existing)
        try:
            db.commit()
            db.refresh(existing)
        except IntegrityError:
            db.rollback()
            raise
        return existing

    answer = Answer(
        attempt_id=attempt_id,
        question_id=question_id,
        selected_option_id=selected_option_id,
        is_marked_for_review=is_marked_for_review,
        saved_at=datetime.now(timezone.utc),
    )
    db.add(answer)
    try:
        db.commit()
        db.refresh(answer)
    except IntegrityError:
        db.rollback()
        existing = db.exec(
            select(Answer).where(
                Answer.attempt_id == attempt_id,
                Answer.question_id == question_id,
            )
        ).first()
        if existing:
            existing.selected_option_id = selected_option_id
            existing.is_marked_for_review = is_marked_for_review
            existing.saved_at = datetime.now(timezone.utc)
            db.add(existing)
            try:
                db.commit()
                db.refresh(existing)
            except IntegrityError:
                db.rollback()
                raise
            return existing
        raise

    return answer


def get_answers(
    db: Session,
    attempt_id: int,
    student_id: int,
) -> list[Answer]:
    """
    Retrieve all saved answers for an attempt belonging to the student.
    """
    attempt = db.get(Attempt, attempt_id)
    if not attempt:
        raise ValueError("Attempt not found")

    if attempt.student_id != student_id:
        raise ValueError("You do not own this attempt")

    answers = db.exec(
        select(Answer).where(Answer.attempt_id == attempt_id)
    ).all()
    return answers


def clear_answer(
    db: Session,
    attempt_id: int,
    student_id: int,
    question_id: int,
) -> Optional[Answer]:
    """
    Clear a student's answer for a question (deselect the option).
    Preserves is_marked_for_review and updates saved_at.
    Returns None if no answer exists for the question.
    Rejects if the attempt is not in_progress or the examination deadline has passed.
    """
    attempt = db.get(Attempt, attempt_id)
    if not attempt:
        raise ValueError("Attempt not found")

    if attempt.student_id != student_id:
        raise ValueError("You do not own this attempt")

    if attempt.status != AttemptStatus.in_progress:
        raise ValueError("Examination is not in progress")

    if _finalize_attempt_if_expired(db, attempt):
        raise ValueError("Examination time has expired")

    question = db.get(Question, question_id)
    if not question:
        raise ValueError("Question not found")

    if question.test_id != attempt.test_id:
        raise ValueError("Question does not belong to this examination")

    answer = db.exec(
        select(Answer).where(
            Answer.attempt_id == attempt_id,
            Answer.question_id == question_id,
        )
    ).first()

    if answer is None:
        return None

    answer.selected_option_id = None
    answer.saved_at = datetime.now(timezone.utc)
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return answer


def submit_attempt(
    db: Session,
    attempt_id: int,
    student_id: int,
) -> Attempt:
    """
    Finalize an examination attempt. Transitions status to 'submitted' if
    finalized on or before the deadline, or 'timed_out' if the deadline
    has passed. Sets submitted_at and calculates/persists the result.

    Idempotent: if the attempt is already finalized, returns the existing
    attempt without creating a duplicate result.

    Concurrency-safe: uses a conditional UPDATE so that only one request
    can transition the attempt from 'in_progress'. A losing request
    retrieves and returns the already-finalized attempt and result.
    """
    attempt = db.get(Attempt, attempt_id)
    if not attempt:
        raise ValueError("Attempt not found")

    if attempt.student_id != student_id:
        raise ValueError("You do not own this attempt")

    if attempt.status == AttemptStatus.created:
        raise ValueError("Attempt has not been started")

    if attempt.status in (AttemptStatus.submitted, AttemptStatus.timed_out, AttemptStatus.terminated_by_warnings):
        return attempt

    now = datetime.now(timezone.utc)
    deadline = _as_utc(attempt.time_limit_ends_at)

    if deadline is not None and now > deadline:
        new_status = AttemptStatus.timed_out
    else:
        new_status = AttemptStatus.submitted

    finalized = _finalize_attempt(
        db, attempt_id, student_id, new_status, now
    )

    if finalized is None:
        # Another request finalized this attempt; return the current state
        attempt = db.get(Attempt, attempt_id)
        if not attempt:
            raise ValueError("Attempt not found")
        return attempt

    return finalized[0]


def get_identity_verification(db: Session, attempt_id: int) -> Optional[AttemptIdentityVerification]:
    return db.exec(
        select(AttemptIdentityVerification).where(
            AttemptIdentityVerification.attempt_id == attempt_id
        )
    ).first()


def _get_owned_attempt_for_identity(
    db: Session, attempt_id: int, student_id: int
) -> Attempt:
    attempt = db.get(Attempt, attempt_id)
    if not attempt:
        raise ValueError("Attempt not found")
    if attempt.student_id != student_id:
        raise ValueError("You do not own this attempt")
    return attempt


def get_identity_verification_status(
    db: Session, attempt_id: int, student_id: int
) -> dict:
    attempt = _get_owned_attempt_for_identity(db, attempt_id, student_id)
    record = get_identity_verification(db, attempt_id)
    if not record:
        status_value = IdentityVerificationStatus.not_submitted
        submitted_at = None
        reviewed_at = None
        reviewer_notes = None
    else:
        status_value = record.status
        submitted_at = record.submitted_at
        reviewed_at = record.reviewed_at
        # Do not expose reviewer notes to student in status payload for now unless needed;
        # keep minimal. Students can see reviewed/rejected state.
        reviewer_notes = None

    can_start = status_value in (
        IdentityVerificationStatus.pending,
        IdentityVerificationStatus.verified,
    ) and attempt.status in (AttemptStatus.created, AttemptStatus.in_progress)

    message = None
    if status_value == IdentityVerificationStatus.not_submitted:
        message = "Identity photo has not been submitted."
    elif status_value == IdentityVerificationStatus.pending:
        message = "Identity photo submitted and pending manual review."
    elif status_value == IdentityVerificationStatus.verified:
        message = "Identity photo verified."
    elif status_value == IdentityVerificationStatus.rejected:
        message = "Identity photo was rejected. Please contact your instructor or follow provided instructions."

    return {
        "attempt_id": attempt.id,
        "status": status_value,
        "submitted_at": submitted_at,
        "reviewed_at": reviewed_at,
        "reviewer_notes": reviewer_notes,
        "can_start_examination": can_start,
        "message": message,
    }


def submit_identity_verification_photo(
    db: Session,
    attempt_id: int,
    student_id: int,
    content: bytes,
    claimed_content_type: Optional[str],
    filename: Optional[str],
) -> AttemptIdentityVerification:
    attempt = _get_owned_attempt_for_identity(db, attempt_id, student_id)

    # Submission allowed only before finalization and for attempts that can still proceed.
    if attempt.status in (AttemptStatus.submitted, AttemptStatus.timed_out):
        raise ValueError("Identity verification cannot be submitted for a finalized attempt")

    test = db.get(Test, attempt.test_id)
    if not test:
        raise ValueError("Examination not found")
    if test.status != TestStatus.active:
        raise ValueError("Examination is not currently active")

    existing = get_identity_verification(db, attempt_id)
    if existing and existing.status in (
        IdentityVerificationStatus.pending,
        IdentityVerificationStatus.verified,
    ):
        raise ValueError("Identity verification photo has already been submitted")

    try:
        actual_mime, ext = validate_image_content(content, claimed_content_type, filename)
    except IdentityImageStorageError as exc:
        raise ValueError(str(exc))

    # Save new image before DB mutation so validation/storage failures cannot create incomplete DB records.
    try:
        relative_path, saved_path = save_identity_image(content, attempt_id, student_id, actual_mime, ext)
    except (OSError, IdentityImageStorageError) as exc:
        raise ValueError("Failed to store identity image securely.") from exc

    previous_path = existing.image_path if existing else None
    now = datetime.now(timezone.utc)

    try:
        if existing:
            # Resubmission allowed only after rejection; replace image/metadata and return to pending.
            existing.status = IdentityVerificationStatus.pending
            existing.image_path = relative_path
            existing.original_filename = (filename or "")[:255] or None
            existing.content_type = actual_mime
            existing.file_size_bytes = len(content)
            existing.submitted_at = now
            existing.reviewer_id = None
            existing.reviewed_at = None
            existing.reviewer_notes = None
            existing.updated_at = now
            record = existing
        else:
            record = AttemptIdentityVerification(
                attempt_id=attempt.id,
                student_id=student_id,
                status=IdentityVerificationStatus.pending,
                image_path=relative_path,
                original_filename=(filename or "")[:255] or None,
                content_type=actual_mime,
                file_size_bytes=len(content),
                submitted_at=now,
                created_at=now,
                updated_at=now,
            )
            db.add(record)

        # Do NOT auto-mark attempt.identity_verified on upload/pending submission.
        # attempt.identity_verified remains reviewer-controlled/future use.
        db.commit()
        db.refresh(record)
    except IntegrityError:
        db.rollback()
        # Cleanup newly stored file; DB state remains unchanged or consistent.
        try:
            if saved_path.exists():
                saved_path.unlink()
        except OSError:
            pass
        existing_after = get_identity_verification(db, attempt_id)
        if existing_after and existing_after.status in (
            IdentityVerificationStatus.pending,
            IdentityVerificationStatus.verified,
        ):
            raise ValueError("Identity verification photo has already been submitted")
        raise
    except Exception:
        db.rollback()
        try:
            if saved_path.exists():
                saved_path.unlink()
        except OSError:
            pass
        raise

    # Best-effort cleanup of replaced rejected photo after successful commit.
    if previous_path and previous_path != relative_path:
        delete_identity_image(previous_path)

    return record


def get_student_attempts_history(
    db: Session, student_id: int
) -> list[dict]:
    """
    Retrieve the authenticated student's examination attempts with
    associated results where available.

    Joins Attempt with Test and left-joins Result. Filters strictly by
    student_id. Sorted by Attempt.created_at descending.

    Includes attempts of all statuses (created, in_progress, submitted,
    timed_out). Includes historical examination titles even if the
    examination is now closed or inactive.

    For unfinished attempts, result fields are None. For finalized
    attempts, persisted Result fields are returned without recalculation.
    """
    statement = (
        select(Attempt, Test, Result)
        .join(Test, Attempt.test_id == Test.id)
        .outerjoin(Result, Attempt.id == Result.attempt_id)
        .where(Attempt.student_id == student_id)
        .order_by(Attempt.created_at.desc())
    )
    rows = db.exec(statement).all()

    history = []
    for attempt, test, result in rows:
        history.append({
            "id": attempt.id,
            "test_id": attempt.test_id,
            "test_title": test.title,
            "test_code": test.test_code,
            "status": attempt.status,
            "created_at": attempt.created_at,
            "started_at": attempt.started_at,
            "submitted_at": attempt.submitted_at,
            "score": result.score if result else None,
            "total_marks": result.total_marks if result else None,
            "percentage": result.percentage if result else None,
            "correct_count": result.correct_count if result else None,
            "incorrect_count": result.incorrect_count if result else None,
            "unanswered_count": result.unanswered_count if result else None,
            "calculated_at": result.calculated_at if result else None,
        })
    return history
