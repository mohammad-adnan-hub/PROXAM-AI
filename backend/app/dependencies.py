from typing import Annotated, Optional
from fastapi import Cookie, Depends, Header, HTTPException, status
from sqlmodel import Session
from app.database import get_session
from app.models.user import User, UserRole
from app.modules.auth.service import decode_access_token


def get_db(session: Session = Depends(get_session)) -> Session:
    return session


def get_current_user(
    access_token: Annotated[Optional[str], Cookie()] = None,
    authorization: Annotated[Optional[str], Header()] = None,
    db: Session = Depends(get_db),
) -> User:
    """
    Decode JWT from HTTP-only cookie or Authorization header and return the authenticated User.
    """
    token = access_token
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    user = db.get(User, int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )
    return user


def require_role(*roles: UserRole):
    """Factory that returns a dependency enforcing a set of allowed roles."""
    def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return _check


require_student = require_role(UserRole.student)
require_teacher = require_role(UserRole.teacher)
require_admin = require_role(UserRole.admin)
require_teacher_or_admin = require_role(UserRole.teacher, UserRole.admin)
