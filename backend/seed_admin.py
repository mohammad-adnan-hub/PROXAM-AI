"""
Admin account seed script for Proxam AI.

Usage:
    python seed_admin.py
"""
import os
import sys
from pathlib import Path

# Ensure backend root is in sys.path
sys.path.insert(0, str(Path(__file__).parent))

from sqlmodel import Session, select
from app.config import get_settings
from app.database import engine, create_db_and_tables
from app.models.user import User, UserRole
from app.modules.auth.service import hash_password


def seed_admin() -> None:
    settings = get_settings()
    create_db_and_tables()

    email = os.environ.get("ADMIN_EMAIL", settings.admin_email).strip()
    password = os.environ.get("ADMIN_PASSWORD", settings.admin_password).strip()
    full_name = os.environ.get("ADMIN_FULL_NAME", settings.admin_full_name).strip()

    if not email:
        email = input("Admin email: ").strip()
    if not password:
        import getpass
        password = getpass.getpass("Admin password (min 8 chars): ").strip()
    if not full_name:
        full_name = "Platform Administrator"

    if len(password) < 8:
        print("Error: Admin password must be at least 8 characters.")
        sys.exit(1)

    with Session(engine) as db:
        existing = db.exec(select(User).where(User.email == email.lower())).first()
        if existing:
            if existing.role == UserRole.admin:
                print(f"[OK] Admin account already exists: {existing.email} (id={existing.id})")
            else:
                print(f"[!] User {existing.email} exists with role {existing.role}. Promoting to admin...")
                existing.role = UserRole.admin
                db.add(existing)
                db.commit()
                print(f"[OK] Promoted {existing.email} to admin.")
            return

        admin = User(
            full_name=full_name,
            email=email.lower(),
            hashed_password=hash_password(password),
            role=UserRole.admin,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"[OK] Admin account created: {admin.email} (id={admin.id}, role={admin.role})")


if __name__ == "__main__":
    seed_admin()
