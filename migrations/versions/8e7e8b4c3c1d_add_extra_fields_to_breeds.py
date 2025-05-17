"""Add suspect, weight, share_single to breeds

Revision ID: 8e7e8b4c3c1d
Revises: 9c6c2fb34b4e
Create Date: 2025-05-16 13:20:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '8e7e8b4c3c1d'
down_revision: Union[str, None] = '9c6c2fb34b4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('breeds', sa.Column('suspect', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('breeds', sa.Column('weight', sa.Numeric(5, 2), nullable=True))
    op.add_column('breeds', sa.Column('share_single', sa.Boolean(), nullable=False, server_default='true'))


def downgrade() -> None:
    op.drop_column('breeds', 'share_single')
    op.drop_column('breeds', 'weight')
    op.drop_column('breeds', 'suspect') 