"""add_reviewer_field_to_withdrawal_and_recharge

Revision ID: d1e2f3a4b5c6
Revises: b7e79be02716
Create Date: 2026-01-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1e2f3a4b5c6'
down_revision = 'b7e79be02716'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('withdrawals', sa.Column('reviewer_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_withdrawals_reviewer_id_user', 'withdrawals', 'user', ['reviewer_id'], ['id'])

    op.add_column('recharge', sa.Column('reviewer_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_recharge_reviewer_id_user', 'recharge', 'user', ['reviewer_id'], ['id'])


def downgrade():
    op.drop_constraint('fk_recharge_reviewer_id_user', 'recharge', type_='foreignkey')
    op.drop_column('recharge', 'reviewer_id')

    op.drop_constraint('fk_withdrawals_reviewer_id_user', 'withdrawals', type_='foreignkey')
    op.drop_column('withdrawals', 'reviewer_id')
