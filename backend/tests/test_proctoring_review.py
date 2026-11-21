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
from app.modules.auth.router import _reset_rate_limit_state, _set_rate_limit_enabled
from app.modules.proctoring.service import rate_limiter


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
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


def create_user(session, email, role):
    u = User(full_name=f"User {email}", email=email, hashed_password=hash_password("Password123!"), role=role, is_active=True)
    session.add(u); session.commit(); session.refresh(u); return u


def login(client, email):
    client.post("/api/auth/login", json={"email": email, "password": "Password123!"})


def setup_attempt(session, teacher, student):
    test = Test(title="T", description="d", duration_minutes=30, total_marks=10, status=TestStatus.active, test_code="PX", created_by=teacher.id)
    session.add(test); session.commit(); session.refresh(test)
    att = Attempt(student_id=student.id, test_id=test.id, status=AttemptStatus.in_progress, started_at=datetime.now(timezone.utc), time_limit_ends_at=datetime.now(timezone.utc)+timedelta(minutes=30), created_at=datetime.now(timezone.utc))
    session.add(att); session.commit(); session.refresh(att)
    ev = ProctoringEvent(attempt_id=att.id, event_type=EventType.looking_away, severity="low", timestamp=datetime.now(timezone.utc), review_status=ReviewStatus.unreviewed)
    session.add(ev); session.commit(); session.refresh(ev)
    return test, att, ev


def test_review_update_success(client, session):
    t = create_user(session, "t@test.edu", UserRole.teacher)
    s = create_user(session, "s@test.edu", UserRole.student)
    test, att, ev = setup_attempt(session, t, s)
    login(client, "t@test.edu")
    r = client.put(f"/api/proctoring/attempts/{att.id}/events/{ev.id}", json={"review_status": "reviewed", "reviewer_notes": "ok"})
    assert r.status_code == 200
    data = r.json()
    assert data["review_status"] == "reviewed"
    assert data["reviewer_notes"] == "ok"
    assert data["reviewer_id"] == t.id
    assert data["reviewed_at"] is not None


def test_review_status_validation(client, session):
    t = create_user(session, "t@test.edu", UserRole.teacher)
    s = create_user(session, "s@test.edu", UserRole.student)
    test, att, ev = setup_attempt(session, t, s)
    login(client, "t@test.edu")
    r = client.put(f"/api/proctoring/attempts/{att.id}/events/{ev.id}", json={"review_status": "bogus", "reviewer_notes": None})
    assert r.status_code == 422


def test_reviewer_notes_persistence(client, session):
    t = create_user(session, "t@test.edu", UserRole.teacher)
    s = create_user(session, "s@test.edu", UserRole.student)
    test, att, ev = setup_attempt(session, t, s)
    login(client, "t@test.edu")
    client.put(f"/api/proctoring/attempts/{att.id}/events/{ev.id}", json={"review_status": "no_concern", "reviewer_notes": "fine"})
    r = client.get(f"/api/proctoring/attempts/{att.id}/events")
    assert r.status_code == 200
    assert r.json()[0]["reviewer_notes"] == "fine"
    assert r.json()[0]["review_status"] == "no_concern"


def test_teacher_cannot_review_other_teacher(client, session):
    t1 = create_user(session, "t1@test.edu", UserRole.teacher)
    t2 = create_user(session, "t2@test.edu", UserRole.teacher)
    s = create_user(session, "s@test.edu", UserRole.student)
    test, att, ev = setup_attempt(session, t1, s)
    login(client, "t2@test.edu")
    r = client.put(f"/api/proctoring/attempts/{att.id}/events/{ev.id}", json={"review_status": "reviewed", "reviewer_notes": None})
    assert r.status_code == 403


def test_admin_can_review(client, session):
    t = create_user(session, "t@test.edu", UserRole.teacher)
    admin = create_user(session, "a@test.edu", UserRole.admin)
    s = create_user(session, "s@test.edu", UserRole.student)
    test, att, ev = setup_attempt(session, t, s)
    login(client, "a@test.edu")
    r = client.put(f"/api/proctoring/attempts/{att.id}/events/{ev.id}", json={"review_status": "reviewed", "reviewer_notes": None})
    assert r.status_code == 200


def test_student_cannot_review(client, session):
    t = create_user(session, "t@test.edu", UserRole.teacher)
    s = create_user(session, "s@test.edu", UserRole.student)
    test, att, ev = setup_attempt(session, t, s)
    login(client, "s@test.edu")
    r = client.put(f"/api/proctoring/attempts/{att.id}/events/{ev.id}", json={"review_status": "reviewed", "reviewer_notes": None})
    assert r.status_code in (403, 401)


