"""attempt_created_status_nullable_timestamps

Revision ID: attempt_created_status_nullable_timestamps
Revises: 
Create Date: 2026-10-31 21:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'attempt_created_status_nullable_timestamps'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite does not support ALTER COLUMN directly, so we use batch operations.
    # batch_alter_table will recreate the table with the new schema.
    with op.batch_alter_table('attempts') as batch_op:
        # Make started_at nullable
        batch_op.alter_column(
            'started_at',
            existing_type=sa.DATETIME(),
            nullable=True,
            existing_nullable=False,
        )
        # Make time_limit_ends_at nullable
        batch_op.alter_column(
            'time_limit_ends_at',
            existing_type=sa.DATETIME(),
            nullable=True,
            existing_nullable=False,
        )
        # Add created_at column (nullable for existing rows)
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('attempts') as batch_op:
        batch_op.drop_column('created_at')
        batch_op.alter_column(
            'time_limit_ends_at',
            existing_type=sa.DATETIME(),
            nullable=False,
            existing_nullable=True,
        )
        batch_op.alter_column(
            'started_at',
            existing_type=sa.DATETIME(),
            nullable=False,
            existing_nullable=True,
        )
