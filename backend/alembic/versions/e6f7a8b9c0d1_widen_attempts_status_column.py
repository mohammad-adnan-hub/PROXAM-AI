"""widen_attempts_status_column

Revision ID: e6f7a8b9c0d1
Revises: d4e5f6a7b8c9
Create Date: 2026-11-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e6f7a8b9c0d1"
down_revision: Union[str, None] = "d4e5f6a7b8c9"
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    # Widens attempts.status so all AttemptStatus values, including
    # terminated_by_warnings (24 characters), fit in both SQLite and PostgreSQL.
    with op.batch_alter_table("attempts") as batch_op:
        batch_op.alter_column(
            "status",
            existing_type=sa.String(length=11),
            type_=sa.String(length=32),
            existing_nullable=False,
        )


def downgrade() -> None:
    # WARNING: Downgrading truncates any status value longer than 11 characters,
    # including terminated_by_warnings. This downgrade is therefore not safe for
    # databases containing terminated attempts.
    with op.batch_alter_table("attempts") as batch_op:
        batch_op.alter_column(
            "status",
            existing_type=sa.String(length=32),
            type_=sa.String(length=11),
            existing_nullable=False,
        )