def test_event_belongs_to_another_attempt(client, session):
    t = create_user(session, "t@test.edu", UserRole.teacher)
    s = create_user(session, "s@test.edu", UserRole.student)
    test, att, ev = setup_attempt(session, t, s)
    # create second attempt + event
    s2 = create_user(session, "s2@test.edu", UserRole.student)
    att2 = Attempt(student_id=s2.id, test_id=test.id, status=AttemptStatus.in_progress, started_at=datetime.now(timezone.utc), time_limit_ends_at=datetime.now(timezone.utc)+timedelta(minutes=30), created_at=datetime.now(timezone.utc))
    session.add(att2); session.commit(); session.refresh(att2)
    login(client, "t@test.edu")
    r = client.put(f"/api/proctoring/attempts/{att2.id}/events/{ev.id}", json={"review_status": "reviewed", "reviewer_notes": None})
    assert r.status_code == 404


def test_nonexistent_event(client, session):
    t = create_user(session, "t@test.edu", UserRole.teacher)
    s = create_user(session, "s@test.edu", UserRole.student)
    test, att, ev = setup_attempt(session, t, s)
    login(client, "t@test.edu")
    r = client.put(f"/api/proctoring/attempts/{att.id}/events/99999", json={"review_status": "reviewed", "reviewer_notes": None})
    assert r.status_code == 404


def test_empty_and_max_notes(client, session):
    t = create_user(session, "t@test.edu", UserRole.teacher)
    s = create_user(session, "s@test.edu", UserRole.student)
    test, att, ev = setup_attempt(session, t, s)
    login(client, "t@test.edu")
    r = client.put(f"/api/proctoring/attempts/{att.id}/events/{ev.id}", json={"review_status": "reviewed", "reviewer_notes": ""})
    assert r.status_code == 200
    assert r.json()["reviewer_notes"] in (None, "")
    # max length
    long_note = "x" * 2000
    r2 = client.put(f"/api/proctoring/attempts/{att.id}/events/{ev.id}", json={"review_status": "reviewed", "reviewer_notes": long_note})
    assert r2.status_code == 200
    r3 = client.put(f"/api/proctoring/attempts/{att.id}/events/{ev.id}", json={"review_status": "reviewed", "reviewer_notes": "x" * 2001})
    assert r3.status_code == 422

# ---------------------------------------------------------------------------
# Audit trail tests
# ---------------------------------------------------------------------------

def test_audit_first_review(client, session):
    from app.models.proctoring_event import ProctoringReviewAudit
    t = create_user(session, "t@test.edu", UserRole.teacher)
    s = create_user(session, "s@test.edu", UserRole.student)
    test, att, ev = setup_attempt(session, t, s)
    login(client, "t@test.edu")
    r = client.put(f"/api/proctoring/attempts/{att.id}/events/{ev.id}", json={"review_status": "reviewed", "reviewer_notes": "first"})
    assert r.status_code == 200
    audits = session.exec(select(ProctoringReviewAudit).where(ProctoringReviewAudit.proctoring_event_id == ev.id)).all()
    assert len(audits) == 1
    a = audits[0]
    assert a.previous_review_status == ReviewStatus.unreviewed
    assert a.new_review_status == ReviewStatus.reviewed
    assert a.previous_reviewer_notes is None
    assert a.new_reviewer_notes == "first"
    assert a.reviewer_id == t.id
    assert a.reviewed_at is not None


def test_audit_second_review_appends(client, session):
    from app.models.proctoring_event import ProctoringReviewAudit
    t = create_user(session, "t@test.edu", UserRole.teacher)
    s = create_user(session, "s@test.edu", UserRole.student)
    test, att, ev = setup_attempt(session, t, s)
    login(client, "t@test.edu")
    client.put(f"/api/proctoring/attempts/{att.id}/events/{ev.id}", json={"review_status": "reviewed", "reviewer_notes": "first"})
    client.put(f"/api/proctoring/attempts/{att.id}/events/{ev.id}", json={"review_status": "no_concern", "reviewer_notes": "second"})
    audits = session.exec(select(ProctoringReviewAudit).where(ProctoringReviewAudit.proctoring_event_id == ev.id).order_by(ProctoringReviewAudit.id)).all()
    assert len(audits) == 2
    assert audits[0].new_review_status == ReviewStatus.reviewed
    assert audits[1].previous_review_status == ReviewStatus.reviewed
    assert audits[1].new_review_status == ReviewStatus.no_concern
    assert audits[1].previous_reviewer_notes == "first"
    assert audits[1].new_reviewer_notes == "second"


