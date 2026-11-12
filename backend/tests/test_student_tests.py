"""
Integration tests for Student Test Code Validation Module.
Covers valid/invalid codes, inactive examinations, authorization,
and correct-answer data leakage prevention.
"""
import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")

import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.models.user import User, UserRole
from app.models.test import Test, TestStatus
from app.models.question import Question
from app.models.attempt import Attempt, AttemptStatus
from app.models.option import Option
from app.models.result import Result
from app.modules.auth.service import hash_password


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def create_user(session: Session, email: str, role: UserRole) -> User:
    user = User(
        full_name=f"User {email}",
        email=email,
        hashed_password=hash_password("Password123!"),
        role=role,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_active_test(session: Session, title: str, code: str, created_by: int) -> Test:
    test = Test(
        title=title,
        description="Test description",
        duration_minutes=30,
        total_marks=10.0,
        status=TestStatus.active,
        test_code=code,
        created_by=created_by,
    )
    session.add(test)
    session.commit()
    session.refresh(test)
    return test


def create_inactive_test(session: Session, title: str, code: str, created_by: int) -> Test:
    test = Test(
        title=title,
        description="Inactive test",
        duration_minutes=30,
        total_marks=10.0,
        status=TestStatus.closed,
        test_code=code,
        created_by=created_by,
    )
    session.add(test)
    session.commit()
    session.refresh(test)
    return test


def add_questions(session: Session, test_id: int, count: int = 2):
    for i in range(count):
        q = Question(
            test_id=test_id,
            question_text=f"Question {i + 1}?",
            marks=1.0,
            order_index=i,
        )
        session.add(q)
    session.commit()


def add_options(session: Session, question_id: int, correct_label: str = "B"):
    labels = ["A", "B", "C", "D"]
    for label in labels:
        o = Option(
            question_id=question_id,
            option_text=f"Option {label}",
            label=label,
            is_correct=(label == correct_label),
        )
        session.add(o)
    session.commit()


def login_student(client: TestClient, email: str, password: str = "Password123!"):
    client.post("/api/auth/login", json={"email": email, "password": password})


# ---------------------------------------------------------------------------
# Valid Code Validation Tests
# ---------------------------------------------------------------------------

def test_validate_valid_test_code_returns_sanitized_details(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    add_questions(session, test.id, 3)

    login_student(client, "student1@test.edu")

    resp = client.post(
        "/api/student/tests/validate-code",
        json={"test_code": "PXAM-ABCDE"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == test.id
    assert data["title"] == "Midterm Exam"
    assert data["description"] == "Test description"
    assert data["duration_minutes"] == 30
    assert data["total_marks"] == 10.0
    assert data["question_count"] == 3
    assert data["status"] == "active"
    assert data["test_code"] == "PXAM-ABCDE"


def test_validate_test_code_case_insensitive(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    create_active_test(session, "Exam", "PXAM-ABCDE", teacher.id)

    login_student(client, "student1@test.edu")

    resp = client.post(
        "/api/student/tests/validate-code",
        json={"test_code": "pxam-abcde"},
    )
    assert resp.status_code == 200
    assert resp.json()["test_code"] == "PXAM-ABCDE"


# ---------------------------------------------------------------------------
# Invalid Code Tests
# ---------------------------------------------------------------------------

def test_validate_invalid_test_code_returns_404(client: TestClient, session: Session):
    student = create_user(session, "student1@test.edu", UserRole.student)
    login_student(client, "student1@test.edu")

    resp = client.post(
        "/api/student/tests/validate-code",
        json={"test_code": "PXAM-NONEXIST"},
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Invalid test code"


def test_validate_empty_test_code_rejected(client: TestClient, session: Session):
    student = create_user(session, "student1@test.edu", UserRole.student)
    login_student(client, "student1@test.edu")

    resp = client.post(
        "/api/student/tests/validate-code",
        json={"test_code": "   "},
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Inactive Examination Tests
# ---------------------------------------------------------------------------

def test_validate_inactive_test_code_returns_403(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    create_inactive_test(session, "Closed Exam", "PXAM-CLOSED", teacher.id)

    login_student(client, "student1@test.edu")

    resp = client.post(
        "/api/student/tests/validate-code",
        json={"test_code": "PXAM-CLOSED"},
    )
    assert resp.status_code == 403
    assert "active" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Authorization Tests
# ---------------------------------------------------------------------------

def test_validate_test_code_unauthenticated_returns_401(client: TestClient):
    resp = client.post(
        "/api/student/tests/validate-code",
        json={"test_code": "PXAM-ABCDE"},
    )
    assert resp.status_code == 401


def test_validate_test_code_teacher_forbidden_403(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    create_active_test(session, "Exam", "PXAM-ABCDE", teacher.id)

    # Login as teacher
    client.post("/api/auth/login", json={"email": "teacher1@test.edu", "password": "Password123!"})

    resp = client.post(
        "/api/student/tests/validate-code",
        json={"test_code": "PXAM-ABCDE"},
    )
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Insufficient permissions"


def test_get_student_test_details_unauthenticated_returns_401(client: TestClient):
    resp = client.get("/api/student/tests/1")
    assert resp.status_code == 401


def test_get_student_test_details_teacher_forbidden_403(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    create_active_test(session, "Exam", "PXAM-ABCDE", teacher.id)

    client.post("/api/auth/login", json={"email": "teacher1@test.edu", "password": "Password123!"})

    resp = client.get("/api/student/tests/1")
    assert resp.status_code == 403


def test_get_student_test_details_no_token_returns_401(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Exam", "PXAM-ABCDE", teacher.id)

    login_student(client, "student1@test.edu")

    # No token, no existing attempt -> 401
    resp = client.get(f"/api/student/tests/{test.id}")
    assert resp.status_code == 401


def test_get_student_test_details_wrong_student_token_returns_401(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student1 = create_user(session, "student1@test.edu", UserRole.student)
    student2 = create_user(session, "student2@test.edu", UserRole.student)
    test = create_active_test(session, "Exam", "PXAM-ABCDE", teacher.id)

    # Login as student1 and get a token
    login_student(client, "student1@test.edu")
    validate_resp = client.post(
        "/api/student/tests/validate-code",
        json={"test_code": "PXAM-ABCDE"},
    )
    assert validate_resp.status_code == 200
    student1_token = validate_resp.json()["validation_token"]

    # Login as student2 and try to use student1's token
    login_student(client, "student2@test.edu")
    resp = client.get(
        f"/api/student/tests/{test.id}",
        headers={"X-Validation-Token": student1_token},
    )
    assert resp.status_code == 401


def test_get_student_test_details_invalid_token_returns_401(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Exam", "PXAM-ABCDE", teacher.id)

    login_student(client, "student1@test.edu")

    resp = client.get(
        f"/api/student/tests/{test.id}",
        headers={"X-Validation-Token": "not-a-valid-token"},
    )
    assert resp.status_code == 401


def test_get_student_test_details_existing_attempt_without_token(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Exam", "PXAM-ABCDE", teacher.id)

    login_student(client, "student1@test.edu")

    # Create an attempt first
    attempt_resp = client.post(f"/api/student/tests/{test.id}/attempt")
    assert attempt_resp.status_code == 201

    # Now GET without token should succeed via existing attempt
    resp = client.get(f"/api/student/tests/{test.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == test.id


def test_get_student_test_details_another_students_attempt_never_authorizes(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student1 = create_user(session, "student1@test.edu", UserRole.student)
    student2 = create_user(session, "student2@test.edu", UserRole.student)
    test = create_active_test(session, "Exam", "PXAM-ABCDE", teacher.id)

    # Student1 creates an attempt
    login_student(client, "student1@test.edu")
    client.post(f"/api/student/tests/{test.id}/attempt")

    # Student2 tries to access using their own session (no token, no attempt)
    login_student(client, "student2@test.edu")
    resp = client.get(f"/api/student/tests/{test.id}")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Data Leakage Prevention Tests
# ---------------------------------------------------------------------------

def test_validate_test_code_excludes_questions_and_options(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    add_questions(session, test.id, 2)

    login_student(client, "student1@test.edu")

    resp = client.post(
        "/api/student/tests/validate-code",
        json={"test_code": "PXAM-ABCDE"},
    )
    assert resp.status_code == 200
    data = resp.json()

    # Must NOT contain questions, options, or correct answers
    assert "questions" not in data
    assert "options" not in data

    # Must NOT contain teacher-sensitive fields
    assert "created_by" not in data
    assert "instructions" not in data
    assert "attempt_count" not in data
    assert "created_at" not in data
    assert "updated_at" not in data

    # Must only contain sanitized fields
    expected_keys = {
        "id", "title", "description", "duration_minutes",
        "total_marks", "question_count", "status", "test_code",
        "validation_token",
    }
    assert set(data.keys()) == expected_keys
    assert isinstance(data["validation_token"], str)
    assert len(data["validation_token"]) > 0


def test_get_student_test_details_excludes_correct_answers(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    add_questions(session, test.id, 2)

    login_student(client, "student1@test.edu")

    # Obtain a validation token first
    validate_resp = client.post(
        "/api/student/tests/validate-code",
        json={"test_code": "PXAM-ABCDE"},
    )
    assert validate_resp.status_code == 200
    token = validate_resp.json()["validation_token"]
    assert isinstance(token, str) and len(token) > 0

    resp = client.get(
        f"/api/student/tests/{test.id}",
        headers={"X-Validation-Token": token},
    )
    assert resp.status_code == 200
    data = resp.json()

    assert "questions" not in data
    assert "created_by" not in data
    assert "instructions" not in data
    expected_keys = {
        "id", "title", "description", "duration_minutes",
        "total_marks", "question_count", "status", "test_code",
    }
    assert set(data.keys()) == expected_keys


# ---------------------------------------------------------------------------
# Attempt Creation Tests
# ---------------------------------------------------------------------------

def test_student_create_attempt_success(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)

    login_student(client, "student1@test.edu")

    resp = client.post(f"/api/student/tests/{test.id}/attempt")
    assert resp.status_code == 201
    data = resp.json()
    assert data["test_id"] == test.id
    assert data["student_id"] == student.id
    assert data["status"] == "created"
    assert data["started_at"] is None
    assert data["submitted_at"] is None
    assert data["time_limit_ends_at"] is None  # Timer NOT started
    assert data["created_at"] is not None  # Record creation timestamp populated
    assert data["identity_verified"] is False
    assert "id" in data


def test_create_attempt_unauthenticated_401(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)

    resp = client.post(f"/api/student/tests/{test.id}/attempt")
    assert resp.status_code == 401


def test_create_attempt_teacher_forbidden_403(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)

    client.post("/api/auth/login", json={"email": "teacher1@test.edu", "password": "Password123!"})

    resp = client.post(f"/api/student/tests/{test.id}/attempt")
    assert resp.status_code == 403


def test_create_attempt_invalid_test_id_404(client: TestClient, session: Session):
    student = create_user(session, "student1@test.edu", UserRole.student)

    login_student(client, "student1@test.edu")

    resp = client.post("/api/student/tests/99999/attempt")
    assert resp.status_code == 404


def test_create_attempt_inactive_test_403(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    create_inactive_test(session, "Closed Exam", "PXAM-CLOSED", teacher.id)

    login_student(client, "student1@test.edu")

    # Get the inactive test's id
    test = session.exec(
        select(Test).where(Test.test_code == "PXAM-CLOSED")
    ).first()

    resp = client.post(f"/api/student/tests/{test.id}/attempt")
    assert resp.status_code == 403


def test_create_attempt_duplicate_returns_existing_attempt(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)

    login_student(client, "student1@test.edu")

    resp1 = client.post(f"/api/student/tests/{test.id}/attempt")
    assert resp1.status_code == 201
    attempt1 = resp1.json()
    assert attempt1["student_id"] == student.id
    assert "id" in attempt1

    # Second request returns the same existing attempt
    resp2 = client.post(f"/api/student/tests/{test.id}/attempt")
    assert resp2.status_code == 201
    attempt2 = resp2.json()
    assert attempt2["id"] == attempt1["id"]
    assert attempt2["student_id"] == student.id
    assert attempt2["test_id"] == test.id


def test_create_attempt_timer_not_started(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)

    login_student(client, "student1@test.edu")

    resp = client.post(f"/api/student/tests/{test.id}/attempt")
    assert resp.status_code == 201
    data = resp.json()
    assert data["time_limit_ends_at"] is None, "Timer must not be started on attempt creation"
    assert data["started_at"] is None, "started_at must be null before exam starts"
    assert data["status"] == "created", "Attempt status must be 'created' before exam starts"
    assert data["created_at"] is not None, "created_at must be populated"


def test_create_attempt_ownership_enforced(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student1 = create_user(session, "student1@test.edu", UserRole.student)
    student2 = create_user(session, "student2@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)

    # Student 1 creates an attempt
    login_student(client, "student1@test.edu")
    resp1 = client.post(f"/api/student/tests/{test.id}/attempt")
    assert resp1.status_code == 201
    assert resp1.json()["student_id"] == student1.id

    # Student 2 creates their own attempt for the same test
    login_student(client, "student2@test.edu")
    resp2 = client.post(f"/api/student/tests/{test.id}/attempt")
    assert resp2.status_code == 201
    assert resp2.json()["student_id"] == student2.id

    # Student 1 cannot create a second attempt — gets their existing attempt back
    login_student(client, "student1@test.edu")
    resp3 = client.post(f"/api/student/tests/{test.id}/attempt")
    assert resp3.status_code == 201
    assert resp3.json()["student_id"] == student1.id
    assert resp3.json()["id"] == resp1.json()["id"]


# ---------------------------------------------------------------------------
# Start Examination Tests
# ---------------------------------------------------------------------------

def test_start_attempt_success(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    add_questions(session, test.id, 2)

    login_student(client, "student1@test.edu")

    # Create attempt first
    create_resp = client.post(f"/api/student/tests/{test.id}/attempt")
    assert create_resp.status_code == 201
    attempt_id = create_resp.json()["id"]

    # Start the attempt
    resp = client.post(f"/api/student/attempts/{attempt_id}/start")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == attempt_id
    assert data["status"] == "in_progress"
    assert data["started_at"] is not None
    assert data["time_limit_ends_at"] is not None
    assert data["student_id"] == student.id


def test_start_attempt_deadline_uses_exam_duration(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Timed Exam", "PXAM-TIMED", teacher.id)
    test.duration_minutes = 45
    session.add(test)
    session.commit()
    add_questions(session, test.id, 1)

    login_student(client, "student1@test.edu")
    create_resp = client.post(f"/api/student/tests/{test.id}/attempt")
    attempt_id = create_resp.json()["id"]

    resp = client.post(f"/api/student/attempts/{attempt_id}/start")
    assert resp.status_code == 200
    data = resp.json()

    started = data["started_at"]
    ends = data["time_limit_ends_at"]
    assert ends is not None
    assert started is not None
    # Deadline should be started_at + 45 minutes
    from datetime import datetime, timezone, timedelta
    started_dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
    ends_dt = datetime.fromisoformat(ends.replace("Z", "+00:00"))
    expected_ends = started_dt + timedelta(minutes=45)
    assert abs((ends_dt - expected_ends).total_seconds()) < 2


def test_start_attempt_repeated_does_not_reset_timestamps(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    add_questions(session, test.id, 1)

    login_student(client, "student1@test.edu")
    create_resp = client.post(f"/api/student/tests/{test.id}/attempt")
    attempt_id = create_resp.json()["id"]

    # First start
    resp1 = client.post(f"/api/student/attempts/{attempt_id}/start")
    assert resp1.status_code == 200
    data1 = resp1.json()
    started_1 = data1["started_at"]
    ends_1 = data1["time_limit_ends_at"]

    # Second start should not reset timestamps
    resp2 = client.post(f"/api/student/attempts/{attempt_id}/start")
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["status"] == "in_progress"
    assert data2["started_at"] == started_1
    assert data2["time_limit_ends_at"] == ends_1


def test_start_attempt_wrong_student_403(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student1 = create_user(session, "student1@test.edu", UserRole.student)
    student2 = create_user(session, "student2@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    add_questions(session, test.id, 1)

    # Student 1 creates and starts attempt
    login_student(client, "student1@test.edu")
    create_resp = client.post(f"/api/student/tests/{test.id}/attempt")
    assert create_resp.status_code == 201
    attempt_id = create_resp.json()["id"]
    client.post(f"/api/student/attempts/{attempt_id}/start")

    # Student 2 tries to start student 1's attempt
    login_student(client, "student2@test.edu")
    resp = client.post(f"/api/student/attempts/{attempt_id}/start")
    assert resp.status_code == 403


def test_start_attempt_missing_attempt_404(client: TestClient, session: Session):
    student = create_user(session, "student1@test.edu", UserRole.student)
    login_student(client, "student1@test.edu")

    resp = client.post("/api/student/tests/99999/start")
    assert resp.status_code == 404


def test_start_attempt_inactive_test_403(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    create_inactive_test(session, "Closed Exam", "PXAM-CLOSED", teacher.id)

    login_student(client, "student1@test.edu")
    test = session.exec(
        select(Test).where(Test.test_code == "PXAM-CLOSED")
    ).first()

    create_resp = client.post(f"/api/student/tests/{test.id}/attempt")
    assert create_resp.status_code == 403


def test_start_attempt_submitted_cannot_restart(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    add_questions(session, test.id, 1)

    login_student(client, "student1@test.edu")
    create_resp = client.post(f"/api/student/tests/{test.id}/attempt")
    attempt_id = create_resp.json()["id"]

    # Start the attempt
    start_resp = client.post(f"/api/student/attempts/{attempt_id}/start")
    assert start_resp.status_code == 200

    # Manually submit the attempt in the DB
    from app.models.attempt import Attempt
    attempt = session.get(Attempt, attempt_id)
    attempt.status = AttemptStatus.submitted
    attempt.submitted_at = datetime.now(timezone.utc)
    session.add(attempt)
    session.commit()

    # Try to start again - should fail
    resp = client.post(f"/api/student/attempts/{attempt_id}/start")
    assert resp.status_code == 409


def test_start_attempt_timed_out_cannot_restart(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    add_questions(session, test.id, 1)

    login_student(client, "student1@test.edu")
    create_resp = client.post(f"/api/student/tests/{test.id}/attempt")
    attempt_id = create_resp.json()["id"]

    # Start the attempt
    client.post(f"/api/student/attempts/{attempt_id}/start")

    # Manually mark as timed_out
    from app.models.attempt import Attempt
    attempt = session.get(Attempt, attempt_id)
    attempt.status = AttemptStatus.timed_out
    session.add(attempt)
    session.commit()

    resp = client.post(f"/api/student/attempts/{attempt_id}/start")
    assert resp.status_code == 409


# ---------------------------------------------------------------------------
# Question Retrieval Tests
# ---------------------------------------------------------------------------

def test_get_attempt_questions_success(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    add_questions(session, test.id, 2)

    # Add options to each question
    from app.models.question import Question as QuestionModel
    questions = session.exec(
        select(QuestionModel).where(QuestionModel.test_id == test.id)
    ).all()
    for q in questions:
        add_options(session, q.id, correct_label="B")

    login_student(client, "student1@test.edu")
    create_resp = client.post(f"/api/student/tests/{test.id}/attempt")
    attempt_id = create_resp.json()["id"]

    # Start the attempt
    client.post(f"/api/student/attempts/{attempt_id}/start")

    resp = client.get(f"/api/student/attempts/{attempt_id}/questions")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["order_index"] == 0
    assert data[1]["order_index"] == 1
    assert "question_text" in data[0]
    assert "marks" in data[0]
    assert "options" in data[0]
    assert len(data[0]["options"]) == 4


def test_get_attempt_questions_excludes_correct_answers(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    add_questions(session, test.id, 1)

    login_student(client, "student1@test.edu")
    create_resp = client.post(f"/api/student/tests/{test.id}/attempt")
    attempt_id = create_resp.json()["id"]

    # Get the question ID to add options
    from app.models.question import Question as QuestionModel
    question = session.exec(
        select(QuestionModel).where(QuestionModel.test_id == test.id)
    ).first()
    add_options(session, question.id, correct_label="B")

    # Start the attempt
    client.post(f"/api/student/attempts/{attempt_id}/start")

    resp = client.get(f"/api/student/attempts/{attempt_id}/questions")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    options = data[0]["options"]
    for opt in options:
        assert "is_correct" not in opt, f"Option {opt['label']} must not expose is_correct"
    # Verify all 4 options present with labels A-D
    labels = sorted([opt["label"] for opt in options])
    assert labels == ["A", "B", "C", "D"]


def test_get_attempt_questions_wrong_student_403(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student1 = create_user(session, "student1@test.edu", UserRole.student)
    student2 = create_user(session, "student2@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    add_questions(session, test.id, 1)

    # Student 1 creates and starts attempt
    login_student(client, "student1@test.edu")
    create_resp = client.post(f"/api/student/tests/{test.id}/attempt")
    attempt_id = create_resp.json()["id"]
    client.post(f"/api/student/attempts/{attempt_id}/start")

    # Student 2 tries to retrieve questions
    login_student(client, "student2@test.edu")
    resp = client.get(f"/api/student/attempts/{attempt_id}/questions")
    assert resp.status_code == 403


def test_get_attempt_questions_before_start_403(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    add_questions(session, test.id, 1)

    login_student(client, "student1@test.edu")
    create_resp = client.post(f"/api/student/tests/{test.id}/attempt")
    attempt_id = create_resp.json()["id"]

    # Attempt is still 'created', not started
    resp = client.get(f"/api/student/attempts/{attempt_id}/questions")
    assert resp.status_code == 403


def test_get_attempt_questions_missing_attempt_404(client: TestClient, session: Session):
    student = create_user(session, "student1@test.edu", UserRole.student)
    login_student(client, "student1@test.edu")

    resp = client.get("/api/student/tests/99999/questions")
    assert resp.status_code == 404


def test_get_attempt_questions_submitted_403(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    add_questions(session, test.id, 1)

    login_student(client, "student1@test.edu")
    create_resp = client.post(f"/api/student/tests/{test.id}/attempt")
    attempt_id = create_resp.json()["id"]

    # Start then manually submit
    client.post(f"/api/student/attempts/{attempt_id}/start")

    from app.models.attempt import Attempt
    attempt = session.get(Attempt, attempt_id)
    attempt.status = AttemptStatus.submitted
    session.add(attempt)
    session.commit()

    resp = client.get(f"/api/student/attempts/{attempt_id}/questions")
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Answer Persistence Tests
# ---------------------------------------------------------------------------

def _create_and_start_attempt(client: TestClient, session: Session, test_id: int) -> int:
    login_student(client, "student1@test.edu")
    create_resp = client.post(f"/api/student/tests/{test_id}/attempt")
    assert create_resp.status_code == 201
    attempt_id = create_resp.json()["id"]
    start_resp = client.post(f"/api/student/attempts/{attempt_id}/start")
    assert start_resp.status_code == 200
    return attempt_id


def _add_question_and_option(session: Session, test_id: int, question_order: int = 0, correct_label: str = "B") -> int:
    q = Question(
        test_id=test_id,
        question_text=f"Question {question_order + 1}?",
        marks=1.0,
        order_index=question_order,
    )
    session.add(q)
    session.commit()
    session.refresh(q)
    labels = ["A", "B", "C", "D"]
    for label in labels:
        o = Option(
            question_id=q.id,
            option_text=f"Option {label}",
            label=label,
            is_correct=(label == correct_label),
        )
        session.add(o)
    session.commit()
    return q.id


def test_save_answer_creates_new_answer(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    question_id = _add_question_and_option(session, test.id, 0)

    attempt_id = _create_and_start_attempt(client, session, test.id)

    resp = client.put(
        f"/api/student/attempts/{attempt_id}/answers/{question_id}",
        json={"selected_option_id": 1},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["attempt_id"] == attempt_id
    assert data["question_id"] == question_id
    assert data["selected_option_id"] == 1
    assert data["is_marked_for_review"] is False
    assert data["saved_at"] is not None


def test_save_answer_updates_existing_answer(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    question_id = _add_question_and_option(session, test.id, 0)

    attempt_id = _create_and_start_attempt(client, session, test.id)

    resp1 = client.put(
        f"/api/student/attempts/{attempt_id}/answers/{question_id}",
        json={"selected_option_id": 1},
    )
    assert resp1.status_code == 200
    saved_at_1 = resp1.json()["saved_at"]

    import time
    time.sleep(0.01)
    resp2 = client.put(
        f"/api/student/attempts/{attempt_id}/answers/{question_id}",
        json={"selected_option_id": 2},
    )
    assert resp2.status_code == 200
    data = resp2.json()
    assert data["attempt_id"] == attempt_id
    assert data["question_id"] == question_id
    assert data["selected_option_id"] == 2
    assert data["saved_at"] != saved_at_1


def test_save_answer_clears_option_when_null(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    question_id = _add_question_and_option(session, test.id, 0)

    attempt_id = _create_and_start_attempt(client, session, test.id)

    client.put(
        f"/api/student/attempts/{attempt_id}/answers/{question_id}",
        json={"selected_option_id": 1},
    )

    resp = client.put(
        f"/api/student/attempts/{attempt_id}/answers/{question_id}",
        json={"selected_option_id": None},
    )
    assert resp.status_code == 200
    assert resp.json()["selected_option_id"] is None


def test_save_answer_wrong_student_403(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student1 = create_user(session, "student1@test.edu", UserRole.student)
    student2 = create_user(session, "student2@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    question_id = _add_question_and_option(session, test.id, 0)

    login_student(client, "student1@test.edu")
    attempt_id = _create_and_start_attempt(client, session, test.id)

    login_student(client, "student2@test.edu")
    resp = client.put(
        f"/api/student/attempts/{attempt_id}/answers/{question_id}",
        json={"selected_option_id": 1},
    )
    assert resp.status_code == 403


def test_save_answer_missing_attempt_404(client: TestClient, session: Session):
    student = create_user(session, "student1@test.edu", UserRole.student)
    login_student(client, "student1@test.edu")

    resp = client.put(
        "/api/student/attempts/99999/answers/1",
        json={"selected_option_id": 1},
    )
    assert resp.status_code == 404


def test_save_answer_before_start_409(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    question_id = _add_question_and_option(session, test.id, 0)

    login_student(client, "student1@test.edu")
    create_resp = client.post(f"/api/student/tests/{test.id}/attempt")
    attempt_id = create_resp.json()["id"]

    resp = client.put(
        f"/api/student/attempts/{attempt_id}/answers/{question_id}",
        json={"selected_option_id": 1},
    )
    assert resp.status_code == 409


def test_save_answer_after_expiry_409(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    test.duration_minutes = 1
    session.add(test)
    session.commit()
    question_id = _add_question_and_option(session, test.id, 0)

    login_student(client, "student1@test.edu")
    attempt_id = _create_and_start_attempt(client, session, test.id)

    from app.models.attempt import Attempt
    attempt = session.get(Attempt, attempt_id)
    from datetime import timedelta
    attempt.time_limit_ends_at = datetime.now(timezone.utc) - timedelta(minutes=5)
    session.add(attempt)
    session.commit()

    resp = client.put(
        f"/api/student/attempts/{attempt_id}/answers/{question_id}",
        json={"selected_option_id": 1},
    )
    assert resp.status_code == 409


def test_get_answers_success(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    q1_id = _add_question_and_option(session, test.id, 0)
    q2_id = _add_question_and_option(session, test.id, 1)

    # Get option IDs that belong to each question
    from app.models.option import Option
    q1_options = session.exec(
        select(Option).where(Option.question_id == q1_id)
    ).all()
    q2_options = session.exec(
        select(Option).where(Option.question_id == q2_id)
    ).all()
    q1_option_id = q1_options[0].id
    q2_option_id = q2_options[0].id

    attempt_id = _create_and_start_attempt(client, session, test.id)

    client.put(
        f"/api/student/attempts/{attempt_id}/answers/{q1_id}",
        json={"selected_option_id": q1_option_id},
    )
    client.put(
        f"/api/student/attempts/{attempt_id}/answers/{q2_id}",
        json={"selected_option_id": q2_option_id},
    )

    resp = client.get(f"/api/student/attempts/{attempt_id}/answers")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    question_ids = sorted([a["question_id"] for a in data])
    assert question_ids == [q1_id, q2_id]


def test_get_answers_empty_list(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)

    attempt_id = _create_and_start_attempt(client, session, test.id)

    resp = client.get(f"/api/student/attempts/{attempt_id}/answers")
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_answers_wrong_student_403(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student1 = create_user(session, "student1@test.edu", UserRole.student)
    student2 = create_user(session, "student2@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    question_id = _add_question_and_option(session, test.id, 0)

    login_student(client, "student1@test.edu")
    attempt_id = _create_and_start_attempt(client, session, test.id)

    login_student(client, "student2@test.edu")
    resp = client.get(f"/api/student/attempts/{attempt_id}/answers")
    assert resp.status_code == 403


def test_get_answers_missing_attempt_404(client: TestClient, session: Session):
    student = create_user(session, "student1@test.edu", UserRole.student)
    login_student(client, "student1@test.edu")

    resp = client.get("/api/student/attempts/99999/answers")
    assert resp.status_code == 404


def test_clear_answer_existing(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    question_id = _add_question_and_option(session, test.id, 0)

    attempt_id = _create_and_start_attempt(client, session, test.id)

    client.put(
        f"/api/student/attempts/{attempt_id}/answers/{question_id}",
        json={"selected_option_id": 1},
    )

    resp = client.delete(
        f"/api/student/attempts/{attempt_id}/answers/{question_id}",
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["detail"] == "Answer cleared"
    assert data["question_id"] == question_id
    assert data["answer"]["selected_option_id"] is None
    assert data["answer"]["is_marked_for_review"] is False
    assert data["answer"]["saved_at"] is not None


def test_clear_answer_nonexistent_returns_success(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    question_id = _add_question_and_option(session, test.id, 0)

    attempt_id = _create_and_start_attempt(client, session, test.id)

    resp = client.delete(
        f"/api/student/attempts/{attempt_id}/answers/{question_id}",
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["detail"] == "No answer to clear"
    assert data["question_id"] == question_id


def test_clear_answer_wrong_student_403(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student1 = create_user(session, "student1@test.edu", UserRole.student)
    student2 = create_user(session, "student2@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    question_id = _add_question_and_option(session, test.id, 0)

    login_student(client, "student1@test.edu")
    attempt_id = _create_and_start_attempt(client, session, test.id)

    login_student(client, "student2@test.edu")
    resp = client.delete(
        f"/api/student/attempts/{attempt_id}/answers/{question_id}",
    )
    assert resp.status_code == 403


def test_clear_answer_missing_attempt_404(client: TestClient, session: Session):
    student = create_user(session, "student1@test.edu", UserRole.student)
    login_student(client, "student1@test.edu")

    resp = client.delete("/api/student/attempts/99999/answers/1")
    assert resp.status_code == 404


def test_clear_answer_before_start_409(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    question_id = _add_question_and_option(session, test.id, 0)

    login_student(client, "student1@test.edu")
    create_resp = client.post(f"/api/student/tests/{test.id}/attempt")
    attempt_id = create_resp.json()["id"]

    resp = client.delete(
        f"/api/student/attempts/{attempt_id}/answers/{question_id}",
    )
    assert resp.status_code == 409


# ---------------------------------------------------------------------------
# Mark-for-review persistence tests
# ---------------------------------------------------------------------------

def test_save_answer_mark_for_review_true(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    question_id = _add_question_and_option(session, test.id, 0)

    attempt_id = _create_and_start_attempt(client, session, test.id)

    resp = client.put(
        f"/api/student/attempts/{attempt_id}/answers/{question_id}",
        json={"selected_option_id": 1, "is_marked_for_review": True},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_marked_for_review"] is True


def test_save_answer_mark_for_review_update_false(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    question_id = _add_question_and_option(session, test.id, 0)

    attempt_id = _create_and_start_attempt(client, session, test.id)

    # Save with mark-for-review true
    client.put(
        f"/api/student/attempts/{attempt_id}/answers/{question_id}",
        json={"selected_option_id": 1, "is_marked_for_review": True},
    )

    # Update to false
    resp = client.put(
        f"/api/student/attempts/{attempt_id}/answers/{question_id}",
        json={"selected_option_id": 2, "is_marked_for_review": False},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_marked_for_review"] is False
    assert data["selected_option_id"] == 2


def test_get_answers_preserves_mark_for_review(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    question_id = _add_question_and_option(session, test.id, 0)

    attempt_id = _create_and_start_attempt(client, session, test.id)

    client.put(
        f"/api/student/attempts/{attempt_id}/answers/{question_id}",
        json={"selected_option_id": 1, "is_marked_for_review": True},
    )

    resp = client.get(f"/api/student/attempts/{attempt_id}/answers")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["is_marked_for_review"] is True


def test_clear_answer_preserves_mark_for_review(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    question_id = _add_question_and_option(session, test.id, 0)

    attempt_id = _create_and_start_attempt(client, session, test.id)

    # Save with mark-for-review true
    client.put(
        f"/api/student/attempts/{attempt_id}/answers/{question_id}",
        json={"selected_option_id": 1, "is_marked_for_review": True},
    )

    # Clear - mark-for-review should be preserved
    resp = client.delete(
        f"/api/student/attempts/{attempt_id}/answers/{question_id}",
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["detail"] == "Answer cleared"
    assert data["answer"]["selected_option_id"] is None
    assert data["answer"]["is_marked_for_review"] is True


# ---------------------------------------------------------------------------
# Question and option ownership tests
# ---------------------------------------------------------------------------

def test_save_answer_question_from_another_test_409(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test1 = create_active_test(session, "Exam 1", "PXAM-AAAAA", teacher.id)
    test2 = create_active_test(session, "Exam 2", "PXAM-BBBBB", teacher.id)
    question_id = _add_question_and_option(session, test2.id, 0)

    attempt_id = _create_and_start_attempt(client, session, test1.id)

    resp = client.put(
        f"/api/student/attempts/{attempt_id}/answers/{question_id}",
        json={"selected_option_id": 1},
    )
    assert resp.status_code == 409


def test_save_answer_option_from_another_question_409(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    q1_id = _add_question_and_option(session, test.id, 0, correct_label="B")
    q2_id = _add_question_and_option(session, test.id, 1, correct_label="D")

    # Get an option that belongs to q2, not q1
    from app.models.option import Option
    q2_options = session.exec(
        select(Option).where(Option.question_id == q2_id)
    ).all()
    q2_option_id = q2_options[0].id

    attempt_id = _create_and_start_attempt(client, session, test.id)

    resp = client.put(
        f"/api/student/attempts/{attempt_id}/answers/{q1_id}",
        json={"selected_option_id": q2_option_id},
    )
    assert resp.status_code == 409


def test_save_answer_invalid_option_id_404(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    question_id = _add_question_and_option(session, test.id, 0)

    attempt_id = _create_and_start_attempt(client, session, test.id)

    resp = client.put(
        f"/api/student/attempts/{attempt_id}/answers/{question_id}",
        json={"selected_option_id": 99999},
    )
    assert resp.status_code == 404


def test_save_answer_invalid_question_id_404(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)

    attempt_id = _create_and_start_attempt(client, session, test.id)

    resp = client.put(
        "/api/student/attempts/{}/answers/99999".format(attempt_id),
        json={"selected_option_id": 1},
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Attempt state rejection tests (submitted / timed-out)
# ---------------------------------------------------------------------------

def test_save_answer_submitted_attempt_409(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    question_id = _add_question_and_option(session, test.id, 0)

    login_student(client, "student1@test.edu")
    create_resp = client.post(f"/api/student/tests/{test.id}/attempt")
    attempt_id = create_resp.json()["id"]
    client.post(f"/api/student/attempts/{attempt_id}/start")

    # Manually submit
    from app.models.attempt import Attempt
    attempt = session.get(Attempt, attempt_id)
    attempt.status = AttemptStatus.submitted
    attempt.submitted_at = datetime.now(timezone.utc)
    session.add(attempt)
    session.commit()

    resp = client.put(
        f"/api/student/attempts/{attempt_id}/answers/{question_id}",
        json={"selected_option_id": 1},
    )
    assert resp.status_code == 409


def test_clear_answer_submitted_attempt_409(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    question_id = _add_question_and_option(session, test.id, 0)

    login_student(client, "student1@test.edu")
    create_resp = client.post(f"/api/student/tests/{test.id}/attempt")
    attempt_id = create_resp.json()["id"]
    client.post(f"/api/student/attempts/{attempt_id}/start")

    from app.models.attempt import Attempt
    attempt = session.get(Attempt, attempt_id)
    attempt.status = AttemptStatus.submitted
    attempt.submitted_at = datetime.now(timezone.utc)
    session.add(attempt)
    session.commit()

    resp = client.delete(
        f"/api/student/attempts/{attempt_id}/answers/{question_id}",
    )
    assert resp.status_code == 409


def test_save_answer_timed_out_attempt_409(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    question_id = _add_question_and_option(session, test.id, 0)

    login_student(client, "student1@test.edu")
    create_resp = client.post(f"/api/student/tests/{test.id}/attempt")
    attempt_id = create_resp.json()["id"]
    client.post(f"/api/student/attempts/{attempt_id}/start")

    from app.models.attempt import Attempt
    attempt = session.get(Attempt, attempt_id)
    attempt.status = AttemptStatus.timed_out
    session.add(attempt)
    session.commit()

    resp = client.put(
        f"/api/student/attempts/{attempt_id}/answers/{question_id}",
        json={"selected_option_id": 1},
    )
    assert resp.status_code == 409


def test_clear_answer_timed_out_attempt_409(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    question_id = _add_question_and_option(session, test.id, 0)

    login_student(client, "student1@test.edu")
    create_resp = client.post(f"/api/student/tests/{test.id}/attempt")
    attempt_id = create_resp.json()["id"]
    client.post(f"/api/student/attempts/{attempt_id}/start")

    from app.models.attempt import Attempt
    attempt = session.get(Attempt, attempt_id)
    attempt.status = AttemptStatus.timed_out
    session.add(attempt)
    session.commit()

    resp = client.delete(
        f"/api/student/attempts/{attempt_id}/answers/{question_id}",
    )
    assert resp.status_code == 409


def test_save_answer_expired_deadline_finalizes_timed_out(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    question_id = _add_question_and_option(session, test.id, 0)

    login_student(client, "student1@test.edu")
    attempt_id = _create_and_start_attempt(client, session, test.id)

    from app.models.attempt import Attempt
    from datetime import timedelta
    attempt = session.get(Attempt, attempt_id)
    attempt.time_limit_ends_at = datetime.now(timezone.utc) - timedelta(minutes=5)
    session.add(attempt)
    session.commit()

    before_status = attempt.status

    resp = client.put(
        f"/api/student/attempts/{attempt_id}/answers/{question_id}",
        json={"selected_option_id": 1},
    )
    assert resp.status_code == 409

    # Verify attempt was finalized as timed_out
    attempt = session.get(Attempt, attempt_id)
    assert attempt.status == AttemptStatus.timed_out
    assert attempt.submitted_at is not None
    assert attempt.status != before_status

    # Verify result was created
    result = session.exec(select(Result).where(Result.attempt_id == attempt_id)).first()
    assert result is not None


# ---------------------------------------------------------------------------
# Unauthenticated access tests
# ---------------------------------------------------------------------------

def test_save_answer_unauthenticated_401(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    question_id = _add_question_and_option(session, test.id, 0)

    resp = client.put(
        "/api/student/attempts/1/answers/{}".format(question_id),
        json={"selected_option_id": 1},
    )
    assert resp.status_code == 401


def test_get_answers_unauthenticated_401(client: TestClient, session: Session):
    resp = client.get("/api/student/attempts/1/answers")
    assert resp.status_code == 401


def test_clear_answer_unauthenticated_401(client: TestClient, session: Session):
    resp = client.delete("/api/student/attempts/1/answers/1")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Response security: no correct-answer leakage
# ---------------------------------------------------------------------------

def test_get_answers_excludes_correct_answers(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    question_id = _add_question_and_option(session, test.id, 0)

    attempt_id = _create_and_start_attempt(client, session, test.id)

    client.put(
        f"/api/student/attempts/{attempt_id}/answers/{question_id}",
        json={"selected_option_id": 2},
    )

    resp = client.get(f"/api/student/attempts/{attempt_id}/answers")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    answer = data[0]
    assert "is_correct" not in answer
    assert "correct_option_id" not in answer
    assert answer["selected_option_id"] == 2


# ---------------------------------------------------------------------------
# Submission and Result Tests
# ---------------------------------------------------------------------------

def _add_question_with_correct_option(session: Session, test_id: int, question_order: int = 0, correct_label: str = "B", marks: float = 2.0) -> int:
    q = Question(
        test_id=test_id,
        question_text=f"Question {question_order + 1}?",
        marks=marks,
        order_index=question_order,
    )
    session.add(q)
    session.commit()
    session.refresh(q)
    labels = ["A", "B", "C", "D"]
    for label in labels:
        o = Option(
            question_id=q.id,
            option_text=f"Option {label}",
            label=label,
            is_correct=(label == correct_label),
        )
        session.add(o)
    session.commit()
    return q.id


def test_submit_attempt_success_before_deadline(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    test.duration_minutes = 60
    session.add(test)
    session.commit()
    q1_id = _add_question_with_correct_option(session, test.id, 0, correct_label="B", marks=2.0)
    q2_id = _add_question_with_correct_option(session, test.id, 1, correct_label="D", marks=3.0)

    login_student(client, "student1@test.edu")
    attempt_id = _create_and_start_attempt(client, session, test.id)

    # Save answers: q1 correct (B), q2 incorrect (A instead of D)
    from app.models.option import Option
    q1_options = session.exec(select(Option).where(Option.question_id == q1_id)).all()
    q2_options = session.exec(select(Option).where(Option.question_id == q2_id)).all()
    q1_correct_id = [o.id for o in q1_options if o.label == "B"][0]
    q2_wrong_id = [o.id for o in q2_options if o.label == "A"][0]

    client.put(
        f"/api/student/attempts/{attempt_id}/answers/{q1_id}",
        json={"selected_option_id": q1_correct_id},
    )
    client.put(
        f"/api/student/attempts/{attempt_id}/answers/{q2_id}",
        json={"selected_option_id": q2_wrong_id},
    )

    resp = client.post(f"/api/student/attempts/{attempt_id}/submit")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "submitted"
    assert data["submitted_at"] is not None
    assert data["result"] is not None
    assert data["result"]["score"] == 2.0
    assert data["result"]["total_marks"] == 5.0
    assert data["result"]["correct_count"] == 1
    assert data["result"]["incorrect_count"] == 1
    assert data["result"]["unanswered_count"] == 0
    assert data["result"]["percentage"] == 40.0


def test_submit_attempt_after_deadline_timed_out(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    test.duration_minutes = 60
    session.add(test)
    session.commit()
    q1_id = _add_question_with_correct_option(session, test.id, 0, correct_label="B", marks=2.0)

    login_student(client, "student1@test.edu")
    attempt_id = _create_and_start_attempt(client, session, test.id)

    # Manually set deadline to the past
    from datetime import timedelta
    attempt = session.get(Attempt, attempt_id)
    attempt.time_limit_ends_at = datetime.now(timezone.utc) - timedelta(minutes=5)
    session.add(attempt)
    session.commit()

    resp = client.post(f"/api/student/attempts/{attempt_id}/submit")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "timed_out"
    assert data["submitted_at"] is not None
    assert data["result"] is not None


def test_submit_created_attempt_rejected(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)

    login_student(client, "student1@test.edu")
    create_resp = client.post(f"/api/student/tests/{test.id}/attempt")
    attempt_id = create_resp.json()["id"]
    # Attempt is 'created', not started

    resp = client.post(f"/api/student/attempts/{attempt_id}/submit")
    assert resp.status_code == 409


def test_submit_already_submitted_repeat_safe(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    test.duration_minutes = 60
    session.add(test)
    session.commit()
    q1_id = _add_question_with_correct_option(session, test.id, 0, correct_label="B", marks=2.0)

    login_student(client, "student1@test.edu")
    attempt_id = _create_and_start_attempt(client, session, test.id)

    # First submission
    resp1 = client.post(f"/api/student/attempts/{attempt_id}/submit")
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["status"] == "submitted"

    # Second submission - should be repeat-safe
    resp2 = client.post(f"/api/student/attempts/{attempt_id}/submit")
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["status"] == "submitted"
    assert data2["result"]["id"] == data1["result"]["id"]


def test_submit_already_timed_out_repeat_safe(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    test.duration_minutes = 60
    session.add(test)
    session.commit()

    login_student(client, "student1@test.edu")
    attempt_id = _create_and_start_attempt(client, session, test.id)

    # Manually mark as timed_out
    attempt = session.get(Attempt, attempt_id)
    attempt.status = AttemptStatus.timed_out
    attempt.submitted_at = datetime.now(timezone.utc)
    session.add(attempt)
    session.commit()

    resp = client.post(f"/api/student/attempts/{attempt_id}/submit")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "timed_out"


def test_submit_missing_attempt_404(client: TestClient, session: Session):
    student = create_user(session, "student1@test.edu", UserRole.student)
    login_student(client, "student1@test.edu")

    resp = client.post("/api/student/attempts/99999/submit")
    assert resp.status_code == 404


def test_submit_wrong_student_403(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student1 = create_user(session, "student1@test.edu", UserRole.student)
    student2 = create_user(session, "student2@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)

    login_student(client, "student1@test.edu")
    attempt_id = _create_and_start_attempt(client, session, test.id)

    login_student(client, "student2@test.edu")
    resp = client.post(f"/api/student/attempts/{attempt_id}/submit")
    assert resp.status_code == 403


def test_submit_all_correct(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    test.duration_minutes = 60
    session.add(test)
    session.commit()
    q1_id = _add_question_with_correct_option(session, test.id, 0, correct_label="B", marks=2.0)
    q2_id = _add_question_with_correct_option(session, test.id, 1, correct_label="D", marks=3.0)

    login_student(client, "student1@test.edu")
    attempt_id = _create_and_start_attempt(client, session, test.id)

    from app.models.option import Option
    q1_options = session.exec(select(Option).where(Option.question_id == q1_id)).all()
    q2_options = session.exec(select(Option).where(Option.question_id == q2_id)).all()
    q1_correct_id = [o.id for o in q1_options if o.label == "B"][0]
    q2_correct_id = [o.id for o in q2_options if o.label == "D"][0]

    client.put(
        f"/api/student/attempts/{attempt_id}/answers/{q1_id}",
        json={"selected_option_id": q1_correct_id},
    )
    client.put(
        f"/api/student/attempts/{attempt_id}/answers/{q2_id}",
        json={"selected_option_id": q2_correct_id},
    )

    resp = client.post(f"/api/student/attempts/{attempt_id}/submit")
    assert resp.status_code == 200
    data = resp.json()
    assert data["result"]["score"] == 5.0
    assert data["result"]["total_marks"] == 5.0
    assert data["result"]["correct_count"] == 2
    assert data["result"]["incorrect_count"] == 0
    assert data["result"]["unanswered_count"] == 0
    assert data["result"]["percentage"] == 100.0


def test_submit_unanswered_questions(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    test.duration_minutes = 60
    session.add(test)
    session.commit()
    q1_id = _add_question_with_correct_option(session, test.id, 0, correct_label="B", marks=2.0)
    q2_id = _add_question_with_correct_option(session, test.id, 1, correct_label="D", marks=3.0)

    login_student(client, "student1@test.edu")
    attempt_id = _create_and_start_attempt(client, session, test.id)

    # Answer only q1, leave q2 unanswered
    from app.models.option import Option
    q1_options = session.exec(select(Option).where(Option.question_id == q1_id)).all()
    q1_correct_id = [o.id for o in q1_options if o.label == "B"][0]

    client.put(
        f"/api/student/attempts/{attempt_id}/answers/{q1_id}",
        json={"selected_option_id": q1_correct_id},
    )

    resp = client.post(f"/api/student/attempts/{attempt_id}/submit")
    assert resp.status_code == 200
    data = resp.json()
    assert data["result"]["score"] == 2.0
    assert data["result"]["total_marks"] == 5.0
    assert data["result"]["correct_count"] == 1
    assert data["result"]["incorrect_count"] == 0
    assert data["result"]["unanswered_count"] == 1
    assert data["result"]["percentage"] == 40.0


def test_submit_mark_for_review_no_score_impact(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    test.duration_minutes = 60
    session.add(test)
    session.commit()
    q1_id = _add_question_with_correct_option(session, test.id, 0, correct_label="B", marks=2.0)

    login_student(client, "student1@test.edu")
    attempt_id = _create_and_start_attempt(client, session, test.id)

    from app.models.option import Option
    q1_options = session.exec(select(Option).where(Option.question_id == q1_id)).all()
    q1_correct_id = [o.id for o in q1_options if o.label == "B"][0]

    # Save answer with mark_for_review=True
    client.put(
        f"/api/student/attempts/{attempt_id}/answers/{q1_id}",
        json={"selected_option_id": q1_correct_id, "is_marked_for_review": True},
    )

    resp = client.post(f"/api/student/attempts/{attempt_id}/submit")
    assert resp.status_code == 200
    data = resp.json()
    assert data["result"]["score"] == 2.0
    assert data["result"]["correct_count"] == 1


def test_save_answer_after_expiry_finalizes_timed_out(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    test.duration_minutes = 60
    session.add(test)
    session.commit()
    q1_id = _add_question_with_correct_option(session, test.id, 0, correct_label="B", marks=2.0)

    login_student(client, "student1@test.edu")
    attempt_id = _create_and_start_attempt(client, session, test.id)

    from datetime import timedelta
    attempt = session.get(Attempt, attempt_id)
    attempt.time_limit_ends_at = datetime.now(timezone.utc) - timedelta(minutes=5)
    session.add(attempt)
    session.commit()

    # Try to save an answer - should be rejected and attempt finalized as timed_out
    resp = client.put(
        f"/api/student/attempts/{attempt_id}/answers/{q1_id}",
        json={"selected_option_id": 1},
    )
    assert resp.status_code == 409

    # Verify attempt was finalized as timed_out
    attempt = session.get(Attempt, attempt_id)
    assert attempt.status == AttemptStatus.timed_out
    assert attempt.submitted_at is not None

    # Verify result was created
    result = session.exec(select(Result).where(Result.attempt_id == attempt_id)).first()
    assert result is not None


def test_clear_answer_after_expiry_finalizes_timed_out(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    test.duration_minutes = 60
    session.add(test)
    session.commit()
    q1_id = _add_question_with_correct_option(session, test.id, 0, correct_label="B", marks=2.0)

    login_student(client, "student1@test.edu")
    attempt_id = _create_and_start_attempt(client, session, test.id)

    # Save an answer first
    client.put(
        f"/api/student/attempts/{attempt_id}/answers/{q1_id}",
        json={"selected_option_id": 1},
    )

    from datetime import timedelta
    attempt = session.get(Attempt, attempt_id)
    attempt.time_limit_ends_at = datetime.now(timezone.utc) - timedelta(minutes=5)
    session.add(attempt)
    session.commit()

    # Try to clear an answer - should be rejected and attempt finalized as timed_out
    resp = client.delete(
        f"/api/student/attempts/{attempt_id}/answers/{q1_id}",
    )
    assert resp.status_code == 409

    # Verify attempt was finalized as timed_out
    attempt = session.get(Attempt, attempt_id)
    assert attempt.status == AttemptStatus.timed_out
    assert attempt.submitted_at is not None

    # Verify result was created
    result = session.exec(select(Result).where(Result.attempt_id == attempt_id)).first()
    assert result is not None


# ---------------------------------------------------------------------------
# Result Retrieval Tests
# ---------------------------------------------------------------------------

def test_get_result_success(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    test.duration_minutes = 60
    session.add(test)
    session.commit()
    q1_id = _add_question_with_correct_option(session, test.id, 0, correct_label="B", marks=2.0)

    login_student(client, "student1@test.edu")
    attempt_id = _create_and_start_attempt(client, session, test.id)

    from app.models.option import Option
    q1_options = session.exec(select(Option).where(Option.question_id == q1_id)).all()
    q1_correct_id = [o.id for o in q1_options if o.label == "B"][0]

    client.put(
        f"/api/student/attempts/{attempt_id}/answers/{q1_id}",
        json={"selected_option_id": q1_correct_id},
    )

    # Submit first
    submit_resp = client.post(f"/api/student/attempts/{attempt_id}/submit")
    assert submit_resp.status_code == 200

    # Now retrieve the result
    resp = client.get(f"/api/student/attempts/{attempt_id}/result")
    assert resp.status_code == 200
    data = resp.json()
    assert data["attempt_id"] == attempt_id
    assert data["score"] == 2.0
    assert data["total_marks"] == 2.0
    assert data["correct_count"] == 1
    assert data["incorrect_count"] == 0
    assert data["unanswered_count"] == 0
    assert data["percentage"] == 100.0
    assert "calculated_at" in data


def test_get_result_returns_submitted_status(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    test.duration_minutes = 60
    session.add(test)
    session.commit()
    q1_id = _add_question_with_correct_option(session, test.id, 0, correct_label="B", marks=2.0)

    login_student(client, "student1@test.edu")
    attempt_id = _create_and_start_attempt(client, session, test.id)

    from app.models.option import Option
    q1_options = session.exec(select(Option).where(Option.question_id == q1_id)).all()
    q1_correct_id = [o.id for o in q1_options if o.label == "B"][0]

    client.put(
        f"/api/student/attempts/{attempt_id}/answers/{q1_id}",
        json={"selected_option_id": q1_correct_id},
    )

    submit_resp = client.post(f"/api/student/attempts/{attempt_id}/submit")
    assert submit_resp.status_code == 200

    resp = client.get(f"/api/student/attempts/{attempt_id}/result")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "submitted"
    assert data["attempt_id"] == attempt_id
    assert data["score"] == 2.0
    assert data["total_marks"] == 2.0
    assert data["correct_count"] == 1
    assert data["incorrect_count"] == 0
    assert data["unanswered_count"] == 0
    assert data["percentage"] == 100.0
    assert "calculated_at" in data


def test_get_result_returns_timed_out_status(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    test.duration_minutes = 60
    session.add(test)
    session.commit()
    q1_id = _add_question_with_correct_option(session, test.id, 0, correct_label="B", marks=2.0)

    login_student(client, "student1@test.edu")
    attempt_id = _create_and_start_attempt(client, session, test.id)

    # Mark deadline as past so submission finalizes as timed_out
    from app.models.attempt import Attempt
    from datetime import timedelta
    attempt = session.get(Attempt, attempt_id)
    attempt.time_limit_ends_at = datetime.now(timezone.utc) - timedelta(minutes=5)
    session.add(attempt)
    session.commit()

    resp = client.post(f"/api/student/attempts/{attempt_id}/submit")
    assert resp.status_code == 200

    result_resp = client.get(f"/api/student/attempts/{attempt_id}/result")
    assert result_resp.status_code == 200
    data = result_resp.json()
    assert data["status"] == "timed_out"
    assert data["attempt_id"] == attempt_id
    assert data["score"] == 0.0
    assert data["total_marks"] == 2.0
    assert data["correct_count"] == 0
    assert data["incorrect_count"] == 0
    assert data["unanswered_count"] == 1
    assert data["percentage"] == 0.0
    assert "calculated_at" in data


def test_get_result_wrong_student_403(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student1 = create_user(session, "student1@test.edu", UserRole.student)
    student2 = create_user(session, "student2@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    test.duration_minutes = 60
    session.add(test)
    session.commit()
    q1_id = _add_question_with_correct_option(session, test.id, 0, correct_label="B", marks=2.0)

    login_student(client, "student1@test.edu")
    attempt_id = _create_and_start_attempt(client, session, test.id)

    # Submit
    client.post(f"/api/student/attempts/{attempt_id}/submit")

    # Wrong student tries to retrieve result
    login_student(client, "student2@test.edu")
    resp = client.get(f"/api/student/attempts/{attempt_id}/result")
    assert resp.status_code == 403


def test_get_result_missing_attempt_404(client: TestClient, session: Session):
    student = create_user(session, "student1@test.edu", UserRole.student)
    login_student(client, "student1@test.edu")

    resp = client.get("/api/student/attempts/99999/result")
    assert resp.status_code == 404


def test_get_result_before_finalization_409(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    test.duration_minutes = 60
    session.add(test)
    session.commit()
    _add_question_with_correct_option(session, test.id, 0, correct_label="B", marks=2.0)

    login_student(client, "student1@test.edu")
    attempt_id = _create_and_start_attempt(client, session, test.id)
    # Attempt is 'in_progress' but not submitted

    resp = client.get(f"/api/student/attempts/{attempt_id}/result")
    assert resp.status_code == 409


# ---------------------------------------------------------------------------
# Atomicity and Concurrency Tests
# ---------------------------------------------------------------------------

def test_sequential_duplicate_submission_idempotent(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    test.duration_minutes = 60
    session.add(test)
    session.commit()
    q1_id = _add_question_with_correct_option(session, test.id, 0, correct_label="B", marks=2.0)

    login_student(client, "student1@test.edu")
    attempt_id = _create_and_start_attempt(client, session, test.id)

    from app.models.option import Option
    q1_options = session.exec(select(Option).where(Option.question_id == q1_id)).all()
    q1_correct_id = [o.id for o in q1_options if o.label == "B"][0]

    client.put(
        f"/api/student/attempts/{attempt_id}/answers/{q1_id}",
        json={"selected_option_id": q1_correct_id},
    )

    # First submission
    resp1 = client.post(f"/api/student/attempts/{attempt_id}/submit")
    assert resp1.status_code == 200
    result_id_1 = resp1.json()["result"]["id"]
    submitted_at_1 = resp1.json()["submitted_at"]

    # Second submission - should be idempotent
    resp2 = client.post(f"/api/student/attempts/{attempt_id}/submit")
    assert resp2.status_code == 200
    result_id_2 = resp2.json()["result"]["id"]
    submitted_at_2 = resp2.json()["submitted_at"]

    assert result_id_1 == result_id_2
    assert submitted_at_1 == submitted_at_2


def test_timeout_finalization_via_save_is_atomic(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    test.duration_minutes = 60
    session.add(test)
    session.commit()
    q1_id = _add_question_with_correct_option(session, test.id, 0, correct_label="B", marks=2.0)

    login_student(client, "student1@test.edu")
    attempt_id = _create_and_start_attempt(client, session, test.id)

    from datetime import timedelta
    attempt = session.get(Attempt, attempt_id)
    attempt.time_limit_ends_at = datetime.now(timezone.utc) - timedelta(minutes=5)
    session.add(attempt)
    session.commit()

    # Try to save an answer - should be rejected (409) but attempt+result committed
    resp = client.put(
        f"/api/student/attempts/{attempt_id}/answers/{q1_id}",
        json={"selected_option_id": 1},
    )
    assert resp.status_code == 409

    # Verify attempt was finalized as timed_out (committed)
    attempt = session.get(Attempt, attempt_id)
    assert attempt.status == AttemptStatus.timed_out
    assert attempt.submitted_at is not None

    # Verify result was created in the same transaction
    result = session.exec(select(Result).where(Result.attempt_id == attempt_id)).first()
    assert result is not None
    assert result.total_marks == 2.0


def test_timeout_finalization_via_clear_is_atomic(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    test.duration_minutes = 60
    session.add(test)
    session.commit()
    q1_id = _add_question_with_correct_option(session, test.id, 0, correct_label="B", marks=2.0)

    login_student(client, "student1@test.edu")
    attempt_id = _create_and_start_attempt(client, session, test.id)

    # Save an answer first
    client.put(
        f"/api/student/attempts/{attempt_id}/answers/{q1_id}",
        json={"selected_option_id": 1},
    )

    from datetime import timedelta
    attempt = session.get(Attempt, attempt_id)
    attempt.time_limit_ends_at = datetime.now(timezone.utc) - timedelta(minutes=5)
    session.add(attempt)
    session.commit()

    # Try to clear an answer - should be rejected (409) but attempt+result committed
    resp = client.delete(
        f"/api/student/attempts/{attempt_id}/answers/{q1_id}",
    )
    assert resp.status_code == 409

    # Verify attempt was finalized as timed_out (committed)
    attempt = session.get(Attempt, attempt_id)
    assert attempt.status == AttemptStatus.timed_out
    assert attempt.submitted_at is not None

    # Verify result was created in the same transaction
    result = session.exec(select(Result).where(Result.attempt_id == attempt_id)).first()
    assert result is not None


# ---------------------------------------------------------------------------
# Scoring Validation Tests
# ---------------------------------------------------------------------------

def test_scoring_option_from_wrong_question(client: TestClient, session: Session):
    """Verify that an option belonging to a different question is not
    counted as correct during scoring."""
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    test.duration_minutes = 60
    session.add(test)
    session.commit()
    q1_id = _add_question_with_correct_option(session, test.id, 0, correct_label="B", marks=2.0)
    q2_id = _add_question_with_correct_option(session, test.id, 1, correct_label="D", marks=3.0)

    login_student(client, "student1@test.edu")
    attempt_id = _create_and_start_attempt(client, session, test.id)

    from app.models.option import Option
    # Get q2's correct option (D) and try to use it for q1
    q2_options = session.exec(select(Option).where(Option.question_id == q2_id)).all()
    q2_correct_id = [o.id for o in q2_options if o.label == "D"][0]

    # Submit q2's correct option as the answer for q1
    client.put(
        f"/api/student/attempts/{attempt_id}/answers/{q1_id}",
        json={"selected_option_id": q2_correct_id},
    )

    resp = client.post(f"/api/student/attempts/{attempt_id}/submit")
    assert resp.status_code == 200
    data = resp.json()
    # The option belongs to q2, not q1, so it should NOT be counted as correct
    assert data["result"]["correct_count"] == 0
    assert data["result"]["incorrect_count"] == 0
    assert data["result"]["unanswered_count"] == 2
    assert data["result"]["score"] == 0.0


def test_total_marks_consistency_with_question_marks(client: TestClient, session: Session):
    """Verify that the result's total_marks equals the sum of question marks."""
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABCDE", teacher.id)
    test.duration_minutes = 60
    # Set test.total_marks to a different value than the sum of question marks
    test.total_marks = 7.0
    session.add(test)
    session.commit()
    q1_id = _add_question_with_correct_option(session, test.id, 0, correct_label="B", marks=2.0)
    q2_id = _add_question_with_correct_option(session, test.id, 1, correct_label="D", marks=3.0)
    # Sum of question marks = 2.0 + 3.0 = 5.0, but test.total_marks = 7.0
    # The scoring should use sum(question.marks), not test.total_marks

    login_student(client, "student1@test.edu")
    attempt_id = _create_and_start_attempt(client, session, test.id)

    from app.models.option import Option
    q1_options = session.exec(select(Option).where(Option.question_id == q1_id)).all()
    q2_options = session.exec(select(Option).where(Option.question_id == q2_id)).all()
    q1_correct_id = [o.id for o in q1_options if o.label == "B"][0]
    q2_correct_id = [o.id for o in q2_options if o.label == "D"][0]

    client.put(
        f"/api/student/attempts/{attempt_id}/answers/{q1_id}",
        json={"selected_option_id": q1_correct_id},
    )
    client.put(
        f"/api/student/attempts/{attempt_id}/answers/{q2_id}",
        json={"selected_option_id": q2_correct_id},
    )

    resp = client.post(f"/api/student/attempts/{attempt_id}/submit")
    assert resp.status_code == 200
    data = resp.json()
    # total_marks should be sum of question marks (5.0), not test.total_marks (7.0)
    assert data["result"]["total_marks"] == 5.0
    assert data["result"]["score"] == 5.0
    assert data["result"]["correct_count"] == 2
    assert data["result"]["percentage"] == 100.0


# ---------------------------------------------------------------------------
# Attempt History Tests
# ---------------------------------------------------------------------------

def _login_and_create_attempts(
    client: TestClient,
    session: Session,
    student_email: str,
    test_count: int = 2,
) -> list[int]:
    """Helper: create multiple attempts for a student across different tests."""
    teacher = create_user(session, "teacher_history@test.edu", UserRole.teacher)
    student = create_user(session, student_email, UserRole.student)
    attempt_ids = []
    for i in range(test_count):
        test = create_active_test(
            session,
            f"History Test {i + 1}",
            f"PXAM-HIST{i + 1:03d}",
            teacher.id,
        )
        add_questions(session, test.id, 2)
        session.commit()
        login_student(client, student_email)
        create_resp = client.post(f"/api/student/tests/{test.id}/attempt")
        assert create_resp.status_code == 201
        attempt_id = create_resp.json()["id"]
        attempt_ids.append(attempt_id)
    return attempt_ids


def test_student_receives_own_attempts(client: TestClient, session: Session):
    """Authenticated student receives their own attempts only."""
    attempt_ids = _login_and_create_attempts(client, session, "student_hist1@test.edu", 2)

    resp = client.get("/api/student/attempts")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    returned_ids = {item["id"] for item in data}
    assert returned_ids == set(attempt_ids)
    for item in data:
        assert item["test_title"] is not None
        assert item["test_code"] is not None


def test_student_no_attempts_returns_empty_list(client: TestClient, session: Session):
    """Student with no attempts receives an empty list."""
    student = create_user(session, "student_empty@test.edu", UserRole.student)
    login_student(client, "student_empty@test.edu")

    resp = client.get("/api/student/attempts")
    assert resp.status_code == 200
    assert resp.json() == []


def test_student_does_not_see_another_students_attempts(
    client: TestClient, session: Session
):
    """Another student's attempts are never returned."""
    # Student 1 creates attempts
    _login_and_create_attempts(client, session, "student_owner@test.edu", 1)

    # Create and log in as Student 2
    student_other = create_user(
        session, "student_other@test.edu", UserRole.student
    )
    login_student(client, "student_other@test.edu")
    resp = client.get("/api/student/attempts")
    assert resp.status_code == 200
    assert resp.json() == []


def test_history_includes_submitted_attempt_with_result(
    client: TestClient, session: Session
):
    """Submitted attempt includes persisted result fields."""
    teacher = create_user(session, "teacher_sub@test.edu", UserRole.teacher)
    student = create_user(session, "student_sub@test.edu", UserRole.student)
    test = create_active_test(session, "Submitted Exam", "PXAM-SUBMIT", teacher.id)
    q1_id = _add_question_with_correct_option(session, test.id, 0, correct_label="B", marks=2.0)

    login_student(client, "student_sub@test.edu")
    attempt_id = _create_and_start_attempt(client, session, test.id)

    from app.models.option import Option
    q1_options = session.exec(select(Option).where(Option.question_id == q1_id)).all()
    q1_correct_id = [o.id for o in q1_options if o.label == "B"][0]

    client.put(
        f"/api/student/attempts/{attempt_id}/answers/{q1_id}",
        json={"selected_option_id": q1_correct_id},
    )
    client.post(f"/api/student/attempts/{attempt_id}/submit")

    resp = client.get("/api/student/attempts")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    item = data[0]
    assert item["id"] == attempt_id
    assert item["status"] == "submitted"
    assert item["score"] == 2.0
    assert item["total_marks"] == 2.0
    assert item["percentage"] == 100.0
    assert item["correct_count"] == 1
    assert item["incorrect_count"] == 0
    assert item["unanswered_count"] == 0
    assert item["calculated_at"] is not None


def test_history_includes_timed_out_attempt_with_result(
    client: TestClient, session: Session
):
    """Timed-out attempt includes persisted result fields."""
    teacher = create_user(session, "teacher_to@test.edu", UserRole.teacher)
    student = create_user(session, "student_to@test.edu", UserRole.student)
    test = create_active_test(session, "Timed Out Exam", "PXAM-TIMEOUT", teacher.id)
    q1_id = _add_question_with_correct_option(session, test.id, 0, correct_label="B", marks=2.0)

    login_student(client, "student_to@test.edu")
    attempt_id = _create_and_start_attempt(client, session, test.id)

    # Mark deadline as past so submission finalizes as timed_out
    from app.models.attempt import Attempt
    from datetime import timedelta
    attempt = session.get(Attempt, attempt_id)
    attempt.time_limit_ends_at = datetime.now(timezone.utc) - timedelta(minutes=5)
    session.add(attempt)
    session.commit()

    client.post(f"/api/student/attempts/{attempt_id}/submit")

    resp = client.get("/api/student/attempts")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    item = data[0]
    assert item["id"] == attempt_id
    assert item["status"] == "timed_out"
    assert item["score"] == 0.0
    assert item["total_marks"] == 2.0
    assert item["percentage"] == 0.0
    assert item["correct_count"] == 0
    assert item["incorrect_count"] == 0
    assert item["unanswered_count"] == 1
    assert item["calculated_at"] is not None


def test_history_includes_created_attempt_with_null_result(
    client: TestClient, session: Session
):
    """Created/in-progress attempt returns null result fields."""
    teacher = create_user(session, "teacher_created@test.edu", UserRole.teacher)
    student = create_user(session, "student_created@test.edu", UserRole.student)
    test = create_active_test(session, "Created Exam", "PXAM-CREATED", teacher.id)
    add_questions(session, test.id, 1)

    login_student(client, "student_created@test.edu")
    create_resp = client.post(f"/api/student/tests/{test.id}/attempt")
    assert create_resp.status_code == 201
    attempt_id = create_resp.json()["id"]

    resp = client.get("/api/student/attempts")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    item = data[0]
    assert item["id"] == attempt_id
    assert item["status"] == "created"
    assert item["score"] is None
    assert item["total_marks"] is None
    assert item["percentage"] is None
    assert item["correct_count"] is None
    assert item["incorrect_count"] is None
    assert item["unanswered_count"] is None
    assert item["calculated_at"] is None


def test_history_includes_closed_examination(
    client: TestClient, session: Session
):
    """Closed/inactive examinations still appear in historical records."""
    teacher = create_user(session, "teacher_closed@test.edu", UserRole.teacher)
    student = create_user(session, "student_closed@test.edu", UserRole.student)
    test = create_inactive_test(session, "Closed Exam", "PXAM-CLOSED", teacher.id)
    add_questions(session, test.id, 1)

    # Directly insert an attempt for a closed test (API would reject it,
    # but the history endpoint should still surface historical records)
    from app.models.attempt import Attempt, AttemptStatus
    attempt = Attempt(
        test_id=test.id,
        student_id=student.id,
        status=AttemptStatus.created,
        created_at=datetime.now(timezone.utc),
        started_at=None,
        submitted_at=None,
        time_limit_ends_at=None,
        identity_verified=False,
    )
    session.add(attempt)
    session.commit()
    session.refresh(attempt)

    login_student(client, "student_closed@test.edu")
    resp = client.get("/api/student/attempts")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    item = data[0]
    assert item["test_title"] == "Closed Exam"
    assert item["test_code"] == "PXAM-CLOSED"
    assert item["status"] == "created"


def test_history_ordered_newest_first(client: TestClient, session: Session):
    """Attempts are ordered newest first."""
    teacher = create_user(session, "teacher_order@test.edu", UserRole.teacher)
    student = create_user(session, "student_order@test.edu", UserRole.student)

    attempt_ids = []
    for i in range(3):
        test = create_active_test(
            session,
            f"Order Test {i + 1}",
            f"PXAM-ORD{i + 1:03d}",
            teacher.id,
        )
        add_questions(session, test.id, 1)
        session.commit()
        login_student(client, "student_order@test.edu")
        create_resp = client.post(f"/api/student/tests/{test.id}/attempt")
        assert create_resp.status_code == 201
        attempt_ids.append(create_resp.json()["id"])

    resp = client.get("/api/student/attempts")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    # Newest attempt should be first
    assert data[0]["id"] == attempt_ids[2]
    assert data[1]["id"] == attempt_ids[1]
    assert data[2]["id"] == attempt_ids[0]


def test_history_unauthenticated_returns_401(client: TestClient, session: Session):
    """Unauthenticated request returns 401."""
    resp = client.get("/api/student/attempts")
    assert resp.status_code == 401


def test_history_teacher_forbidden_403(client: TestClient, session: Session):
    """Teacher cannot access the student-only endpoint."""
    teacher = create_user(session, "teacher_hist@test.edu", UserRole.teacher)
    client.post("/api/auth/login", json={"email": "teacher_hist@test.edu", "password": "Password123!"})

    resp = client.get("/api/student/attempts")
    assert resp.status_code == 403


def test_history_admin_forbidden_403(client: TestClient, session: Session):
    """Admin cannot access the student-only endpoint."""
    admin = create_user(session, "admin_hist@test.edu", UserRole.admin)
    client.post("/api/auth/login", json={"email": "admin_hist@test.edu", "password": "Password123!"})

    resp = client.get("/api/student/attempts")
    assert resp.status_code == 403
