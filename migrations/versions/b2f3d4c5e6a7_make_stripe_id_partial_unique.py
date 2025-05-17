"""Make stripe_id unique only when non-null/non-empty

Revision ID: b2f3d4c5e6a7
Revises: a1d2e3f4b5c6
Create Date: 2025-05-16 14:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'b2f3d4c5e6a7'
down_revision: Union[str, None] = 'a1d2e3f4b5c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop previous unconditional unique constraint if it exists
    try:
        op.drop_constraint('uq_customers_stripe_id', 'customers', type_='unique')
    except Exception:
        pass
    # Create partial unique index (PostgreSQL only)
    op.create_index(
        'ix_customers_stripe_id_unique',
        'customers',
        ['stripe_id'],
        unique=True,
        postgresql_where=sa.text("stripe_id IS NOT NULL AND stripe_id <> ''")
    )


def downgrade() -> None:
    op.drop_index('ix_customers_stripe_id_unique', table_name='customers')
    op.create_unique_constraint('uq_customers_stripe_id', 'customers', ['stripe_id']) 