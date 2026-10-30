import secrets
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Session, select, func

from app.models.test import Test, TestStatus
from app.models.question import Question
from app.models.option import Option
from app.models.attempt import Attempt
from app.modules.tests.schemas import TestCreateRequest, TestUpdateRequest

# Characters allowed for test codes (excludes confusing glyphs: 0, O, 1, I)
CODE_CHARS = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"


def generate_unique_test_code(db: Session) -> str:
    """
    Generate a 10-character code matching pattern PXAM-XXXXX.
    Uses cryptographically secure random choice with collision detection.
    """
    for _ in range(50):
        random_suffix = "".join(secrets.choice(CODE_CHARS) for _ in range(5))
        code = f"PXAM-{random_suffix}"
        existing = db.exec(select(Test.id).where(Test.test_code == code)).first()
        if not existing:
            return code
    raise RuntimeError("Failed to generate a unique test code after multiple attempts.")


def create_test(db: Session, teacher_id: int, payload: TestCreateRequest) -> dict:
    """
    Persist examination, questions, and options within a single database transaction.
    Automatically assigns an active status and unique test code.
    """
    test_code = generate_unique_test_code(db)
    total_marks = sum(q.marks for q in payload.questions)

    now = datetime.now(timezone.utc)
    test = Test(
        title=payload.title,
        description=payload.description,
        instructions=payload.instructions,
        duration_minutes=payload.duration_minutes,
        total_marks=total_marks,
        status=TestStatus.active,
        test_code=test_code,
        created_by=teacher_id,
        created_at=now,
        updated_at=now,
    )
    db.add(test)
    db.flush()  # Populates test.id for foreign keys

    created_questions = []
    for q_idx, q_data in enumerate(payload.questions):
        question = Question(
            test_id=test.id,
            question_text=q_data.question_text,
            marks=q_data.marks,
            order_index=q_data.order_index if q_data.order_index is not None else q_idx,
        )
        db.add(question)
        db.flush()  # Populates question.id for option foreign keys

        created_options = []
        for opt_data in q_data.options:
            option = Option(
                question_id=question.id,
                label=opt_data.label,
                option_text=opt_data.option_text,
                is_correct=opt_data.is_correct,
            )
            db.add(option)
            created_options.append(option)

        created_questions.append((question, created_options))

    db.commit()
    db.refresh(test)

    return build_test_detail_dict(test, created_questions, attempt_count=0)


def get_teacher_tests(db: Session, teacher_id: int) -> list[dict]:
    """
    Retrieve all tests created by the specified teacher with question & attempt counts.
    """
    tests = db.exec(
        select(Test).where(Test.created_by == teacher_id).order_by(Test.created_at.desc())
    ).all()

    results = []
    for test in tests:
        q_count = db.exec(
            select(func.count(Question.id)).where(Question.test_id == test.id)
        ).one()
        a_count = db.exec(
            select(func.count(Attempt.id)).where(Attempt.test_id == test.id)
        ).one()

        results.append({
            "id": test.id,
            "title": test.title,
            "description": test.description,
            "duration_minutes": test.duration_minutes,
            "total_marks": test.total_marks,
            "status": test.status,
            "test_code": test.test_code,
            "created_at": test.created_at,
            "updated_at": test.updated_at,
            "question_count": q_count,
            "attempt_count": a_count,
        })

    return results


def get_test_by_id_for_teacher(db: Session, test_id: int, teacher_id: int) -> Optional[dict]:
    """
    Retrieve single test with complete question/option payload for the owning teacher.
    Returns None if test not found or if the teacher is not the owner.
    """
    test = db.get(Test, test_id)
    if not test or test.created_by != teacher_id:
        return None

    questions = db.exec(
        select(Question).where(Question.test_id == test.id).order_by(Question.order_index.asc())
    ).all()

    question_list = []
    for q in questions:
        options = db.exec(
            select(Option).where(Option.question_id == q.id).order_by(Option.label.asc())
        ).all()
        question_list.append((q, options))

    attempt_count = db.exec(
        select(func.count(Attempt.id)).where(Attempt.test_id == test.id)
    ).one()

    return build_test_detail_dict(test, question_list, attempt_count)


