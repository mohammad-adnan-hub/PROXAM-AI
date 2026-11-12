"""add_attempt_foreign_keys_and_unique_constraint

Revision ID: add_attempt_foreign_keys_and_unique_constraint
Revises: attempt_created_status_nullable_timestamps
Create Date: 2026-10-31 22:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_attempt_foreign_keys_and_unique_constraint'
down_revision: Union[str, None] = 'attempt_created_status_nullable_timestamps'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite does not support ALTER TABLE ADD CONSTRAINT / ADD FOREIGN KEY
    # directly, so we use batch_alter_table which recreates the table
    # preserving all data, indexes, and records.
    with op.batch_alter_table('attempts') as batch_op:
        batch_op.create_foreign_key(
            'fk_attempts_test_id_tests',
            'tests',
            ['test_id'],
            ['id'],
        )
        batch_op.create_foreign_key(
            'fk_attempts_student_id_users',
            'users',
            ['student_id'],
            ['id'],
        )
        batch_op.create_unique_constraint(
            'uq_student_test_attempt',
            ['student_id', 'test_id'],
        )


def downgrade() -> None:
    with op.batch_alter_table('attempts') as batch_op:
        batch_op.drop_constraint('uq_student_test_attempt', type_='unique')
        batch_op.drop_constraint('fk_attempts_student_id_users', type_='foreignkey')
        batch_op.drop_constraint('fk_attempts_test_id_tests', type_='foreignkey')
