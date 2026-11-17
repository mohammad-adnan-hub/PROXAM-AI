"""
Tests for Phase 5.7: Manual Identity Verification.
Covers secure submission/status, validation, ownership, lifecycle, privacy constraints,
storage/DB consistency, and exam start-gating behavior.
"""
import io
import os
from datetime import datetime, timezone

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.main import app
from app.models.attempt import Attempt, AttemptStatus
from app.models.identity_verification import AttemptIdentityVerification, IdentityVerificationStatus
from app.models.test import Test, TestStatus
from app.models.user import User, UserRole
from app.modules.auth.router import _reset_rate_limit_state, _set_rate_limit_enabled
from app.modules.auth.service import hash_password

# Valid minimal images (strict validation requires decodable, well-formed PNG/JPEG).
MINIMAL_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010802000000907753de"
    "0000000c49444154789c63606060000000040001f61738550000000049454e44ae426082"
)

try:
    from PIL import Image  # type: ignore

    _buf = io.BytesIO()
    Image.new("RGB", (1, 1), (255, 0, 0)).save(_buf, format="JPEG")
    MINIMAL_JPEG = _buf.getvalue()
except Exception:  # pragma: no cover - fallback when Pillow unavailable
    MINIMAL_JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\x7f\x00\xff\xd9"


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
    yield
    _set_rate_limit_enabled(False)
    _reset_rate_limit_state()