def update_test(db: Session, test_id: int, teacher_id: int, payload: TestUpdateRequest) -> dict:
    """
    Update test parameters. If attempts already exist, question modification is forbidden.
    """
    test = db.get(Test, test_id)
    if not test:
        raise ValueError("Examination not found")
    if test.created_by != teacher_id:
        raise PermissionError("You do not have permission to modify this examination")

    attempt_count = db.exec(
        select(func.count(Attempt.id)).where(Attempt.test_id == test.id)
    ).one()

    if payload.questions is not None and attempt_count > 0:
        raise ValueError("Cannot modify questions on an examination that already has candidate attempts.")

    # Update metadata fields
    if payload.title is not None:
        test.title = payload.title
    if payload.description is not None:
        test.description = payload.description
    if payload.instructions is not None:
        test.instructions = payload.instructions
    if payload.duration_minutes is not None:
        test.duration_minutes = payload.duration_minutes

    test.updated_at = datetime.now(timezone.utc)

    # If updating questions and no attempts exist, replace question set
    if payload.questions is not None and attempt_count == 0:
        # Delete existing options & questions
        existing_questions = db.exec(select(Question).where(Question.test_id == test.id)).all()
        for eq in existing_questions:
            existing_options = db.exec(select(Option).where(Option.question_id == eq.id)).all()
            for eo in existing_options:
                db.delete(eo)
            db.delete(eq)
        db.flush()

        # Add new questions & options
        total_marks = sum(q.marks for q in payload.questions)
        test.total_marks = total_marks

        for q_idx, q_data in enumerate(payload.questions):
            question = Question(
                test_id=test.id,
                question_text=q_data.question_text,
                marks=q_data.marks,
                order_index=q_data.order_index if q_data.order_index is not None else q_idx,
            )
            db.add(question)
            db.flush()

            for opt_data in q_data.options:
                option = Option(
                    question_id=question.id,
                    label=opt_data.label,
                    option_text=opt_data.option_text,
                    is_correct=opt_data.is_correct,
                )
                db.add(option)

    db.commit()
    db.refresh(test)

    return get_test_by_id_for_teacher(db, test_id, teacher_id)


def delete_test(db: Session, test_id: int, teacher_id: int) -> bool:
    """
    Safely delete test and its associated questions/options.
    Fails if any candidate attempts exist.
    """
    test = db.get(Test, test_id)
    if not test:
        raise ValueError("Examination not found")
    if test.created_by != teacher_id:
        raise PermissionError("You do not have permission to delete this examination")

    attempt_count = db.exec(
        select(func.count(Attempt.id)).where(Attempt.test_id == test.id)
    ).one()
    if attempt_count > 0:
        raise ValueError("Cannot delete an examination with existing candidate attempts.")

    # Cascading delete of options and questions
    questions = db.exec(select(Question).where(Question.test_id == test.id)).all()
    for q in questions:
        options = db.exec(select(Option).where(Option.question_id == q.id)).all()
        for opt in options:
            db.delete(opt)
        db.delete(q)

    db.delete(test)
    db.commit()
    return True


def get_teacher_stats(db: Session, teacher_id: int) -> dict:
    """
    Aggregate statistics for the teacher dashboard.
    """
    all_tests = get_teacher_tests(db, teacher_id)
    total_tests = len(all_tests)
    total_attempts = sum(t["attempt_count"] for t in all_tests)
    active_tests = sum(1 for t in all_tests if t["status"] == TestStatus.active)
    recent_tests = all_tests[:5]

    return {
        "total_tests": total_tests,
        "total_attempts": total_attempts,
        "active_tests": active_tests,
        "recent_tests": recent_tests,
    }


def build_test_detail_dict(test: Test, questions_with_options: list, attempt_count: int) -> dict:
    formatted_questions = []
    for q, options in questions_with_options:
        formatted_questions.append({
            "id": q.id,
            "question_text": q.question_text,
            "marks": q.marks,
            "order_index": q.order_index,
            "options": [
                {
                    "id": opt.id,
                    "label": opt.label,
                    "option_text": opt.option_text,
                    "is_correct": opt.is_correct,
                }
                for opt in options
            ],
        })

    return {
        "id": test.id,
        "title": test.title,
        "description": test.description,
        "instructions": test.instructions,
        "duration_minutes": test.duration_minutes,
        "total_marks": test.total_marks,
        "status": test.status,
        "test_code": test.test_code,
        "created_at": test.created_at,
        "updated_at": test.updated_at,
        "created_by": test.created_by,
        "question_count": len(formatted_questions),
        "attempt_count": attempt_count,
        "questions": formatted_questions,
    }
