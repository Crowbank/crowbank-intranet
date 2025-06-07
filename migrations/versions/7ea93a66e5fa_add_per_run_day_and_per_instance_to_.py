"""add PER_RUN_DAY and PER_INSTANCE to serviceapplicability enum

Revision ID: 7ea93a66e5fa
Revises: bb60dc9d0e66
Create Date: 2025-06-06 16:40:54.645101

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ea93a66e5fa'
down_revision: Union[str, None] = 'bb60dc9d0e66'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