def test_audit_clear_notes(client, session):
    from app.models.proctoring_event import ProctoringReviewAudit
    t = create_user(session, "t@test.edu", UserRole.teacher)
    s = create_user(session, "s@test.edu", UserRole.student)
    test, att, ev = setup_attempt(session, t, s)
    login(client, "t@test.edu")
    client.put(f"/api/proctoring/attempts/{att.id}/events/{ev.id}", json={"review_status": "reviewed", "reviewer_notes": "note"})
    client.put(f"/api/proctoring/attempts/{att.id}/events/{ev.id}", json={"review_status": "reviewed", "reviewer_notes": None})
    audits = session.exec(select(ProctoringReviewAudit).where(ProctoringReviewAudit.proctoring_event_id == ev.id).order_by(ProctoringReviewAudit.id)).all()
    assert audits[-1].new_reviewer_notes is None


def test_audit_same_status_creates_record(client, session):
    from app.models.proctoring_event import ProctoringReviewAudit
    t = create_user(session, "t@test.edu", UserRole.teacher)
    s = create_user(session, "s@test.edu", UserRole.student)
    test, att, ev = setup_attempt(session, t, s)
    login(client, "t@test.edu")
    client.put(f"/api/proctoring/attempts/{att.id}/events/{ev.id}", json={"review_status": "reviewed", "reviewer_notes": None})
    before = session.exec(select(ProctoringReviewAudit).where(ProctoringReviewAudit.proctoring_event_id == ev.id)).all()
    client.put(f"/api/proctoring/attempts/{att.id}/events/{ev.id}", json={"review_status": "reviewed", "reviewer_notes": None})
    after = session.exec(select(ProctoringReviewAudit).where(ProctoringReviewAudit.proctoring_event_id == ev.id)).all()
    assert len(after) == len(before) + 1


def test_audit_no_record_on_forbidden(client, session):
    from app.models.proctoring_event import ProctoringReviewAudit
    t1 = create_user(session, "t1@test.edu", UserRole.teacher)
    t2 = create_user(session, "t2@test.edu", UserRole.teacher)
    s = create_user(session, "s@test.edu", UserRole.student)
    test, att, ev = setup_attempt(session, t1, s)
    login(client, "t2@test.edu")
    r = client.put(f"/api/proctoring/attempts/{att.id}/events/{ev.id}", json={"review_status": "reviewed", "reviewer_notes": None})
    assert r.status_code == 403
    audits = session.exec(select(ProctoringReviewAudit).where(ProctoringReviewAudit.proctoring_event_id == ev.id)).all()
    assert len(audits) == 0


def test_audit_no_record_on_not_found(client, session):
    from app.models.proctoring_event import ProctoringReviewAudit
    t = create_user(session, "t@test.edu", UserRole.teacher)
    s = create_user(session, "s@test.edu", UserRole.student)
    test, att, ev = setup_attempt(session, t, s)
    login(client, "t@test.edu")
    r = client.put(f"/api/proctoring/attempts/{att.id}/events/99999", json={"review_status": "reviewed", "reviewer_notes": None})
    assert r.status_code == 404
    audits = session.exec(select(ProctoringReviewAudit).where(ProctoringReviewAudit.proctoring_event_id == ev.id)).all()
    assert len(audits) == 0

def test_audit_rollback_on_commit_failure(client, session, monkeypatch):
    from app.models.proctoring_event import ProctoringReviewAudit
    t = create_user(session, "t@test.edu", UserRole.teacher)
    s = create_user(session, "s@test.edu", UserRole.student)
    test, att, ev = setup_attempt(session, t, s)
    login(client, "t@test.edu")

    original_commit = session.commit
    def failing_commit():
        raise RuntimeError("simulated commit failure")
    monkeypatch.setattr(session, "commit", failing_commit)

    try:
        r = client.put(f"/api/proctoring/attempts/{att.id}/events/{ev.id}", json={"review_status": "reviewed", "reviewer_notes": "x"})
    except RuntimeError:
        pass

    # restore
    monkeypatch.setattr(session, "commit", original_commit)

    # event unchanged
    session.refresh(ev)
    assert ev.review_status == ReviewStatus.unreviewed
    assert ev.reviewer_notes is None
    audits = session.exec(select(ProctoringReviewAudit).where(ProctoringReviewAudit.proctoring_event_id == ev.id)).all()
    assert len(audits) == 0


