"""Add relation_type column to customer_contacts

Revision ID: 26e9bab8887b
Revises: f2226ef37c82
Create Date: 2025-05-17 16:51:31.301491

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '26e9bab8887b'
down_revision: Union[str, None] = 'f2226ef37c82'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add relation_type column to customer_contacts
    op.add_column(
        'customer_contacts',
        sa.Column('relation_type', sa.String(50), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop relation_type column from customer_contacts
    op.drop_column('customer_contacts', 'relation_type')
