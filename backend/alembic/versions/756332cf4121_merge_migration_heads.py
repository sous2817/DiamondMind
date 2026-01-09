"""merge_migration_heads

Revision ID: 756332cf4121
Revises: 81bc5a82cc5b, d3b75910232f
Create Date: 2026-01-09 14:41:13.514020

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '756332cf4121'
down_revision: Union[str, Sequence[str], None] = ('81bc5a82cc5b', 'd3b75910232f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