def test_audit_unauthenticated(client, session):
    from app.models.proctoring_event import ProctoringReviewAudit
    t = create_user(session, "t@test.edu", UserRole.teacher)
    s = create_user(session, "s@test.edu", UserRole.student)
    test, att, ev = setup_attempt(session, t, s)
    r = client.put(f"/api/proctoring/attempts/{att.id}/events/{ev.id}", json={"review_status": "reviewed", "reviewer_notes": None})
    assert r.status_code in (401, 403)
    audits = session.exec(select(ProctoringReviewAudit).where(ProctoringReviewAudit.proctoring_event_id == ev.id)).all()
    assert len(audits) == 0

# ---------------------------------------------------------------------------
# Audit history GET tests
# ---------------------------------------------------------------------------

def test_audit_history_get_authorized(client, session):
    t = create_user(session, "t@test.edu", UserRole.teacher)
    s = create_user(session, "s@test.edu", UserRole.student)
    test, att, ev = setup_attempt(session, t, s)
    login(client, "t@test.edu")
    client.put(f"/api/proctoring/attempts/{att.id}/events/{ev.id}", json={"review_status": "reviewed", "reviewer_notes": "n"})
    r = client.get(f"/api/proctoring/attempts/{att.id}/events/{ev.id}/audit")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["reviewer_id"] == t.id
    assert data[0]["new_review_status"] == "reviewed"


def test_audit_history_chronological(client, session):
    t = create_user(session, "t@test.edu", UserRole.teacher)
    s = create_user(session, "s@test.edu", UserRole.student)
    test, att, ev = setup_attempt(session, t, s)
    login(client, "t@test.edu")
    client.put(f"/api/proctoring/attempts/{att.id}/events/{ev.id}", json={"review_status": "reviewed", "reviewer_notes": None})
    client.put(f"/api/proctoring/attempts/{att.id}/events/{ev.id}", json={"review_status": "no_concern", "reviewer_notes": "x"})
    r = client.get(f"/api/proctoring/attempts/{att.id}/events/{ev.id}/audit")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    assert data[0]["new_review_status"] == "reviewed"
    assert data[1]["new_review_status"] == "no_concern"


def test_audit_history_empty(client, session):
    t = create_user(session, "t@test.edu", UserRole.teacher)
    s = create_user(session, "s@test.edu", UserRole.student)
    test, att, ev = setup_attempt(session, t, s)
    login(client, "t@test.edu")
    r = client.get(f"/api/proctoring/attempts/{att.id}/events/{ev.id}/audit")
    assert r.status_code == 200
    assert r.json() == []


def test_audit_history_unauthorized(client, session):
    t = create_user(session, "t@test.edu", UserRole.teacher)
    s = create_user(session, "s@test.edu", UserRole.student)
    test, att, ev = setup_attempt(session, t, s)
    r = client.get(f"/api/proctoring/attempts/{att.id}/events/{ev.id}/audit")
    assert r.status_code in (401, 403)


def test_audit_history_other_teacher(client, session):
    t1 = create_user(session, "t1@test.edu", UserRole.teacher)
    t2 = create_user(session, "t2@test.edu", UserRole.teacher)
    s = create_user(session, "s@test.edu", UserRole.student)
    test, att, ev = setup_attempt(session, t1, s)
    login(client, "t2@test.edu")
    r = client.get(f"/api/proctoring/attempts/{att.id}/events/{ev.id}/audit")
    assert r.status_code == 403


def test_audit_history_event_other_attempt(client, session):
    t = create_user(session, "t@test.edu", UserRole.teacher)
    s = create_user(session, "s@test.edu", UserRole.student)
    s2 = create_user(session, "s2@test.edu", UserRole.student)
    test, att, ev = setup_attempt(session, t, s)
    att2 = Attempt(student_id=s2.id, test_id=test.id, status=AttemptStatus.in_progress, started_at=datetime.now(timezone.utc), time_limit_ends_at=datetime.now(timezone.utc)+timedelta(minutes=30), created_at=datetime.now(timezone.utc))
    session.add(att2); session.commit(); session.refresh(att2)
    login(client, "t@test.edu")
    r = client.get(f"/api/proctoring/attempts/{att2.id}/events/{ev.id}/audit")
    assert r.status_code == 404


def test_audit_history_admin(client, session):
    t = create_user(session, "t@test.edu", UserRole.teacher)
    admin = create_user(session, "a@test.edu", UserRole.admin)
    s = create_user(session, "s@test.edu", UserRole.student)
    test, att, ev = setup_attempt(session, t, s)
    login(client, "t@test.edu")
    client.put(f"/api/proctoring/attempts/{att.id}/events/{ev.id}", json={"review_status": "reviewed", "reviewer_notes": None})
    login(client, "a@test.edu")
    r = client.get(f"/api/proctoring/attempts/{att.id}/events/{ev.id}/audit")
    assert r.status_code == 200
    assert len(r.json()) == 1
