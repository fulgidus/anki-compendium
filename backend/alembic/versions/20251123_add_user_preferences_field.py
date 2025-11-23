"""add user preferences field

Revision ID: 0b2c3d4e5f6a
Revises: ea82ac9c6d47
Create Date: 2025-11-23 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0b2c3d4e5f6a'
down_revision = 'ea82ac9c6d47'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add preferences JSONB column to users table
    op.add_column('users', sa.Column('preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    # Remove preferences column
    op.drop_column('users', 'preferences')
