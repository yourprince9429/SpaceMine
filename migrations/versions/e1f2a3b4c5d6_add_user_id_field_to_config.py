"""add_user_id_field_to_config

Revision ID: e1f2a3b4c5d6
Revises: d1e2f3a4b5c6
Create Date: 2026-01-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1f2a3b4c5d6'
down_revision = 'f1e2d3c4b5a6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('config', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_config_user_id_user', 'config', 'user', ['user_id'], ['id'])


def downgrade():
    op.drop_constraint('fk_config_user_id_user', 'config', type_='foreignkey')
    op.drop_column('config', 'user_id')
