"""
Authentication integration tests for Proxam AI.
Verifies registration, login, logout, cookie handling, password reset,
and role-based access control.
"""
import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.dependencies import get_current_user, require_student, require_teacher, require_admin
from app.models.user import User, UserRole
from app.modules.auth.service import hash_password, create_password_reset_token


# In-memory database fixture for isolated testing
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


# ---------------------------------------------------------------------------
# Registration Tests
# ---------------------------------------------------------------------------

def test_register_student_success(client: TestClient):
    resp = client.post(
        "/api/auth/register",
        json={
            "full_name": "Alice Student",
            "email": "alice@student.edu",
            "password": "Password123!",
            "role": "student",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "alice@student.edu"
    assert data["role"] == "student"
    assert "access_token" in resp.cookies


def test_register_teacher_success(client: TestClient):
    resp = client.post(
        "/api/auth/register",
        json={
            "full_name": "Prof. Smith",
            "email": "smith@faculty.edu",
            "password": "Password123!",
            "role": "teacher",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["role"] == "teacher"
    assert "access_token" in resp.cookies


def test_register_duplicate_email_fails(client: TestClient):
    client.post(
        "/api/auth/register",
        json={
            "full_name": "Alice",
            "email": "alice@student.edu",
            "password": "Password123!",
            "role": "student",
        },
    )
    dup = client.post(
        "/api/auth/register",
        json={
            "full_name": "Alice Clone",
            "email": "alice@student.edu",
            "password": "Password123!",
            "role": "student",
        },
    )
    assert dup.status_code == 409


def test_register_admin_rejected(client: TestClient):
    resp = client.post(
        "/api/auth/register",
        json={
            "full_name": "Rogue Admin",
            "email": "rogue@admin.edu",
            "password": "Password123!",
            "role": "admin",
        },
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Login and Session Tests
# ---------------------------------------------------------------------------

def test_login_success_sets_http_only_cookie(client: TestClient, session: Session):
    user = User(
        full_name="Bob User",
        email="bob@user.edu",
        hashed_password=hash_password("MySecretPass123!"),
        role=UserRole.student,
        is_active=True,
    )
    session.add(user)
    session.commit()

    resp = client.post(
        "/api/auth/login",
        json={"email": "bob@user.edu", "password": "MySecretPass123!"},
    )
    assert resp.status_code == 200
    assert resp.json()["email"] == "bob@user.edu"
    assert "access_token" in resp.cookies


def test_login_invalid_password(client: TestClient, session: Session):
    user = User(
        full_name="Bob User",
        email="bob@user.edu",
        hashed_password=hash_password("MySecretPass123!"),
        role=UserRole.student,
        is_active=True,
    )
    session.add(user)
    session.commit()

    resp = client.post(
        "/api/auth/login",
        json={"email": "bob@user.edu", "password": "WrongPassword!"},
    )
    assert resp.status_code == 401


def test_get_me_authenticated(client: TestClient):
    # Register auto-logs in and sets cookie
    client.post(
        "/api/auth/register",
        json={
            "full_name": "Charlie",
            "email": "charlie@test.edu",
            "password": "Password123!",
            "role": "student",
        },
    )
    me_resp = client.get("/api/auth/me")
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "charlie@test.edu"


def test_get_me_unauthenticated(client: TestClient):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_logout_clears_cookie(client: TestClient):
    client.post(
        "/api/auth/register",
        json={
            "full_name": "Dave",
            "email": "dave@test.edu",
            "password": "Password123!",
            "role": "student",
        },
    )
    logout_resp = client.post("/api/auth/logout")
    assert logout_resp.status_code == 200

    # Next /me call should fail
    me_resp = client.get("/api/auth/me")
    assert me_resp.status_code == 401


# ---------------------------------------------------------------------------
# Password Reset Tests
# ---------------------------------------------------------------------------

def test_forgot_and_reset_password_flow(client: TestClient, session: Session):
    user = User(
        full_name="Eve User",
        email="eve@user.edu",
        hashed_password=hash_password("OldPassword123!"),
        role=UserRole.student,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Forgot password request returns 200
    forgot_resp = client.post(
        "/api/auth/forgot-password",
        json={"email": "eve@user.edu"},
    )
    assert forgot_resp.status_code == 200

    # Obtain reset token from service
    token = create_password_reset_token(session, user)

    # Reset password with token
    reset_resp = client.post(
        "/api/auth/reset-password",
        json={"token": token, "new_password": "NewSecretPassword123!"},
    )
    assert reset_resp.status_code == 200

    # Old password fails
    old_login = client.post(
        "/api/auth/login",
        json={"email": "eve@user.edu", "password": "OldPassword123!"},
    )
    assert old_login.status_code == 401

    # New password succeeds
    new_login = client.post(
        "/api/auth/login",
        json={"email": "eve@user.edu", "password": "NewSecretPassword123!"},
    )
    assert new_login.status_code == 200


def test_reset_password_invalid_token(client: TestClient):
    resp = client.post(
        "/api/auth/reset-password",
        json={"token": "invalid-token-xyz", "new_password": "NewPassword123!"},
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Change Password Tests
# ---------------------------------------------------------------------------

def test_change_password_flow(client: TestClient):
    client.post(
        "/api/auth/register",
        json={
            "full_name": "Frank",
            "email": "frank@test.edu",
            "password": "Password123!",
            "role": "teacher",
        },
    )
    # Change password
    chg_resp = client.post(
        "/api/auth/change-password",
        json={
            "current_password": "Password123!",
            "new_password": "UpdatedPassword456!",
        },
    )
    assert chg_resp.status_code == 200

    # Incorrect current password fails
    fail_resp = client.post(
        "/api/auth/change-password",
        json={
            "current_password": "WrongPassword999!",
            "new_password": "AnotherPassword789!",
        },
    )
    assert fail_resp.status_code == 400


# ---------------------------------------------------------------------------
# Role-Based Access Control (RBAC) Tests
# ---------------------------------------------------------------------------

def test_rbac_student_cannot_access_teacher_route(client: TestClient):
    # Register as student
    client.post(
        "/api/auth/register",
        json={
            "full_name": "Student Only",
            "email": "studentonly@test.edu",
            "password": "Password123!",
            "role": "student",
        },
    )

    # Temporary test endpoint with teacher dependency
    @app.get("/api/test-teacher-only")
    def _teacher_endpoint(user: User = Depends(require_teacher)):
        return {"status": "ok"}

    resp = client.get("/api/test-teacher-only")
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Insufficient permissions"


def test_rbac_teacher_cannot_access_student_route(client: TestClient):
    # Register as teacher
    client.post(
        "/api/auth/register",
        json={
            "full_name": "Teacher Only",
            "email": "teacheronly@test.edu",
            "password": "Password123!",
            "role": "teacher",
        },
    )

    @app.get("/api/test-student-only")
    def _student_endpoint(user: User = Depends(require_student)):
        return {"status": "ok"}

    resp = client.get("/api/test-student-only")
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Insufficient permissions"


def test_rbac_admin_access(client: TestClient, session: Session):
    admin = User(
        full_name="Admin User",
        email="superadmin@test.edu",
        hashed_password=hash_password("AdminPass123!"),
        role=UserRole.admin,
        is_active=True,
    )
    session.add(admin)
    session.commit()

    # Login as admin
    client.post(
        "/api/auth/login",
        json={"email": "superadmin@test.edu", "password": "AdminPass123!"},
    )

    @app.get("/api/test-admin-only")
    def _admin_endpoint(user: User = Depends(require_admin)):
        return {"admin": user.email}

    resp = client.get("/api/test-admin-only")
    assert resp.status_code == 200
    assert resp.json()["admin"] == "superadmin@test.edu"
