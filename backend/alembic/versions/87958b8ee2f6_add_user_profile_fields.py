"""add_user_profile_fields

Revision ID: 87958b8ee2f6
Revises: 756332cf4121
Create Date: 2026-01-09 14:41:21.972990

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '87958b8ee2f6'
down_revision: Union[str, Sequence[str], None] = '756332cf4121'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add profile fields to users table for DM-15."""
    # Add supabase_id column
    op.add_column('users', sa.Column('supabase_id', sa.String(length=255), nullable=True))
    op.create_index(op.f('ix_users_supabase_id'), 'users', ['supabase_id'], unique=True)
    
    # Add profile fields
    op.add_column('users', sa.Column('age_group', sa.Enum('10u', '12u', '14u', '16u', '18u', 'college', 'adult', name='agegroup'), nullable=True))
    op.add_column('users', sa.Column('handedness', sa.Enum('left', 'right', 'switch', name='handedness'), nullable=True))
    op.add_column('users', sa.Column('height_cm', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Remove profile fields from users table."""
    op.drop_column('users', 'height_cm')
    op.drop_column('users', 'handedness')
    op.drop_column('users', 'age_group')
    op.drop_index(op.f('ix_users_supabase_id'), table_name='users')
    op.drop_column('users', 'supabase_id')
    
    # Drop enum types (PostgreSQL only)
    op.execute('DROP TYPE IF EXISTS agegroup')
    op.execute('DROP TYPE IF EXISTS handedness')
