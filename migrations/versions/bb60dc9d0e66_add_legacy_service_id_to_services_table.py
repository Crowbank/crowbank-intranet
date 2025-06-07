"""add legacy_service_id to services table

Revision ID: bb60dc9d0e66
Revises: 7640cb9cf291
Create Date: 2025-06-06 16:16:43.581209

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb60dc9d0e66'
down_revision: Union[str, None] = '7640cb9cf291'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
