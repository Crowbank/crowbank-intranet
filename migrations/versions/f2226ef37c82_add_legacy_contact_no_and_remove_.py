"""Add legacy_contact_no and remove address fields from contacts

Revision ID: f2226ef37c82
Revises: 7318affd696d
Create Date: 2025-05-17 16:39:39.069282

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2226ef37c82'
down_revision: Union[str, None] = '7318affd696d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add legacy_contact_no column
    op.add_column(
        'contacts',
        sa.Column('legacy_contact_no', sa.Integer(), nullable=True)
    )
    
    # Create unique index on legacy_contact_no
    op.create_index(
        'ix_contacts_legacy_contact_no_unique',
        'contacts',
        ['legacy_contact_no'],
        unique=True,
        postgresql_where=sa.text("legacy_contact_no IS NOT NULL")
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop index
    op.drop_index('ix_contacts_legacy_contact_no_unique', table_name='contacts')
    
    # Drop column
    op.drop_column('contacts', 'legacy_contact_no')
