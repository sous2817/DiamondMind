"""add_swing_metadata_columns

Revision ID: d3b75910232f
Revises: 
Create Date: 2026-01-05

Adds status tracking and user-friendly metadata to swings table:
- status: ENUM for tracking upload/processing state (DM-56)
- error_message: TEXT for storing error details (DM-56)
- title: VARCHAR for custom swing names (DM-57)
- notes: TEXT for user notes (DM-57)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd3b75910232f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM type for status (PostgreSQL only, SQLite will use VARCHAR)
    swing_status = postgresql.ENUM('pending', 'processing', 'completed', 'failed', name='swingstatus', create_type=False)
    
    # Check if we're using PostgreSQL
    conn = op.get_bind()
    if conn.dialect.name == 'postgresql':
        swing_status.create(conn, checkfirst=True)
        status_type = sa.Enum('pending', 'processing', 'completed', 'failed', name='swingstatus')
    else:
        # SQLite fallback - use VARCHAR
        status_type = sa.String(20)
    
    # Add columns (all nullable initially for safe migration)
    op.add_column('swings', sa.Column('status', status_type, nullable=True))
    op.add_column('swings', sa.Column('error_message', sa.Text(), nullable=True))
    op.add_column('swings', sa.Column('title', sa.String(255), nullable=True))
    op.add_column('swings', sa.Column('notes', sa.Text(), nullable=True))
    
    # Backfill existing swings with 'completed' status
    # Use ENUM cast for PostgreSQL, plain string for SQLite
    if bind.dialect.name == 'postgresql':
        op.execute("UPDATE swings SET status = 'completed'::swingstatus WHERE status IS NULL")
    else:
        op.execute("UPDATE swings SET status = 'completed' WHERE status IS NULL")
    
    # Make status NOT NULL after backfill
    op.alter_column('swings', 'status', nullable=False, server_default='processing')
    
    # Add index on status for efficient queries
    op.create_index('ix_swings_status', 'swings', ['status'])


def downgrade() -> None:
    # Remove index
    op.drop_index('ix_swings_status', table_name='swings')
    
    # Remove columns
    op.drop_column('swings', 'notes')
    op.drop_column('swings', 'title')
    op.drop_column('swings', 'error_message')
    op.drop_column('swings', 'status')
    
    # Drop ENUM type (PostgreSQL only)
    conn = op.get_bind()
    if conn.dialect.name == 'postgresql':
        sa.Enum(name='swingstatus').drop(conn, checkfirst=True)
