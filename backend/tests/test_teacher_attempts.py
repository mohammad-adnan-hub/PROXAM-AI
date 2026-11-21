import os
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")

from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.models.user import User, UserRole
from app.models.test import Test, TestStatus
from app.models.attempt import Attempt, AttemptStatus
from app.models.proctoring_event import ProctoringEvent, EventType, ReviewStatus
from app.modules.auth.service import hash_password


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


from app.modules.auth.router import _reset_rate_limit_state, _set_rate_limit_enabled
from app.modules.proctoring.service import rate_limiter


@pytest.fixture(autouse=True)
def reset_rate_limit_fixture():
    _set_rate_limit_enabled(False)
    _reset_rate_limit_state()
    rate_limiter.reset()
    yield
    _set_rate_limit_enabled(False)
    _reset_rate_limit_state()
    rate_limiter.reset()


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
    app.dependency_overrides.clear()


def create_user(session, email, role):
    u = User(full_name=f"User {email}", email=email, hashed_password=hash_password("Password123!"), role=role, is_active=True)
    session.add(u); session.commit(); session.refresh(u); return u


def login(client, email):
    client.post("/api/auth/login", json={"email": email, "password": "Password123!"})


def test_teacher_list_attempts(client, session):
    t1 = create_user(session, "t1@test.edu", UserRole.teacher)
    t2 = create_user(session, "t2@test.edu", UserRole.teacher)
    s = create_user(session, "s@test.edu", UserRole.student)
    test = Test(title="T", description="d", duration_minutes=30, total_marks=10, status=TestStatus.active, test_code="PX", created_by=t1.id)
    session.add(test); session.commit(); session.refresh(test)
    att = Attempt(student_id=s.id, test_id=test.id, status=AttemptStatus.in_progress, started_at=datetime.now(timezone.utc), time_limit_ends_at=datetime.now(timezone.utc)+timedelta(minutes=30), created_at=datetime.now(timezone.utc), warning_count=2)
    session.add(att); session.commit(); session.refresh(att)
    ev = ProctoringEvent(attempt_id=att.id, event_type=EventType.looking_away, severity="low", timestamp=datetime.now(timezone.utc), review_status=ReviewStatus.unreviewed)
    session.add(ev); session.commit()

    login(client, "t1@test.edu")
    r = client.get(f"/api/teacher/tests/{test.id}/attempts")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["attempt_id"] == att.id
    assert data[0]["warning_count"] == 2
    assert data[0]["proctoring_event_count"] == 1
    assert data[0]["latest_event_type"] == "looking_away"

    # another teacher denied
    login(client, "t2@test.edu")
    r2 = client.get(f"/api/teacher/tests/{test.id}/attempts")
    assert r2.status_code == 403

    # student denied
    login(client, "s@test.edu")
    r3 = client.get(f"/api/teacher/tests/{test.id}/attempts")
    assert r3.status_code == 403


def test_teacher_attempt_detail_and_result(client, session):
    t = create_user(session, "t@test.edu", UserRole.teacher)
    s = create_user(session, "s@test.edu", UserRole.student)
    test = Test(title="T", description="d", duration_minutes=30, total_marks=10, status=TestStatus.active, test_code="PX2", created_by=t.id)
    session.add(test); session.commit(); session.refresh(test)
    att = Attempt(student_id=s.id, test_id=test.id, status=AttemptStatus.terminated_by_warnings, started_at=datetime.now(timezone.utc), submitted_at=datetime.now(timezone.utc), created_at=datetime.now(timezone.utc), warning_count=4, identity_verified=True)
    session.add(att); session.commit(); session.refresh(att)

    login(client, "t@test.edu")
    r = client.get(f"/api/teacher/attempts/{att.id}")
    assert r.status_code == 200
    assert r.json()["status"] == "terminated_by_warnings"
    assert r.json()["warning_count"] == 4

    r2 = client.get(f"/api/teacher/attempts/{att.id}/result")
    assert r2.status_code == 200
    assert r2.json()["status"] == "terminated_by_warnings"


def test_admin_access_and_empty_list(client, session):
    t = create_user(session, "t@test.edu", UserRole.teacher)
    admin = create_user(session, "a@test.edu", UserRole.admin)
    test = Test(title="T", description="d", duration_minutes=30, total_marks=10, status=TestStatus.active, test_code="PX3", created_by=t.id)
    session.add(test); session.commit(); session.refresh(test)

    login(client, "a@test.edu")
    r = client.get(f"/api/teacher/tests/{test.id}/attempts")
    assert r.status_code == 200
    assert r.json() == []

    # nonexistent
    r2 = client.get("/api/teacher/tests/99999/attempts")
    assert r2.status_code == 404
    r3 = client.get("/api/teacher/attempts/99999")
    assert r3.status_code == 404


def test_missing_result_deliberate(client, session):
    t = create_user(session, "t@test.edu", UserRole.teacher)
    s = create_user(session, "s@test.edu", UserRole.student)
    test = Test(title="T", description="d", duration_minutes=30, total_marks=10, status=TestStatus.active, test_code="PX4", created_by=t.id)
    session.add(test); session.commit(); session.refresh(test)
    att = Attempt(student_id=s.id, test_id=test.id, status=AttemptStatus.in_progress, started_at=datetime.now(timezone.utc), created_at=datetime.now(timezone.utc))
    session.add(att); session.commit(); session.refresh(att)

    login(client, "t@test.edu")
    r = client.get(f"/api/teacher/attempts/{att.id}/result")
    assert r.status_code == 200
    data = r.json()
    assert data["score"] is None
    assert data["total_marks"] is None
