"""add attempt identity verifications table

Revision ID: b7d3e9a1c4f2
Revises: 6520861a8d45
Create Date: 2026-11-15 13:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b7d3e9a1c4f2"
down_revision: Union[str, None] = "6520861a8d45"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "attempt_identity_verifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("attempt_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("image_path", sa.String(length=500), nullable=True),
        sa.Column("original_filename", sa.String(length=255), nullable=True),
        sa.Column("content_type", sa.String(length=100), nullable=True),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(), nullable=True),
        sa.Column("reviewer_id", sa.Integer(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("reviewer_notes", sa.String(length=2000), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["attempt_id"], ["attempts.id"]),
        sa.ForeignKeyConstraint(["reviewer_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("attempt_id", name="uq_attempt_identity_verification_attempt"),
    )
    op.create_index(
        op.f("ix_attempt_identity_verifications_attempt_id"),
        "attempt_identity_verifications",
        ["attempt_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_attempt_identity_verifications_student_id"),
        "attempt_identity_verifications",
        ["student_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_attempt_identity_verifications_student_id"),
        table_name="attempt_identity_verifications",
    )
    op.drop_index(
        op.f("ix_attempt_identity_verifications_attempt_id"),
        table_name="attempt_identity_verifications",
    )
    op.drop_table("attempt_identity_verifications")
