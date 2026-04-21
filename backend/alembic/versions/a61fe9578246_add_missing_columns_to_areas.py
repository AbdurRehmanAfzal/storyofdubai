"""add_missing_columns_to_areas

Revision ID: a61fe9578246
Revises: 001_initial_schema
Create Date: 2026-04-20 19:57:54.269146

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = 'a61fe9578246'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing columns to areas table
    op.add_column('areas', sa.Column('meta_description', sa.String(160), nullable=True))
    op.add_column('areas', sa.Column('character_tags', sa.String(500), nullable=True))


def downgrade() -> None:
    # Drop the added columns
    op.drop_column('areas', 'character_tags')
    op.drop_column('areas', 'meta_description')
