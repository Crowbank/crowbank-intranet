"""Rename relationship column to relation_type in customer_contacts

Revision ID: 7318affd696d
Revises: d4e5f6a7b8c9
Create Date: 2025-05-17 15:24:02.298298

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7318affd696d'
down_revision: Union[str, None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename column 'relationship' to 'relation_type'
    op.alter_column('customer_contacts', 'relationship', new_column_name='relation_type')


def downgrade() -> None:
    """Downgrade schema."""
    # Rename column 'relation_type' back to 'relationship'
    op.alter_column('customer_contacts', 'relation_type', new_column_name='relationship')
