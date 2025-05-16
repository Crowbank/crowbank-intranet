"""Add stripe_id to customers

Revision ID: 9c6c2fb34b4e
Revises: 6dd1e0b9c212
Create Date: 2025-05-16 13:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '9c6c2fb34b4e'
down_revision: Union[str, None] = '6dd1e0b9c212'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('customers', sa.Column('stripe_id', sa.String(length=50), nullable=True))
    op.create_unique_constraint('uq_customers_stripe_id', 'customers', ['stripe_id'])


def downgrade() -> None:
    op.drop_constraint('uq_customers_stripe_id', 'customers', type_='unique')
    op.drop_column('customers', 'stripe_id') 