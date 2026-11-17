"""
Tests for Phase 4.2: Backend Proctoring Event Engine.
Covers validation, ownership, attempt lifecycle gating, authoritative timestamps,
centralized severity assignment, and event flooding protection.
"""
import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")

from datetime import datetime, timedelta, timezone
import io
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.models.user import User, UserRole
from app.models.test import Test, TestStatus
from app.models.question import Question
from app.models.option import Option
from app.models.attempt import Attempt, AttemptStatus
from app.models.proctoring_event import EventType, ProctoringEvent, ReviewStatus
from app.modules.auth.service import hash_password
from app.modules.auth.router import _reset_rate_limit_state, _set_rate_limit_enabled
from app.modules.proctoring.service import rate_limiter


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


@pytest.fixture(autouse=True)
def reset_rate_limit_fixture():
    _set_rate_limit_enabled(False)
    _reset_rate_limit_state()
    rate_limiter.reset()
    yield
    _set_rate_limit_enabled(False)
    _reset_rate_limit_state()
    rate_limiter.reset()


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
        description="Active test description",
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


def create_attempt(
    session: Session,
    student_id: int,
    test_id: int,
    status: AttemptStatus = AttemptStatus.in_progress,
    started_at: datetime | None = None,
    time_limit_ends_at: datetime | None = None,
) -> Attempt:
    now = datetime.now(timezone.utc)
    if started_at is None and status == AttemptStatus.in_progress:
        started_at = now
    if time_limit_ends_at is None and status == AttemptStatus.in_progress:
        time_limit_ends_at = now + timedelta(minutes=30)

    attempt = Attempt(
        student_id=student_id,
        test_id=test_id,
        status=status,
        started_at=started_at,
        time_limit_ends_at=time_limit_ends_at,
        created_at=now,
    )
    session.add(attempt)
    session.commit()
    session.refresh(attempt)
    return attempt


def login_user(client: TestClient, email: str, password: str = "Password123!"):
    client.post("/api/auth/login", json={"email": email, "password": password})

MINIMAL_JPEG = bytes.fromhex('ffd8ffe000104a46494600010100000100010000ffd9')

def submit_identity_photo(client: TestClient, attempt_id: int, content: bytes = MINIMAL_JPEG, filename: str = 'photo.jpg', content_type: str = 'image/jpeg'):
    return client.post(
        f'/api/student/attempts/{attempt_id}/identity-verification',
        files={'photo': (filename, io.BytesIO(content), content_type)},
    )



# ---------------------------------------------------------------------------
# 1. Valid Event Creation
# ---------------------------------------------------------------------------

