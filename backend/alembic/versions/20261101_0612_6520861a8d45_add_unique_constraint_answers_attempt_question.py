"""add_unique_constraint_answers_attempt_question

Revision ID: 6520861a8d45
Revises: add_attempt_foreign_keys_and_unique_constraint
Create Date: 2026-11-01 06:12:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6520861a8d45'
down_revision: Union[str, None] = 'add_attempt_foreign_keys_and_unique_constraint'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite does not support ALTER TABLE ADD CONSTRAINT directly,
    # so we use batch_alter_table which recreates the table
    # preserving all data, indexes, and records.
    with op.batch_alter_table('answers') as batch_op:
        batch_op.create_unique_constraint(
            'uq_answers_attempt_question',
            ['attempt_id', 'question_id'],
        )


def downgrade() -> None:
    with op.batch_alter_table('answers') as batch_op:
        batch_op.drop_constraint('uq_answers_attempt_question', type_='unique')
