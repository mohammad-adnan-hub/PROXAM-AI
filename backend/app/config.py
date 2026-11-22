from functools import lru_cache
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Docs
    docs_enabled: bool = True

    # Database
    database_url: str = "sqlite:///./proxam_ai.db"

    # JWT (must be configured via environment variable; no production fallback)
    secret_key: str = Field(default="", description="JWT signing key - required")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if not v:
            raise ValueError("SECRET_KEY must be set via environment variable or .env file")
        if v == "proxam-ai-super-secret-jwt-key-minimum-32-chars-2026":
            raise ValueError("SECRET_KEY must not use the hardcoded development value")
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v

    # Cookie
    cookie_secure: bool = False
    cookie_samesite: str = "lax"

    # CORS
    frontend_url: str = "http://localhost:5173"

    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@proxamai.com"
    smtp_from_name: str = "Proxam AI"

    # Dev mode: log reset URLs to console instead of sending email (default off)
    dev_mode: bool = False

    # Password reset token expiry in minutes
    password_reset_expire_minutes: int = 30

    # Admin seed config (no predictable defaults; must be explicitly configured)
    admin_email: str | None = None
    admin_password: str | None = None
    admin_full_name: str = "Platform Administrator"

    # Authentication rate limiting (requests per minute per IP)
    auth_rate_limit_requests: int = 5
    auth_rate_limit_window_seconds: int = 60

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        if not self.dev_mode:
            if "sqlite" in self.database_url.lower():
                raise ValueError("DATABASE_URL must use PostgreSQL in production")
            if "localhost" in self.frontend_url or "127.0.0.1" in self.frontend_url:
                raise ValueError("FRONTEND_URL must be a production origin")
        return self

    @model_validator(mode="after")
    def validate_production_cookie_security(self) -> "Settings":
        """Require Secure cookies in production (dev_mode=False)."""
        if not self.dev_mode and not self.cookie_secure:
            raise ValueError(
                "COOKIE_SECURE must be true in production (DEV_MODE=false). "
                "Set COOKIE_SECURE=true for production deployments."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