def test_valid_event_creation(client: TestClient, session: Session):
    teacher = create_user(session, "teacher1@test.edu", UserRole.teacher)
    student = create_user(session, "student1@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABC01", teacher.id)
    attempt = create_attempt(session, student.id, test.id, AttemptStatus.in_progress)

    login_user(client, "student1@test.edu")

    payload = {
        "event_type": "face_not_detected",
        "description": "Student face not in frame for 4 seconds",
        "duration_seconds": 4.0,
    }

    response = client.post(
        f"/api/student/attempts/{attempt.id}/proctoring-events",
        json=payload,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["attempt_id"] == attempt.id
    assert data["event_type"] == "face_not_detected"
    assert data["severity"] == "medium"  # Authoritative severity assigned by backend
    assert data["review_status"] == "unreviewed"
    assert data["description"] == "Student face not in frame for 4 seconds"
    assert data["duration_seconds"] == 4.0
    assert "timestamp" in data


# ---------------------------------------------------------------------------
# 2. Unauthenticated Request
# ---------------------------------------------------------------------------

def test_unauthenticated_request(client: TestClient, session: Session):
    teacher = create_user(session, "teacher2@test.edu", UserRole.teacher)
    student = create_user(session, "student2@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABC02", teacher.id)
    attempt = create_attempt(session, student.id, test.id, AttemptStatus.in_progress)

    # Do not login
    response = client.post(
        f"/api/student/attempts/{attempt.id}/proctoring-events",
        json={"event_type": "fullscreen_exited"},
    )
    assert response.status_code == 401
    assert "not authenticated" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# 3. Non-Student Role
# ---------------------------------------------------------------------------

def test_non_student_role_rejected(client: TestClient, session: Session):
    teacher = create_user(session, "teacher3@test.edu", UserRole.teacher)
    student = create_user(session, "student3@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABC03", teacher.id)
    attempt = create_attempt(session, student.id, test.id, AttemptStatus.in_progress)

    # Login as teacher
    login_user(client, "teacher3@test.edu")

    response = client.post(
        f"/api/student/attempts/{attempt.id}/proctoring-events",
        json={"event_type": "fullscreen_exited"},
    )
    assert response.status_code == 403
    assert "insufficient permissions" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# 4. Attempt Belonging to Another Student
# ---------------------------------------------------------------------------

def test_attempt_belonging_to_another_student_rejected(client: TestClient, session: Session):
    teacher = create_user(session, "teacher4@test.edu", UserRole.teacher)
    student1 = create_user(session, "student4a@test.edu", UserRole.student)
    student2 = create_user(session, "student4b@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABC04", teacher.id)
    attempt1 = create_attempt(session, student1.id, test.id, AttemptStatus.in_progress)

    # Login as student 2 and attempt to record event on student 1's attempt
    login_user(client, "student4b@test.edu")

    response = client.post(
        f"/api/student/attempts/{attempt1.id}/proctoring-events",
        json={"event_type": "tab_visibility_changed"},
    )
    assert response.status_code == 403
    assert "do not own" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# 5. Attempt Not Found
# ---------------------------------------------------------------------------

def test_attempt_not_found(client: TestClient, session: Session):
    student = create_user(session, "student5@test.edu", UserRole.student)
    login_user(client, "student5@test.edu")

    response = client.post(
        "/api/student/attempts/999999/proctoring-events",
        json={"event_type": "looking_away"},
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# 6. Attempt in Created Status
# ---------------------------------------------------------------------------

def test_attempt_in_created_status_rejected(client: TestClient, session: Session):
    teacher = create_user(session, "teacher6@test.edu", UserRole.teacher)
    student = create_user(session, "student6@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABC06", teacher.id)
    attempt = create_attempt(session, student.id, test.id, status=AttemptStatus.created)

    login_user(client, "student6@test.edu")

    response = client.post(
        f"/api/student/attempts/{attempt.id}/proctoring-events",
        json={"event_type": "camera_disconnected"},
    )
    assert response.status_code == 409
    assert "not been started" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# 7. Attempt Already Submitted
# ---------------------------------------------------------------------------

def test_attempt_already_submitted_rejected(client: TestClient, session: Session):
    teacher = create_user(session, "teacher7@test.edu", UserRole.teacher)
    student = create_user(session, "student7@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABC07", teacher.id)
    attempt = create_attempt(session, student.id, test.id, status=AttemptStatus.submitted)

    login_user(client, "student7@test.edu")

    response = client.post(
        f"/api/student/attempts/{attempt.id}/proctoring-events",
        json={"event_type": "fullscreen_exited"},
    )
    assert response.status_code == 409
    assert "already been submitted" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# 8. Attempt Timed Out
# ---------------------------------------------------------------------------

def test_attempt_timed_out_status_rejected(client: TestClient, session: Session):
    teacher = create_user(session, "teacher8@test.edu", UserRole.teacher)
    student = create_user(session, "student8@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABC08", teacher.id)
    attempt = create_attempt(session, student.id, test.id, status=AttemptStatus.timed_out)

    login_user(client, "student8@test.edu")

    response = client.post(
        f"/api/student/attempts/{attempt.id}/proctoring-events",
        json={"event_type": "fullscreen_exited"},
    )
    assert response.status_code == 409
    assert "timed out" in response.json()["detail"].lower()


def test_attempt_with_expired_deadline_rejected(client: TestClient, session: Session):
    teacher = create_user(session, "teacher8b@test.edu", UserRole.teacher)
    student = create_user(session, "student8b@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABC8B", teacher.id)

    # Attempt started in past and deadline passed
    past_start = datetime.now(timezone.utc) - timedelta(hours=2)
    past_end = datetime.now(timezone.utc) - timedelta(hours=1)
    attempt = create_attempt(
        session,
        student.id,
        test.id,
        status=AttemptStatus.in_progress,
        started_at=past_start,
        time_limit_ends_at=past_end,
    )

    login_user(client, "student8b@test.edu")

    response = client.post(
        f"/api/student/attempts/{attempt.id}/proctoring-events",
        json={"event_type": "face_not_detected"},
    )
    assert response.status_code == 409
    assert "expired" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# 9. Invalid Event Type
# ---------------------------------------------------------------------------

def test_invalid_event_type_rejected(client: TestClient, session: Session):
    teacher = create_user(session, "teacher9@test.edu", UserRole.teacher)
    student = create_user(session, "student9@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABC09", teacher.id)
    attempt = create_attempt(session, student.id, test.id, AttemptStatus.in_progress)

    login_user(client, "student9@test.edu")

    response = client.post(
        f"/api/student/attempts/{attempt.id}/proctoring-events",
        json={"event_type": "unsupported_event_type_name"},
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# 10. Invalid Severity and Client-Supplied Reviewer Fields
# ---------------------------------------------------------------------------

def test_invalid_severity_rejected(client: TestClient, session: Session):
    teacher = create_user(session, "teacher10a@test.edu", UserRole.teacher)
    student = create_user(session, "student10a@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABC10A", teacher.id)
    attempt = create_attempt(session, student.id, test.id, AttemptStatus.in_progress)

    login_user(client, "student10a@test.edu")

    response = client.post(
        f"/api/student/attempts/{attempt.id}/proctoring-events",
        json={
            "event_type": "face_not_detected",
            "severity": "extreme",  # Invalid severity value
        },
    )
    assert response.status_code == 422


def test_client_supplied_reviewer_fields_forbidden(client: TestClient, session: Session):
    teacher = create_user(session, "teacher10b@test.edu", UserRole.teacher)
    student = create_user(session, "student10b@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABC10B", teacher.id)
    attempt = create_attempt(session, student.id, test.id, AttemptStatus.in_progress)

    login_user(client, "student10b@test.edu")

    # Attempt to inject reviewer_id
    response1 = client.post(
        f"/api/student/attempts/{attempt.id}/proctoring-events",
        json={
            "event_type": "fullscreen_exited",
            "reviewer_id": 999,
        },
    )
    assert response1.status_code == 422

    # Attempt to inject review_status
    response2 = client.post(
        f"/api/student/attempts/{attempt.id}/proctoring-events",
        json={
            "event_type": "fullscreen_exited",
            "review_status": "no_concern",
        },
    )
    assert response2.status_code == 422


def test_client_severity_does_not_override_authoritative_mapping(client: TestClient, session: Session):
    teacher = create_user(session, "teacher10c@test.edu", UserRole.teacher)
    student = create_user(session, "student10c@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABC10C", teacher.id)
    attempt = create_attempt(session, student.id, test.id, AttemptStatus.in_progress)

    login_user(client, "student10c@test.edu")

    # multiple_faces_detected has authoritative severity "high"
    # Even if client passes severity "low", backend assigns authoritative "high"
    response = client.post(
        f"/api/student/attempts/{attempt.id}/proctoring-events",
        json={
            "event_type": "multiple_faces_detected",
            "severity": "low",
        },
    )
    assert response.status_code == 201
    assert response.json()["severity"] == "high"


# ---------------------------------------------------------------------------
# 11. Event Flooding Protection
# ---------------------------------------------------------------------------

def test_event_flooding_protection(client: TestClient, session: Session):
    teacher = create_user(session, "teacher11@test.edu", UserRole.teacher)
    student = create_user(session, "student11@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABC11", teacher.id)
    attempt = create_attempt(session, student.id, test.id, AttemptStatus.in_progress)

    login_user(client, "student11@test.edu")

    payload = {"event_type": "looking_away"}

    # Default rate limit is 5 events per 10 seconds for same (attempt_id, event_type)
    for i in range(5):
        resp = client.post(
            f"/api/student/attempts/{attempt.id}/proctoring-events",
            json=payload,
        )
        assert resp.status_code == 201, f"Expected 201 on iteration {i}, got {resp.status_code}"

    # 6th immediate request must be rate limited with HTTP 429
    flood_resp = client.post(
        f"/api/student/attempts/{attempt.id}/proctoring-events",
        json=payload,
    )
    assert flood_resp.status_code == 429
    assert "too many proctoring events" in flood_resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# 12. Event Belongs to Correct Attempt
# ---------------------------------------------------------------------------

def test_event_belongs_to_correct_attempt(client: TestClient, session: Session):
    teacher = create_user(session, "teacher12@test.edu", UserRole.teacher)
    student = create_user(session, "student12@test.edu", UserRole.student)
    test1 = create_active_test(session, "Exam 1", "PXAM-ABC12A", teacher.id)
    test2 = create_active_test(session, "Exam 2", "PXAM-ABC12B", teacher.id)

    attempt1 = create_attempt(session, student.id, test1.id, AttemptStatus.in_progress)
    attempt2 = create_attempt(session, student.id, test2.id, AttemptStatus.in_progress)

    login_user(client, "student12@test.edu")

    client.post(
        f"/api/student/attempts/{attempt1.id}/proctoring-events",
        json={"event_type": "fullscreen_exited"},
    )
    client.post(
        f"/api/student/attempts/{attempt2.id}/proctoring-events",
        json={"event_type": "camera_disconnected"},
    )

    events_attempt1 = session.exec(
        select(ProctoringEvent).where(ProctoringEvent.attempt_id == attempt1.id)
    ).all()
    events_attempt2 = session.exec(
        select(ProctoringEvent).where(ProctoringEvent.attempt_id == attempt2.id)
    ).all()

    assert len(events_attempt1) == 1
    assert events_attempt1[0].event_type == EventType.fullscreen_exited

    assert len(events_attempt2) == 1
    assert events_attempt2[0].event_type == EventType.camera_disconnected


# ---------------------------------------------------------------------------
# 13. Server Timestamp is Authoritative
# ---------------------------------------------------------------------------

def test_server_timestamp_is_authoritative(client: TestClient, session: Session):
    teacher = create_user(session, "teacher13@test.edu", UserRole.teacher)
    student = create_user(session, "student13@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABC13", teacher.id)
    attempt = create_attempt(session, student.id, test.id, AttemptStatus.in_progress)

    login_user(client, "student13@test.edu")

    # Client claims an untrusted timestamp far in the past
    bogus_client_time = "2020-01-01T00:00:00Z"
    before_post = datetime.now(timezone.utc) - timedelta(seconds=2)

    response = client.post(
        f"/api/student/attempts/{attempt.id}/proctoring-events",
        json={
            "event_type": "tab_visibility_changed",
            "client_timestamp": bogus_client_time,
        },
    )

    after_post = datetime.now(timezone.utc) + timedelta(seconds=2)

    assert response.status_code == 201
    event_id = response.json()["id"]

    db_event = session.get(ProctoringEvent, event_id)
    assert db_event is not None

    # Server timestamp must be recent (within the test execution window)
    event_ts = db_event.timestamp
    if event_ts.tzinfo is None:
        event_ts = event_ts.replace(tzinfo=timezone.utc)

    assert before_post <= event_ts <= after_post
    # And definitely not 2020
    assert event_ts.year >= 2026


# ---------------------------------------------------------------------------
# 14. Existing Examination Functionality Remains Unaffected
# ---------------------------------------------------------------------------

def test_existing_examination_flow_unaffected(client: TestClient, session: Session):
    teacher = create_user(session, "teacher14@test.edu", UserRole.teacher)
    student = create_user(session, "student14@test.edu", UserRole.student)
    test = create_active_test(session, "Biology 101", "PXAM-ABC14", teacher.id)

    # Add question and options
    q = Question(test_id=test.id, question_text="What is DNA?", marks=2.0, order_index=0)
    session.add(q)
    session.commit()
    session.refresh(q)

    opt1 = Option(question_id=q.id, option_text="Protein", label="A", is_correct=False)
    opt2 = Option(question_id=q.id, option_text="Genetic Material", label="B", is_correct=True)
    opt3 = Option(question_id=q.id, option_text="Carbohydrate", label="C", is_correct=False)
    opt4 = Option(question_id=q.id, option_text="Lipid", label="D", is_correct=False)
    session.add_all([opt1, opt2, opt3, opt4])
    session.commit()

    login_user(client, "student14@test.edu")

    # Step A: Validate test code
    code_resp = client.post("/api/student/tests/validate-code", json={"test_code": "PXAM-ABC14"})
    assert code_resp.status_code == 200

    # Step B: Create attempt
    attempt_resp = client.post(f"/api/student/tests/{test.id}/attempt")
    assert attempt_resp.status_code == 201
    attempt_id = attempt_resp.json()["id"]

    # Step C: Submit identity verification and start attempt
    id_resp = submit_identity_photo(client, attempt_id)
    assert id_resp.status_code == 201
    start_resp = client.post(f"/api/student/attempts/{attempt_id}/start")
    assert start_resp.status_code == 200
    assert start_resp.json()["status"] == "in_progress"

    # Step D: Emit proctoring event during examination
    proctor_resp = client.post(
        f"/api/student/attempts/{attempt_id}/proctoring-events",
        json={"event_type": "tab_visibility_changed", "description": "Candidate switched tab"},
    )
    assert proctor_resp.status_code == 201

    # Step E: Save answer
    answer_resp = client.put(
        f"/api/student/attempts/{attempt_id}/answers/{q.id}",
        json={"selected_option_id": opt2.id, "is_marked_for_review": False},
    )
    assert answer_resp.status_code == 200

    # Step F: Submit attempt
    submit_resp = client.post(f"/api/student/attempts/{attempt_id}/submit")
    assert submit_resp.status_code == 200
    assert submit_resp.json()["status"] == "submitted"
    assert submit_resp.json()["result"]["score"] == 2.0

    # Step G: Proctoring event AFTER submission is now rejected
    after_submit_resp = client.post(
        f"/api/student/attempts/{attempt_id}/proctoring-events",
        json={"event_type": "fullscreen_exited"},
    )
    assert after_submit_resp.status_code == 409


# ---------------------------------------------------------------------------
# 15. Maximum Description Length Protection
# ---------------------------------------------------------------------------

def test_maximum_description_length_with_client_timestamp(client: TestClient, session: Session):
    teacher = create_user(session, "teacher15@test.edu", UserRole.teacher)
    student = create_user(session, "student15@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABC15", teacher.id)
    attempt = create_attempt(session, student.id, test.id, AttemptStatus.in_progress)

    login_user(client, "student15@test.edu")

    # Submit a description containing exactly 1000 characters
    exact_1000_char_desc = "x" * 1000
    client_time = "2026-11-12T15:00:00Z"

    before_post = datetime.now(timezone.utc) - timedelta(seconds=2)
    response = client.post(
        f"/api/student/attempts/{attempt.id}/proctoring-events",
        json={
            "event_type": "looking_away",
            "description": exact_1000_char_desc,
            "client_timestamp": client_time,
        },
    )
    after_post = datetime.now(timezone.utc) + timedelta(seconds=2)

    assert response.status_code == 201
    event_id = response.json()["id"]

    db_event = session.get(ProctoringEvent, event_id)
    assert db_event is not None
    assert len(db_event.description) <= 1000
    assert len(db_event.description) == 1000

    # Confirm the server timestamp remains authoritative
    event_ts = db_event.timestamp
    if event_ts.tzinfo is None:
        event_ts = event_ts.replace(tzinfo=timezone.utc)
    assert before_post <= event_ts <= after_post


# ---------------------------------------------------------------------------
# 16. Rate-Limit Category Isolation
# ---------------------------------------------------------------------------

def test_rate_limit_category_isolation(client: TestClient, session: Session):
    teacher = create_user(session, "teacher16@test.edu", UserRole.teacher)
    student = create_user(session, "student16@test.edu", UserRole.student)
    test = create_active_test(session, "Midterm Exam", "PXAM-ABC16", teacher.id)
    attempt = create_attempt(session, student.id, test.id, AttemptStatus.in_progress)

    login_user(client, "student16@test.edu")

    # 1. Exhaust allowed number of events for Category A (looking_away: 5 events)
    for _ in range(5):
        resp = client.post(
            f"/api/student/attempts/{attempt.id}/proctoring-events",
            json={"event_type": "looking_away"},
        )
        assert resp.status_code == 201

    # Confirm Category A is now rate-limited
    resp_blocked = client.post(
        f"/api/student/attempts/{attempt.id}/proctoring-events",
        json={"event_type": "looking_away"},
    )
    assert resp_blocked.status_code == 429

    # 2. Immediately submit an event of Category B (fullscreen_exited) for the same attempt
    resp_other_category = client.post(
        f"/api/student/attempts/{attempt.id}/proctoring-events",
        json={"event_type": "fullscreen_exited"},
    )
    # Confirm Category B is NOT blocked by Category A's rate limit
    assert resp_other_category.status_code == 201
    assert resp_other_category.json()["event_type"] == "fullscreen_exited"


