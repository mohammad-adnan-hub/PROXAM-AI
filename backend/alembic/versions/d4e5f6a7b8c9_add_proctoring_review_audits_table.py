"""add proctoring review audits table

Revision ID: d4e5f6a7b8c9
Revises: c1a2b3d4e5f6
Create Date: 2026-11-21 21:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c1a2b3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "proctoring_review_audits",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("proctoring_event_id", sa.Integer(), nullable=False),
        sa.Column("reviewer_id", sa.Integer(), nullable=False),
        sa.Column("previous_review_status", sa.String(length=30), nullable=False),
        sa.Column("new_review_status", sa.String(length=30), nullable=False),
        sa.Column("previous_reviewer_notes", sa.String(length=2000), nullable=True),
        sa.Column("new_reviewer_notes", sa.String(length=2000), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["proctoring_event_id"], ["proctoring_events.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["reviewer_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_proctoring_review_audits_proctoring_event_id", "proctoring_review_audits", ["proctoring_event_id"])
    op.create_index("ix_proctoring_review_audits_reviewer_id", "proctoring_review_audits", ["reviewer_id"])


def downgrade() -> None:
    op.drop_index("ix_proctoring_review_audits_reviewer_id", table_name="proctoring_review_audits")
    op.drop_index("ix_proctoring_review_audits_proctoring_event_id", table_name="proctoring_review_audits")
    op.drop_table("proctoring_review_audits")
