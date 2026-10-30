from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = "sqlite:///./proxam_ai.db"

    # JWT
    secret_key: str = "proxam-ai-super-secret-jwt-key-minimum-32-chars-2026"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

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

    # Dev mode: log reset URLs to console instead of sending email
    dev_mode: bool = True

    # Password reset token expiry in minutes
    password_reset_expire_minutes: int = 30

    # Admin seed config
    admin_email: str = "admin@proxamai.com"
    admin_password: str = "AdminSecurePassword123!"
    admin_full_name: str = "Platform Administrator"


@lru_cache
def get_settings() -> Settings:
    return Settings()
