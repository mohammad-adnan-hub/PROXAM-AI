"""
Integration tests for Teacher Examination Creation Module.
Covers creation, listing, details, updating, deletion, authorization,
and validation logic.
"""
import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.models.user import User, UserRole
from app.models.test import Test, TestStatus
from app.models.attempt import Attempt, AttemptStatus
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


def valid_exam_payload(title="Distributed Systems Midterm"):
    return {
        "title": title,
        "description": "Comprehensive midterm evaluation.",
        "instructions": "Single attempt permitted.",
        "duration_minutes": 45,
        "questions": [
            {
                "question_text": "What is the primary role of a Leader in Raft?",
                "marks": 2.0,
                "order_index": 0,
                "options": [
                    {"label": "A", "option_text": "To coordinate log replication", "is_correct": True},
                    {"label": "B", "option_text": "To vote for Candidates only", "is_correct": False},
                    {"label": "C", "option_text": "To reset local clocks", "is_correct": False},
                    {"label": "D", "option_text": "To initiate split-brain partitions", "is_correct": False},
                ],
            },
            {
                "question_text": "Which CAP theorem property guarantees freshness of read data?",
                "marks": 3.0,
                "order_index": 1,
                "options": [
                    {"label": "A", "option_text": "Availability", "is_correct": False},
                    {"label": "B", "option_text": "Consistency", "is_correct": True},
                    {"label": "C", "option_text": "Partition tolerance", "is_correct": False},
                    {"label": "D", "option_text": "Fault isolation", "is_correct": False},
                ],
            },
        ],
    }


# ---------------------------------------------------------------------------
# Test Creation & Validation Tests
# ---------------------------------------------------------------------------

def test_teacher_create_examination_success(client: TestClient, session: Session):
    create_user(session, "teacher1@test.edu", UserRole.teacher)
    client.post("/api/auth/login", json={"email": "teacher1@test.edu", "password": "Password123!"})

    resp = client.post("/api/tests/", json=valid_exam_payload())
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Distributed Systems Midterm"
    assert data["duration_minutes"] == 45
    assert data["total_marks"] == 5.0
    assert data["status"] == "active"
    assert data["test_code"].startswith("PXAM-")
    assert len(data["test_code"]) == 10
    assert len(data["questions"]) == 2
    assert data["question_count"] == 2


def test_student_cannot_create_examination(client: TestClient, session: Session):
    create_user(session, "student1@test.edu", UserRole.student)
    client.post("/api/auth/login", json={"email": "student1@test.edu", "password": "Password123!"})

    resp = client.post("/api/tests/", json=valid_exam_payload())
    assert resp.status_code == 403


def test_create_exam_missing_title_rejected(client: TestClient, session: Session):
    create_user(session, "teacher1@test.edu", UserRole.teacher)
    client.post("/api/auth/login", json={"email": "teacher1@test.edu", "password": "Password123!"})

    payload = valid_exam_payload()
    payload["title"] = "   "
    resp = client.post("/api/tests/", json=payload)
    assert resp.status_code == 422


def test_create_exam_invalid_duration_rejected(client: TestClient, session: Session):
    create_user(session, "teacher1@test.edu", UserRole.teacher)
    client.post("/api/auth/login", json={"email": "teacher1@test.edu", "password": "Password123!"})

    payload = valid_exam_payload()
    payload["duration_minutes"] = 0
    resp = client.post("/api/tests/", json=payload)
    assert resp.status_code == 422


def test_create_exam_missing_question_text_rejected(client: TestClient, session: Session):
    create_user(session, "teacher1@test.edu", UserRole.teacher)
    client.post("/api/auth/login", json={"email": "teacher1@test.edu", "password": "Password123!"})

    payload = valid_exam_payload()
    payload["questions"][0]["question_text"] = ""
    resp = client.post("/api/tests/", json=payload)
    assert resp.status_code == 422


def test_create_exam_incomplete_options_rejected(client: TestClient, session: Session):
    create_user(session, "teacher1@test.edu", UserRole.teacher)
    client.post("/api/auth/login", json={"email": "teacher1@test.edu", "password": "Password123!"})

    payload = valid_exam_payload()
    payload["questions"][0]["options"] = payload["questions"][0]["options"][:3]  # Only 3 options
    resp = client.post("/api/tests/", json=payload)
    assert resp.status_code == 422


def test_create_exam_no_correct_answer_rejected(client: TestClient, session: Session):
    create_user(session, "teacher1@test.edu", UserRole.teacher)
    client.post("/api/auth/login", json={"email": "teacher1@test.edu", "password": "Password123!"})

    payload = valid_exam_payload()
    for opt in payload["questions"][0]["options"]:
        opt["is_correct"] = False  # No correct answer
    resp = client.post("/api/tests/", json=payload)
    assert resp.status_code == 422


def test_create_exam_multiple_correct_answers_rejected(client: TestClient, session: Session):
    create_user(session, "teacher1@test.edu", UserRole.teacher)
    client.post("/api/auth/login", json={"email": "teacher1@test.edu", "password": "Password123!"})

    payload = valid_exam_payload()
    payload["questions"][0]["options"][1]["is_correct"] = True  # Two correct answers
    resp = client.post("/api/tests/", json=payload)
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Listing, Retrieval, and Ownership Tests
# ---------------------------------------------------------------------------

