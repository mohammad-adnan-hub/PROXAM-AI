from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func

from app.dependencies import get_db, require_teacher_or_admin
from app.models.attempt import Attempt, AttemptStatus
from app.models.proctoring_event import ProctoringEvent
from app.models.result import Result
from app.models.test import Test
from app.models.user import User, UserRole
from app.modules.students import service as students_service
from app.modules.students.schemas import (
    TeacherAttemptListItem,
    TeacherAttemptDetail,
    TeacherAttemptResult,
)

router = APIRouter(prefix="/teacher", tags=["teacher-attempts"])


def _verify_test_owner(db: Session, test_id: int, user: User) -> Test:
    test = db.get(Test, test_id)
    if not test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Examination not found")
    if user.role != UserRole.admin and test.created_by != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    return test


def _verify_attempt_owner(db: Session, attempt_id: int, user: User) -> Attempt:
    attempt = db.get(Attempt, attempt_id)
    if not attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
    test = db.get(Test, attempt.test_id)
    if not test or (user.role != UserRole.admin and test.created_by != user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    return attempt


@router.get("/tests/{test_id}/attempts", response_model=list[TeacherAttemptListItem])
def list_attempts_for_test(
    test_id: int,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
) -> list[TeacherAttemptListItem]:
    _verify_test_owner(db, test_id, current_user)
    attempts = db.exec(select(Attempt).where(Attempt.test_id == test_id)).all()
    out = []
    for a in attempts:
        student = db.get(User, a.student_id)
        event_count = db.exec(
            select(func.count()).where(ProctoringEvent.attempt_id == a.id)
        ).one()
        latest = db.exec(
            select(ProctoringEvent)
            .where(ProctoringEvent.attempt_id == a.id)
            .order_by(ProctoringEvent.timestamp.desc(), ProctoringEvent.id.desc())
        ).first()
        out.append(TeacherAttemptListItem(
            attempt_id=a.id,
            student_id=a.student_id,
            student_name=student.full_name if student else "",
            student_email=student.email if student else "",
            status=a.status,
            warning_count=a.warning_count,
            started_at=a.started_at,
            submitted_at=a.submitted_at,
            identity_verified=a.identity_verified,
            proctoring_event_count=event_count or 0,
            latest_event_timestamp=latest.timestamp if latest else None,
            latest_event_type=latest.event_type.value if latest else None,
            latest_event_severity=latest.severity if latest else None,
        ))
    return out


@router.get("/attempts/{attempt_id}", response_model=TeacherAttemptDetail)
def get_attempt_detail(
    attempt_id: int,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
) -> TeacherAttemptDetail:
    attempt = _verify_attempt_owner(db, attempt_id, current_user)
    test = db.get(Test, attempt.test_id)
    student = db.get(User, attempt.student_id)
    event_count = db.exec(
        select(func.count()).where(ProctoringEvent.attempt_id == attempt.id)
    ).one()
    iv_status = None
    try:
        from app.models.identity_verification import IdentityVerification
    except ImportError:
        IdentityVerification = None
    if IdentityVerification is not None:
        iv = db.exec(
            select(IdentityVerification).where(IdentityVerification.attempt_id == attempt.id)
        ).first()
        if iv:
            iv_status = iv.status.value if hasattr(iv.status, "value") else str(iv.status)
    return TeacherAttemptDetail(
        attempt_id=attempt.id,
        student_id=attempt.student_id,
        student_name=student.full_name if student else "",
        student_email=student.email if student else "",
        test_id=attempt.test_id,
        test_title=test.title if test else "",
        status=attempt.status,
        warning_count=attempt.warning_count,
        started_at=attempt.started_at,
        submitted_at=attempt.submitted_at,
        identity_verified=attempt.identity_verified,
        identity_verification_status=iv_status,
        proctoring_event_count=event_count or 0,
    )


@router.get("/attempts/{attempt_id}/result", response_model=TeacherAttemptResult)
def get_attempt_result_for_teacher(
    attempt_id: int,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
) -> TeacherAttemptResult:
    attempt = _verify_attempt_owner(db, attempt_id, current_user)
    result = db.exec(select(Result).where(Result.attempt_id == attempt_id)).first()
    return TeacherAttemptResult(
        attempt_id=attempt.id,
        status=attempt.status,
        score=result.score if result else None,
        total_marks=result.total_marks if result else None,
        percentage=result.percentage if result else None,
        correct_count=result.correct_count if result else None,
        incorrect_count=result.incorrect_count if result else None,
        unanswered_count=result.unanswered_count if result else None,
        calculated_at=result.calculated_at if result else None,
    )
