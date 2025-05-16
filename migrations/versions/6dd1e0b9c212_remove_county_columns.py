"""Remove unused county columns

Revision ID: 6dd1e0b9c212
Revises: 5d1be9c1c2f0
Create Date: 2025-05-16 12:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '6dd1e0b9c212'
down_revision: Union[str, None] = '5d1be9c1c2f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop now-unused 'county' columns."""
    with op.batch_alter_table('contacts', schema=None) as batch:
        batch.drop_column('county')
    with op.batch_alter_table('customers', schema=None) as batch:
        batch.drop_column('county')
    with op.batch_alter_table('vets', schema=None) as batch:
        batch.drop_column('county')


def downgrade() -> None:
    """Re-add 'county' columns (nullable)."""
    op.add_column('contacts', sa.Column('county', sa.String(length=50), nullable=True))
    op.add_column('customers', sa.Column('county', sa.String(length=50), nullable=True))
    op.add_column('vets', sa.Column('county', sa.String(length=50), nullable=True)) 