def test_list_only_logged_in_teacher_examinations(client: TestClient, session: Session):
    t1 = create_user(session, "teacher1@test.edu", UserRole.teacher)
    t2 = create_user(session, "teacher2@test.edu", UserRole.teacher)

    # Teacher 1 creates 2 tests
    client.post("/api/auth/login", json={"email": "teacher1@test.edu", "password": "Password123!"})
    client.post("/api/tests/", json=valid_exam_payload("T1 Exam A"))
    client.post("/api/tests/", json=valid_exam_payload("T1 Exam B"))

    # Teacher 2 creates 1 test
    client.post("/api/auth/login", json={"email": "teacher2@test.edu", "password": "Password123!"})
    client.post("/api/tests/", json=valid_exam_payload("T2 Exam C"))

    # Teacher 2 lists tests
    resp2 = client.get("/api/tests/")
    assert resp2.status_code == 200
    tests2 = resp2.json()
    assert len(tests2) == 1
    assert tests2[0]["title"] == "T2 Exam C"

    # Teacher 1 lists tests
    client.post("/api/auth/login", json={"email": "teacher1@test.edu", "password": "Password123!"})
    resp1 = client.get("/api/tests/")
    assert resp1.status_code == 200
    assert len(resp1.json()) == 2


def test_teacher_cannot_access_another_teachers_test(client: TestClient, session: Session):
    create_user(session, "teacher1@test.edu", UserRole.teacher)
    create_user(session, "teacher2@test.edu", UserRole.teacher)

    client.post("/api/auth/login", json={"email": "teacher1@test.edu", "password": "Password123!"})
    t1_exam = client.post("/api/tests/", json=valid_exam_payload("T1 Private Exam")).json()

    # Teacher 2 tries to access Teacher 1's test
    client.post("/api/auth/login", json={"email": "teacher2@test.edu", "password": "Password123!"})
    detail_resp = client.get(f"/api/tests/{t1_exam['id']}")
    assert detail_resp.status_code == 404


def test_teacher_stats_endpoint(client: TestClient, session: Session):
    create_user(session, "teacher1@test.edu", UserRole.teacher)
    client.post("/api/auth/login", json={"email": "teacher1@test.edu", "password": "Password123!"})

    client.post("/api/tests/", json=valid_exam_payload("Exam 1"))
    client.post("/api/tests/", json=valid_exam_payload("Exam 2"))

    stats_resp = client.get("/api/tests/stats")
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert stats["total_tests"] == 2
    assert stats["active_tests"] == 2
    assert stats["total_attempts"] == 0
    assert len(stats["recent_tests"]) == 2


# ---------------------------------------------------------------------------
# Safe Update and Deletion Tests
# ---------------------------------------------------------------------------

def test_safe_update_without_attempts(client: TestClient, session: Session):
    create_user(session, "teacher1@test.edu", UserRole.teacher)
    client.post("/api/auth/login", json={"email": "teacher1@test.edu", "password": "Password123!"})

    exam = client.post("/api/tests/", json=valid_exam_payload("Original Title")).json()

    # Update title and duration
    update_resp = client.put(f"/api/tests/{exam['id']}", json={
        "title": "Renamed Midterm",
        "duration_minutes": 60,
    })
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "Renamed Midterm"
    assert update_resp.json()["duration_minutes"] == 60


def test_safe_delete_without_attempts(client: TestClient, session: Session):
    create_user(session, "teacher1@test.edu", UserRole.teacher)
    client.post("/api/auth/login", json={"email": "teacher1@test.edu", "password": "Password123!"})

    exam = client.post("/api/tests/", json=valid_exam_payload("To Be Deleted")).json()

    del_resp = client.delete(f"/api/tests/{exam['id']}")
    assert del_resp.status_code == 200

    # Verify not found
    get_resp = client.get(f"/api/tests/{exam['id']}")
    assert get_resp.status_code == 404


def test_cannot_delete_test_with_existing_attempts(client: TestClient, session: Session):
    t = create_user(session, "teacher1@test.edu", UserRole.teacher)
    s = create_user(session, "student1@test.edu", UserRole.student)

    client.post("/api/auth/login", json={"email": "teacher1@test.edu", "password": "Password123!"})
    exam = client.post("/api/tests/", json=valid_exam_payload("Exam With Attempt")).json()

    # Create an attempt directly in DB
    now = datetime.now(timezone.utc)
    attempt = Attempt(
        test_id=exam["id"],
        student_id=s.id,
        status=AttemptStatus.submitted,
        started_at=now,
        submitted_at=now,
        time_limit_ends_at=now + timedelta(minutes=45),
        identity_verified=True,
    )
    session.add(attempt)
    session.commit()

    # Teacher tries to delete test
    del_resp = client.delete(f"/api/tests/{exam['id']}")
    assert del_resp.status_code == 400
    assert "attempts" in del_resp.json()["detail"].lower()
