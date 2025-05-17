"""Enforce NOT NULL legacy_vet_no and remove duplicates

Revision ID: a1d2e3f4b5c6
Revises: 8e7e8b4c3c1d
Create Date: 2025-05-16 13:35:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'a1d2e3f4b5c6'
down_revision: Union[str, None] = '8e7e8b4c3c1d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop rows where legacy_vet_no IS NULL (created by earlier import bug)
    op.execute("DELETE FROM vets WHERE legacy_vet_no IS NULL")
    # Ensure uniqueness – remove duplicates keeping the lowest id
    op.execute(
        """
        DELETE FROM vets a
        USING vets b
        WHERE a.id > b.id AND a.legacy_vet_no = b.legacy_vet_no
        """
    )
    # Alter column to NOT NULL
    with op.batch_alter_table('vets') as batch:
        batch.alter_column('legacy_vet_no', nullable=False)


def downgrade() -> None:
    with op.batch_alter_table('vets') as batch:
        batch.alter_column('legacy_vet_no', nullable=True) 