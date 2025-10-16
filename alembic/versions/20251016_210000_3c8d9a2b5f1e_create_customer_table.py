"""Tạo bảng customer cho module quản lý khách hàng.

Revision ID: 3c8d9a2b5f1e
Revises: 1e8c2b6f3759
Create Date: 2025-10-16 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '3c8d9a2b5f1e'
down_revision: Union[str, Sequence[str], None] = '1e8c2b6f3759'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	"""Upgrade schema - tạo bảng customer."""
	op.create_table(
		'customer',
		sa.Column('id', sa.Integer(), nullable=False),
		sa.Column('user_id', sa.Integer(), nullable=True),
		sa.Column('full_name', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
		sa.Column('phone_number', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=True),
		sa.Column('date_of_birth', sa.DateTime(), nullable=True),
		sa.Column('gender', sqlmodel.sql.sqltypes.AutoString(length=10), nullable=True),
		sa.Column('address', sa.Text(), nullable=True),
		sa.Column('notes', sa.Text(), nullable=True),
		sa.Column('skin_type', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
		sa.Column('health_conditions', sa.Text(), nullable=True),
		sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
		sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
		sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
		sa.Column('deleted_at', sa.DateTime(), nullable=True),
		sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='SET NULL'),
		sa.PrimaryKeyConstraint('id'),
	)
	# Tạo indexes
	op.create_index(op.f('ix_customer_user_id'), 'customer', ['user_id'], unique=False)
	op.create_index(op.f('ix_customer_phone_number'), 'customer', ['phone_number'], unique=False)
	op.create_index(op.f('ix_customer_deleted_at'), 'customer', ['deleted_at'], unique=False)


def downgrade() -> None:
	"""Downgrade schema - xóa bảng customer."""
	op.drop_index(op.f('ix_customer_deleted_at'), table_name='customer')
	op.drop_index(op.f('ix_customer_phone_number'), table_name='customer')
	op.drop_index(op.f('ix_customer_user_id'), table_name='customer')
	op.drop_table('customer')
