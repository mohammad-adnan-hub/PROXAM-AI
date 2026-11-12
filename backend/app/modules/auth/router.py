from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlmodel import Session, select
import threading
import time

from app.config import get_settings
from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.modules.auth.schemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    ResetPasswordRequest,
    UserResponse,
)
from app.modules.auth.service import (
    authenticate_user,
    consume_reset_token_and_set_password,
    create_access_token,
    create_password_reset_token,
    hash_password,
    register_user,
    send_password_reset_email,
    verify_password,
)

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["auth"])

_COOKIE_NAME = "access_token"
_COOKIE_MAX_AGE = settings.access_token_expire_minutes * 60

# ---------------------------------------------------------------------------
# In-memory authentication rate limiter
# ---------------------------------------------------------------------------
#
# NOTE: This is per-process in-memory rate limiting. It does NOT provide
# distributed protection across multiple workers or instances. For
# multi-instance deployments, a shared store such as Redis is required.
#
# Key: (endpoint_name, client_ip) -> list of request timestamps
_rate_limit_state: dict[tuple[str, str], list[float]] = {}
_rate_limit_lock = threading.Lock()
_rate_limit_enabled = True


def _is_rate_limited(endpoint: str, client_ip: str) -> bool:
    """Check whether the client has exceeded the rate limit for an endpoint.

    Returns True if the request should be rejected (429), False otherwise.
    Expired entries are cleaned up on each check to prevent unbounded memory
    growth. All state access is protected by a lock for concurrency safety.
    """
    if not _rate_limit_enabled:
        return False

    now = time.time()
    key = (endpoint, client_ip)
    window_seconds = settings.auth_rate_limit_window_seconds
    max_requests = settings.auth_rate_limit_requests

    with _rate_limit_lock:
        timestamps = _rate_limit_state.get(key, [])
        cutoff = now - window_seconds
        valid_timestamps = [ts for ts in timestamps if ts > cutoff]

        if len(valid_timestamps) >= max_requests:
            _rate_limit_state[key] = valid_timestamps
            return True

        valid_timestamps.append(now)
        _rate_limit_state[key] = valid_timestamps
        return False


def _reset_rate_limit_state() -> None:
    """Reset all rate-limit state. For test isolation only."""
    with _rate_limit_lock:
        _rate_limit_state.clear()


def _set_rate_limit_enabled(enabled: bool) -> None:
    """Enable or disable rate limiting. For test isolation only."""
    global _rate_limit_enabled
    _rate_limit_enabled = enabled


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=_COOKIE_MAX_AGE,
        path="/",
    )


def _clear_auth_cookie(response: Response) -> None:
    response.delete_cookie(
        key=_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    request: Request,
    payload: RegisterRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> UserResponse:
    client_host = request.client.host if request.client else "unknown"
    if _is_rate_limited("register", client_host):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
        )
    try:
        user = register_user(
            db=db,
            full_name=payload.full_name,
            email=payload.email,
            password=payload.password,
            role=payload.role,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    token = create_access_token(user.id)
    _set_auth_cookie(response, token)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=UserResponse)
def login(
    request: Request,
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> UserResponse:
    client_host = request.client.host if request.client else "unknown"
    if _is_rate_limited("login", client_host):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
        )
    user = authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )
    token = create_access_token(user.id)
    _set_auth_cookie(response, token)
    return UserResponse.model_validate(user)


@router.post("/logout", response_model=MessageResponse)
def logout(response: Response) -> MessageResponse:
    _clear_auth_cookie(response)
    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(
    request: Request,
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db),
) -> MessageResponse:
    """Request a password reset. Returns generic message to prevent email enumeration."""
    client_host = request.client.host if request.client else "unknown"
    if _is_rate_limited("forgot-password", client_host):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
        )
    user = db.exec(select(User).where(User.email == payload.email.lower())).first()
    if user and user.is_active:
        raw_token = create_password_reset_token(db, user)
        reset_url = f"{settings.frontend_url}/reset-password?token={raw_token}"
        send_password_reset_email(user.email, reset_url)
    return MessageResponse(
        message="If an account with that email exists, a password reset link has been sent."
    )


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(
    request: Request,
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
) -> MessageResponse:
    client_host = request.client.host if request.client else "unknown"
    if _is_rate_limited("reset-password", client_host):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
        )
    success = consume_reset_token_and_set_password(db, payload.token, payload.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )
    return MessageResponse(message="Password reset successfully")


@router.post("/change-password", response_model=MessageResponse)
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    current_user.hashed_password = hash_password(payload.new_password)
    db.add(current_user)
    db.commit()
    return MessageResponse(message="Password changed successfully")
