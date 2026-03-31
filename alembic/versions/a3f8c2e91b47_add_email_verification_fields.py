"""add email verification fields to users

Revision ID: a3f8c2e91b47
Revises: 1c9bea9a0fd1
Create Date: 2026-03-31 14:00:00.000000

新增三個欄位到 users 表：
- is_verified: 帳號是否已通過 Email 驗證（預設 False）
- verification_token: 驗證用的 UUID token
- verification_token_expires: token 的過期時間
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3f8c2e91b47'
down_revision: Union[str, None] = '1c9bea9a0fd1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add email verification columns to users table
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('verification_token', sa.String(), nullable=True))
    op.add_column('users', sa.Column('verification_token_expires', sa.DateTime(timezone=True), nullable=True))

    # Add index on verification_token for fast lookup
    op.create_index(
        op.f('ix_users_verification_token'),
        'users',
        ['verification_token'],
        unique=False
    )

    # IMPORTANT: Set all existing users as verified so they can still log in
    # (They were created before email verification was introduced)
    op.execute("UPDATE users SET is_verified = true, is_active = true WHERE is_verified = false")


def downgrade() -> None:
    op.drop_index(op.f('ix_users_verification_token'), table_name='users')
    op.drop_column('users', 'verification_token_expires')
    op.drop_column('users', 'verification_token')
    op.drop_column('users', 'is_verified')
