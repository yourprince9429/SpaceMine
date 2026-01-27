"""remove is_read field and add user_id field to notices table

Revision ID: f1e2d3c4b5a6
Revises: d1e2f3a4b5c6
Create Date: 2026-01-27 11:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f1e2d3c4b5a6'
down_revision = 'd1e2f3a4b5c6'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('notices', 'is_read')
    op.add_column('notices', sa.Column('user_id', sa.Integer(), nullable=False))


def downgrade():
    op.drop_column('notices', 'user_id')
    op.add_column('notices', sa.Column('is_read', sa.Boolean(), nullable=False))