def create_user(session: Session, email: str, role: UserRole, full_name: str | None = None) -> User:
    user = User(
        full_name=full_name or f"User {email}",
        email=email,
        hashed_password=hash_password("Password123!"),
        role=role,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_test(session: Session, title: str, code: str, created_by: int, status: TestStatus = TestStatus.active) -> Test:
    test = Test(
        title=title,
        description="Test description",
        duration_minutes=30,
        total_marks=10.0,
        status=status,
        test_code=code,
        created_by=created_by,
    )
    session.add(test)
    session.commit()
    session.refresh(test)
    return test


def login(client: TestClient, email: str, password: str = "Password123!"):
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp


def create_attempt_via_api(client: TestClient, test_id: int) -> int:
    resp = client.post(f"/api/student/tests/{test_id}/attempt")
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def submit_identity(client: TestClient, attempt_id: int, content: bytes = MINIMAL_JPEG, filename: str = "photo.jpg", content_type: str = "image/jpeg"):
    return client.post(
        f"/api/student/attempts/{attempt_id}/identity-verification",
        files={"photo": (filename, io.BytesIO(content), content_type)},
    )


# ---------------------------------------------------------------------------
# Successful submission and status
# ---------------------------------------------------------------------------

def test_submit_identity_jpeg_success_sets_pending(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    student = create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID001", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)

    resp = submit_identity(client, attempt_id, MINIMAL_JPEG, "photo.jpg", "image/jpeg")
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["attempt_id"] == attempt_id
    assert data["status"] == "pending"
    assert data["submitted_at"] is not None
    assert data["can_start_examination"] is True

    record = session.exec(select(AttemptIdentityVerification).where(AttemptIdentityVerification.attempt_id == attempt_id)).first()
    assert record is not None
    assert record.status == IdentityVerificationStatus.pending
    assert record.student_id == student.id
    assert record.image_path is not None
    assert record.content_type == "image/jpeg"
    assert record.file_size_bytes == len(MINIMAL_JPEG)
    assert record.reviewer_id is None
    assert record.reviewed_at is None
    assert record.reviewer_notes is None

    attempt = session.get(Attempt, attempt_id)
    assert attempt.identity_verified is False  # never auto-verified


def test_submit_identity_png_success_sets_pending(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID002", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)
    resp = submit_identity(client, attempt_id, MINIMAL_PNG, "photo.png", "image/png")
    assert resp.status_code == 201, resp.text
    assert resp.json()["status"] == "pending"


def test_get_identity_status_not_submitted(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID003", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)

    resp = client.get(f"/api/student/attempts/{attempt_id}/identity-verification")
    assert resp.status_code == 200
    data = resp.json()
    assert data["attempt_id"] == attempt_id
    assert data["status"] == "not_submitted"
    assert data["submitted_at"] is None
    assert data["can_start_examination"] is False
    assert "image_path" not in data
    assert "storage" not in str(data).lower()


def test_get_identity_status_after_submission(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID004", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)
    assert submit_identity(client, attempt_id).status_code == 201

    resp = client.get(f"/api/student/attempts/{attempt_id}/identity-verification")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "pending"
    assert data["submitted_at"] is not None
    assert data["can_start_examination"] is True


# ---------------------------------------------------------------------------
# Validation failures
# ---------------------------------------------------------------------------

def test_submit_identity_invalid_extension_rejected(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID005", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)
    resp = submit_identity(client, attempt_id, MINIMAL_JPEG, "photo.txt", "image/jpeg")
    assert resp.status_code == 400


def test_submit_identity_invalid_mime_type_rejected(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID006", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)
    resp = submit_identity(client, attempt_id, MINIMAL_JPEG, "photo.jpg", "text/plain")
    assert resp.status_code == 400


def test_submit_identity_invalid_signature_rejected(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID007", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)
    resp = submit_identity(client, attempt_id, b"not-an-image-at-all", "photo.jpg", "image/jpeg")
    assert resp.status_code == 400


def test_submit_identity_oversized_rejected(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID008", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)
    big = MINIMAL_JPEG + b"\x00" * (5 * 1024 * 1024 + 1)
    resp = submit_identity(client, attempt_id, big, "photo.jpg", "image/jpeg")
    assert resp.status_code == 400
    assert "size" in resp.json()["detail"].lower() or "exceed" in resp.json()["detail"].lower() or "5" in resp.json()["detail"]


def test_submit_identity_malformed_image_rejected(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID009", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)
    malformed = b"\xff\xd8\xff\xe0broken-not-a-jpeg"
    resp = submit_identity(client, attempt_id, malformed, "photo.jpg", "image/jpeg")
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Auth / ownership / isolation
# ---------------------------------------------------------------------------

def test_submit_identity_unauthenticated(client: TestClient, session: Session):
    resp = client.post("/api/student/attempts/1/identity-verification", files={"photo": ("p.jpg", io.BytesIO(MINIMAL_JPEG), "image/jpeg")})
    assert resp.status_code == 401


def test_get_identity_unauthenticated(client: TestClient, session: Session):
    resp = client.get("/api/student/attempts/1/identity-verification")
    assert resp.status_code == 401


def test_cross_student_upload_rejected(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    create_user(session, "s1@test.edu", UserRole.student)
    create_user(session, "s2@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID010", teacher.id)
    login(client, "s1@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)
    login(client, "s2@test.edu")
    resp = submit_identity(client, attempt_id)
    assert resp.status_code == 403


def test_cross_student_status_access_rejected(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    create_user(session, "s1@test.edu", UserRole.student)
    create_user(session, "s2@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID011", teacher.id)
    login(client, "s1@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)
    submit_identity(client, attempt_id)
    login(client, "s2@test.edu")
    resp = client.get(f"/api/student/attempts/{attempt_id}/identity-verification")
    assert resp.status_code == 403


def test_teacher_access_to_student_identity_endpoints_rejected(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    student = create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID012", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)
    submit_identity(client, attempt_id)
    login(client, "teacher@test.edu")
    assert submit_identity(client, attempt_id).status_code == 403
    assert client.get(f"/api/student/attempts/{attempt_id}/identity-verification").status_code == 403


# ---------------------------------------------------------------------------
# Lifecycle / duplicate / resubmission
# ---------------------------------------------------------------------------

def test_duplicate_pending_upload_rejected(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID013", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)
    assert submit_identity(client, attempt_id).status_code == 201
    resp = submit_identity(client, attempt_id)
    assert resp.status_code == 409


def test_duplicate_verified_upload_rejected(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID014", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)
    assert submit_identity(client, attempt_id).status_code == 201
    record = session.exec(select(AttemptIdentityVerification).where(AttemptIdentityVerification.attempt_id == attempt_id)).first()
    record.status = IdentityVerificationStatus.verified
    record.reviewed_at = datetime.now(timezone.utc)
    session.add(record)
    session.commit()
    resp = submit_identity(client, attempt_id)
    assert resp.status_code == 409


def test_rejected_photo_resubmission_allowed_returns_pending(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    student = create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID015", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)
    assert submit_identity(client, attempt_id).status_code == 201
    record = session.exec(select(AttemptIdentityVerification).where(AttemptIdentityVerification.attempt_id == attempt_id)).first()
    record.status = IdentityVerificationStatus.rejected
    record.reviewer_id = teacher.id
    record.reviewed_at = datetime.now(timezone.utc)
    record.reviewer_notes = "Blurry"
    session.add(record)
    session.commit()

    resp = submit_identity(client, attempt_id, MINIMAL_PNG, "retake.png", "image/png")
    assert resp.status_code == 201, resp.text
    assert resp.json()["status"] == "pending"

    session.refresh(record)
    assert record.status == IdentityVerificationStatus.pending
    assert record.reviewer_id is None
    assert record.reviewed_at is None
    assert record.reviewer_notes is None
    assert record.content_type == "image/png"
    assert record.student_id == student.id


def test_student_cannot_change_reviewer_fields_via_student_endpoints(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID016", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)
    # Attempt to smuggle reviewer fields in multipart form should be ignored; submission still pending.
    resp = client.post(
        f"/api/student/attempts/{attempt_id}/identity-verification",
        files={"photo": ("photo.jpg", io.BytesIO(MINIMAL_JPEG), "image/jpeg")},
        data={"status": "verified", "reviewer_id": "999", "reviewer_notes": "ok"},
    )
    assert resp.status_code == 201
    record = session.exec(select(AttemptIdentityVerification).where(AttemptIdentityVerification.attempt_id == attempt_id)).first()
    assert record.status == IdentityVerificationStatus.pending
    assert record.reviewer_id is None
    assert record.reviewed_at is None
    assert record.reviewer_notes is None
    attempt = session.get(Attempt, attempt_id)
    assert attempt.identity_verified is False


def test_submit_identity_finalized_attempt_rejected(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID017", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)
    attempt = session.get(Attempt, attempt_id)
    attempt.status = AttemptStatus.submitted
    attempt.submitted_at = datetime.now(timezone.utc)
    session.add(attempt)
    session.commit()
    assert submit_identity(client, attempt_id).status_code == 409


# ---------------------------------------------------------------------------
# Start gating
# ---------------------------------------------------------------------------

def test_start_without_identity_photo_rejected(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID018", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)
    resp = client.post(f"/api/student/attempts/{attempt_id}/start")
    assert resp.status_code == 409
    assert "identity" in resp.json()["detail"].lower()


def test_start_with_pending_photo_allowed(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID019", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)
    assert submit_identity(client, attempt_id).status_code == 201
    resp = client.post(f"/api/student/attempts/{attempt_id}/start")
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"


def test_start_with_verified_photo_allowed(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID020", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)
    assert submit_identity(client, attempt_id).status_code == 201
    record = session.exec(select(AttemptIdentityVerification).where(AttemptIdentityVerification.attempt_id == attempt_id)).first()
    record.status = IdentityVerificationStatus.verified
    record.reviewed_at = datetime.now(timezone.utc)
    session.add(record)
    session.commit()
    resp = client.post(f"/api/student/attempts/{attempt_id}/start")
    assert resp.status_code == 200


def test_start_with_rejected_photo_blocked_until_resubmission(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID021", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)
    assert submit_identity(client, attempt_id).status_code == 201
    record = session.exec(select(AttemptIdentityVerification).where(AttemptIdentityVerification.attempt_id == attempt_id)).first()
    record.status = IdentityVerificationStatus.rejected
    session.add(record)
    session.commit()

    assert client.post(f"/api/student/attempts/{attempt_id}/start").status_code == 409
    assert submit_identity(client, attempt_id, MINIMAL_PNG, "retake.png", "image/png").status_code == 201
    assert client.post(f"/api/student/attempts/{attempt_id}/start").status_code == 200


def test_start_expired_attempt_rejected(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID022", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)
    attempt = session.get(Attempt, attempt_id)
    attempt.status = AttemptStatus.timed_out
    session.add(attempt)
    session.commit()
    assert client.post(f"/api/student/attempts/{attempt_id}/start").status_code == 409


def test_start_submitted_attempt_rejected(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID023", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)
    attempt = session.get(Attempt, attempt_id)
    attempt.status = AttemptStatus.submitted
    session.add(attempt)
    session.commit()
    assert client.post(f"/api/student/attempts/{attempt_id}/start").status_code == 409


# ---------------------------------------------------------------------------
# Storage/DB consistency and privacy
# ---------------------------------------------------------------------------

def test_storage_failure_leaves_no_db_record(client: TestClient, session: Session, monkeypatch):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID024", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)

    from app.modules.students import service as student_service

    def boom(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(student_service, "save_identity_image", boom)
    resp = submit_identity(client, attempt_id)
    assert resp.status_code in (400, 500)
    record = session.exec(select(AttemptIdentityVerification).where(AttemptIdentityVerification.attempt_id == attempt_id)).first()
    assert record is None


def test_db_failure_after_storage_cleans_up_new_file(client: TestClient, session: Session, monkeypatch):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    student = create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID025", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)

    from app.modules.students import service as student_service
    from app.modules.students.identity_storage import get_storage_root

    attempt_dir = get_storage_root() / f"attempt_{attempt_id}"
    if attempt_dir.exists():
        for f in attempt_dir.iterdir():
            try:
                f.unlink()
            except OSError:
                pass

    original_commit = session.commit
    calls = {"n": 0}

    def failing_commit():
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("db failure")
        return original_commit()

    monkeypatch.setattr(session, "commit", failing_commit)
    with pytest.raises(RuntimeError):
        student_service.submit_identity_verification_photo(
            db=session,
            attempt_id=attempt_id,
            student_id=student.id,
            content=MINIMAL_JPEG,
            claimed_content_type="image/jpeg",
            filename="photo.jpg",
        )

    session.rollback()
    record = session.exec(select(AttemptIdentityVerification).where(AttemptIdentityVerification.attempt_id == attempt_id)).first()
    assert record is None
    assert not attempt_dir.exists() or not any(attempt_dir.iterdir())


def test_identity_status_does_not_expose_internal_storage_or_paths(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID026", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)
    submit_identity(client, attempt_id)
    resp = client.get(f"/api/student/attempts/{attempt_id}/identity-verification")
    assert resp.status_code == 200
    body = resp.text.lower()
    assert "image_path" not in body
    assert "storage/identity_verifications" not in body
    assert "backend\\storage" not in body and "backend/storage" not in body
    assert "student_" not in body  # filename fragment must not leak
    # attempt_id value is legitimately present; ensure no stored path fragment
    assert "attempt_" not in body.replace('"attempt_id"', '')



# ---------------------------------------------------------------------------
# Teacher review endpoints
# ---------------------------------------------------------------------------

def test_teacher_can_list_pending_identity_verifications(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    student = create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID030", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)
    submit_identity(client, attempt_id)
    login(client, "teacher@test.edu")
    resp = client.get(f"/api/teacher/tests/{test.id}/identity-verifications")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["attempt_id"] == attempt_id
    assert data[0]["student_email"] == "student@test.edu"
    assert data[0]["status"] == "pending"


def test_teacher_cannot_list_for_other_teachers_test(client: TestClient, session: Session):
    teacher1 = create_user(session, "teacher1@test.edu", UserRole.teacher)
    teacher2 = create_user(session, "teacher2@test.edu", UserRole.teacher)
    student = create_user(session, "student@test.edu", UserRole.student)
    test1 = create_test(session, "Exam1", "PXAM-ID031", teacher1.id)
    test2 = create_test(session, "Exam2", "PXAM-ID032", teacher2.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test1.id)
    submit_identity(client, attempt_id)
    login(client, "teacher2@test.edu")
    resp = client.get(f"/api/teacher/tests/{test1.id}/identity-verifications")
    assert resp.status_code == 403


def test_teacher_can_approve_pending_identity_verification(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    student = create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID033", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)
    submit_identity(client, attempt_id)
    record = session.exec(select(AttemptIdentityVerification).where(AttemptIdentityVerification.attempt_id == attempt_id)).first()
    login(client, "teacher@test.edu")
    resp = client.put(
        f"/api/teacher/identity-verifications/{record.id}",
        json={"status": "verified", "reviewer_notes": "Looks good"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "verified"
    assert data["reviewer_id"] == teacher.id
    assert data["reviewer_notes"] == "Looks good"
    assert data["reviewed_at"] is not None
    session.refresh(record)
    assert record.status == IdentityVerificationStatus.verified
    assert record.reviewer_id == teacher.id


def test_teacher_can_reject_pending_identity_verification(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    student = create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID034", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)
    submit_identity(client, attempt_id)
    record = session.exec(select(AttemptIdentityVerification).where(AttemptIdentityVerification.attempt_id == attempt_id)).first()
    login(client, "teacher@test.edu")
    resp = client.put(
        f"/api/teacher/identity-verifications/{record.id}",
        json={"status": "rejected", "reviewer_notes": "Blurry image"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "rejected"
    assert data["reviewer_id"] == teacher.id
    assert data["reviewer_notes"] == "Blurry image"


def test_teacher_cannot_review_non_pending_identity_verification(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    student = create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID035", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)
    submit_identity(client, attempt_id)
    record = session.exec(select(AttemptIdentityVerification).where(AttemptIdentityVerification.attempt_id == attempt_id)).first()
    record.status = IdentityVerificationStatus.verified
    record.reviewed_at = datetime.now(timezone.utc)
    session.add(record)
    session.commit()
    login(client, "teacher@test.edu")
    resp = client.put(
        f"/api/teacher/identity-verifications/{record.id}",
        json={"status": "rejected", "reviewer_notes": "test"},
    )
    assert resp.status_code == 409


def test_teacher_cannot_review_other_teachers_student(client: TestClient, session: Session):
    teacher1 = create_user(session, "teacher1@test.edu", UserRole.teacher)
    teacher2 = create_user(session, "teacher2@test.edu", UserRole.teacher)
    student = create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID036", teacher1.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)
    submit_identity(client, attempt_id)
    record = session.exec(select(AttemptIdentityVerification).where(AttemptIdentityVerification.attempt_id == attempt_id)).first()
    login(client, "teacher2@test.edu")
    resp = client.put(
        f"/api/teacher/identity-verifications/{record.id}",
        json={"status": "verified", "reviewer_notes": "test"},
    )
    assert resp.status_code == 403


def test_teacher_cannot_use_invalid_review_status(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    student = create_user(session, "student@test.edu", UserRole.student)
    test = create_test(session, "Exam", "PXAM-ID037", teacher.id)
    login(client, "student@test.edu")
    attempt_id = create_attempt_via_api(client, test.id)
    submit_identity(client, attempt_id)
    record = session.exec(select(AttemptIdentityVerification).where(AttemptIdentityVerification.attempt_id == attempt_id)).first()
    login(client, "teacher@test.edu")
    resp = client.put(
        f"/api/teacher/identity-verifications/{record.id}",
        json={"status": "not_submitted", "reviewer_notes": "test"},
    )
    assert resp.status_code == 422


def test_teacher_get_nonexistent_identity_verification(client: TestClient, session: Session):
    teacher = create_user(session, "teacher@test.edu", UserRole.teacher)
    login(client, "teacher@test.edu")
    resp = client.get("/api/teacher/identity-verifications/9999")
    assert resp.status_code == 404
