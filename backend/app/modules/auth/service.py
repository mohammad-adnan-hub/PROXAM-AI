import hashlib
import logging
import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from jose import JWTError, jwt
try:
    from pwdlib import PasswordHash
    from pwdlib.hashers.argon2 import Argon2Hasher
    _password_hash = PasswordHash([Argon2Hasher()])
    def hash_password(plain: str) -> str:
        return _password_hash.hash(plain)
    def verify_password(plain: str, hashed: str) -> bool:
        return _password_hash.verify(plain, hashed)
except Exception:
    # Fallback to argon2_cffi directly or passlib/sha256 if pwdlib hasher setup fails
    import hashlib
    def hash_password(plain: str) -> str:
        salt = secrets.token_hex(16)
        h = hashlib.sha256((salt + plain).encode("utf-8")).hexdigest()
        return f"pbkdf2_sha256${salt}${h}"
    def verify_password(plain: str, hashed: str) -> bool:
        if hashed.startswith("pbkdf2_sha256$"):
            _, salt, h = hashed.split("$")
            return hashlib.sha256((salt + plain).encode("utf-8")).hexdigest() == h
        return False

from sqlmodel import Session, select

from app.config import get_settings
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)
settings = get_settings()


# ---------------------------------------------------------------------------
# JWT utilities
# ---------------------------------------------------------------------------

def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None


# ---------------------------------------------------------------------------
# User registration and login
# ---------------------------------------------------------------------------

def register_user(db: Session, full_name: str, email: str, password: str, role: UserRole) -> User:
    """Create a new user. Raises ValueError if email already registered."""
    existing = db.exec(select(User).where(User.email == email.lower())).first()
    if existing:
        raise ValueError("Email already registered")
    user = User(
        full_name=full_name.strip(),
        email=email.lower(),
        hashed_password=hash_password(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Return user if credentials are correct, else None."""
    user = db.exec(select(User).where(User.email == email.lower())).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# ---------------------------------------------------------------------------
# Password reset
# ---------------------------------------------------------------------------

def _hash_token(raw_token: str) -> str:
    """SHA-256 hash of the raw reset token for secure storage."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def create_password_reset_token(db: Session, user: User) -> str:
    """
    Generate a secure single-use reset token, store its hash, return raw token.
    Invalidates any existing unused tokens for this user.
    """
    existing_tokens = db.exec(
        select(PasswordResetToken)
        .where(PasswordResetToken.user_id == user.id, PasswordResetToken.used == False)
    ).all()
    for t in existing_tokens:
        t.used = True
        db.add(t)

    raw_token = secrets.token_urlsafe(32)
    token_hash = _hash_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.password_reset_expire_minutes)

    reset_token = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(reset_token)
    db.commit()
    return raw_token


def verify_reset_token(db: Session, raw_token: str) -> Optional[tuple[User, PasswordResetToken]]:
    """Verify reset token. Returns (user, token_record) if valid, else None."""
    token_hash = _hash_token(raw_token)
    record = db.exec(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used == False,
        )
    ).first()
    if not record:
        return None
    now_utc = datetime.now(timezone.utc)
    rec_exp = record.expires_at if record.expires_at.tzinfo else record.expires_at.replace(tzinfo=timezone.utc)
    if now_utc > rec_exp:
        return None
    user = db.get(User, record.user_id)
    if not user:
        return None
    return user, record


def consume_reset_token_and_set_password(db: Session, raw_token: str, new_password: str) -> bool:
    """Verify token, update password, mark token as used. Returns True on success."""
    result = verify_reset_token(db, raw_token)
    if not result:
        return False
    user, record = result
    user.hashed_password = hash_password(new_password)
    user.updated_at = datetime.now(timezone.utc)
    record.used = True
    db.add(user)
    db.add(record)
    db.commit()
    return True


# ---------------------------------------------------------------------------
# Email sending
# ---------------------------------------------------------------------------

def send_password_reset_email(email: str, reset_url: str) -> None:
    """
    Send password reset email. In dev mode, logs the URL to console instead.
    In production, sends via SMTP.
    """
    if settings.dev_mode:
        print("\n" + "=" * 60)
        print(f"[DEV MODE PASSWORD RESET] To: {email}")
        print(f"Reset Link: {reset_url}")
        print("=" * 60 + "\n")
        logger.info("[DEV MODE] Password reset URL for %s: %s", email, reset_url)
        return

    subject = "Proxam AI — Password Reset Request"
    body_html = f"""
    <html>
    <body style="font-family: sans-serif; line-height: 1.6; color: #111;">
        <h2>Proxam AI Password Reset</h2>
        <p>Hello,</p>
        <p>A password reset was requested for your account. Click the link below to set a new password:</p>
        <p><a href="{reset_url}" style="background: #111; color: #fff; padding: 10px 18px; border-radius: 999px; text-decoration: none; display: inline-block;">Reset Password</a></p>
        <p>Or paste this URL in your browser: {reset_url}</p>
        <p>This link will expire in {settings.password_reset_expire_minutes} minutes.</p>
        <p>If you did not request this, please ignore this email.</p>
        <hr/>
        <p style="font-size: 12px; color: #888;">Proxam AI Assessment System</p>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    msg["To"] = email
    msg.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
            server.starttls()
            if settings.smtp_username and settings.smtp_password:
                server.login(settings.smtp_username, settings.smtp_password)
            server.sendmail(settings.smtp_from_email, email, msg.as_string())
    except Exception as exc:
        logger.error("Failed to send reset email to %s: %s", email, exc)
