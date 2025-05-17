"""Add secondary phone/email to contacts and relationship to customer_contacts

Revision ID: d4e5f6a7b8c9
Revises: c7d8e9f0a1b2
Create Date: 2025-05-16 14:45:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'c7d8e9f0a1b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns to contacts
    op.add_column('contacts', sa.Column('phone_alt', sa.String(length=30), nullable=True))
    op.add_column('contacts', sa.Column('email_alt', sa.String(length=255), nullable=True))

    # Add relationship column to customer_contacts
    op.add_column('customer_contacts', sa.Column('relationship', sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column('customer_contacts', 'relationship')
    op.drop_column('contacts', 'email_alt')
    op.drop_column('contacts', 'phone_alt') 