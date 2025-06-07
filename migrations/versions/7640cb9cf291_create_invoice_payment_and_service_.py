"""create invoice payment and service tables

Revision ID: 7640cb9cf291
Revises: e3f5c6df01a4
Create Date: 2025-06-06 15:55:20.957655

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7640cb9cf291'
down_revision: Union[str, None] = 'e3f5c6df01a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
