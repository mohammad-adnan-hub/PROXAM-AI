"""add_image_data_to_attempt_identity_verifications

Revision ID: f7a8b9c0d1e2
Revises: e6f7a8b9c0d1
Create Date: 2026-11-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f7a8b9c0d1e2"
down_revision: Union[str, None] = "e6f7a8b9c0d1"
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "attempt_identity_verifications",
        sa.Column("image_data", sa.LargeBinary(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("attempt_identity_verifications", "image_data")
