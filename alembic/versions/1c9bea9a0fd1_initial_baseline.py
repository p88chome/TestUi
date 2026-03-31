"""initial baseline

Revision ID: 1c9bea9a0fd1
Revises: 
Create Date: 2026-03-25 18:35:00.000000

This is the baseline migration that represents the existing database schema.
Since the database was originally created via Base.metadata.create_all(),
this migration is intentionally empty — it serves as the "starting point"
for all future migrations.

On first deploy, main.py will auto-stamp this revision via `alembic stamp head`
so existing tables are not re-created.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c9bea9a0fd1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Baseline migration — intentionally empty.
    The existing database tables were created via Base.metadata.create_all().
    Future migrations will contain actual schema changes.
    """
    pass


def downgrade() -> None:
    """
    Cannot downgrade from baseline.
    """
    pass
