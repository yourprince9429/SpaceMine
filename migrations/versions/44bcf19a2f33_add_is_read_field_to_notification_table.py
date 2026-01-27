"""add is_read field to notification table

Revision ID: 44bcf19a2f33
Revises: 86f5762f2175
Create Date: 2026-01-27 11:30:37.832432

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '44bcf19a2f33'
down_revision = '86f5762f2175'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('notification', sa.Column('is_read', sa.Boolean(), nullable=False, server_default='0'))


def downgrade():
    op.drop_column('notification', 'is_read')
