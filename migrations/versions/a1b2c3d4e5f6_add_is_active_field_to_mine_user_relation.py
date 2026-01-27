"""add_is_active_field_to_mine_user_relation

Revision ID: a1b2c3d4e5f6
Revises: 44bcf19a2f33
Create Date: 2026-01-27

"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = '44bcf19a2f33'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('mine_user_relation', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'))


def downgrade():
    op.drop_column('mine_user_relation', 'is_active')
