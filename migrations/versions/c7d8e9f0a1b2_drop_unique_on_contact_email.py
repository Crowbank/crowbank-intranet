"""Drop unique constraint on contacts.email_address

Revision ID: c7d8e9f0a1b2
Revises: b2f3d4c5e6a7
Create Date: 2025-05-16 14:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'c7d8e9f0a1b2'
down_revision: Union[str, None] = 'b2f3d4c5e6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Attempt to drop any unique constraint or index on email_address
    try:
        op.drop_constraint('contacts_email_address_key', 'contacts', type_='unique')
    except Exception:
        pass
    try:
        op.drop_index('ix_contacts_email_address', table_name='contacts')
    except Exception:
        pass


def downgrade() -> None:
    # Recreate a non-unique index for lookup speed
    op.create_index('ix_contacts_email_address', 'contacts', ['email_address']) 