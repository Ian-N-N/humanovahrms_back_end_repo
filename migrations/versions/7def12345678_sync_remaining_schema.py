"""sync remaining schema

Revision ID: 7def12345678
Revises: 6def12345678
Create Date: 2026-01-16 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7def12345678'
down_revision = '6def12345678'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Add missing columns to employees
    with op.batch_alter_table('employees', schema=None) as batch_op:
        batch_op.add_column(sa.Column('personal_email', sa.String(length=255), nullable=True))

    # 2. Add missing columns to attendance
    with op.batch_alter_table('attendance', schema=None) as batch_op:
        batch_op.add_column(sa.Column('hours_worked', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('overtime_hours', sa.Float(), nullable=True))


def downgrade():
    with op.batch_alter_table('attendance', schema=None) as batch_op:
        batch_op.drop_column('overtime_hours')
        batch_op.drop_column('hours_worked')

    with op.batch_alter_table('employees', schema=None) as batch_op:
        batch_op.drop_column('personal_email')
