"""add is_reasoning_model to aimodel

Revision ID: e4f5a6b7c8d9
Revises: a3f8c2e91b47
Create Date: 2026-04-02 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e4f5a6b7c8d9'
down_revision: Union[str, None] = 'a3f8c2e91b47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_reasoning_model column, default false
    op.add_column('ai_models', sa.Column('is_reasoning_model', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    op.drop_column('ai_models', 'is_reasoning_model')
