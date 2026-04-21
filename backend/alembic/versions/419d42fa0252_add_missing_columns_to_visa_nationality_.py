"""add_missing_columns_to_visa_nationality_guides

Revision ID: 419d42fa0252
Revises: e856349cb9e9
Create Date: 2026-04-21 14:02:24.710196

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '419d42fa0252'
down_revision = 'e856349cb9e9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing columns to visa_nationality_guides table
    # Note: slug column already exists in the database, only add is_active
    op.add_column('visa_nationality_guides', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))


def downgrade() -> None:
    op.drop_column('visa_nationality_guides', 'is_active')
