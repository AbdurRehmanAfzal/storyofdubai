"""add_missing_columns_to_developers_and_properties

Revision ID: 76414fec9ddc
Revises: 072a5b02f46f
Create Date: 2026-04-21 13:11:57.405216

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '76414fec9ddc'
down_revision = '072a5b02f46f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing columns to developers table
    op.add_column('developers', sa.Column('established_year', sa.Integer(), nullable=True))
    op.add_column('developers', sa.Column('total_projects', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('developers', sa.Column('ai_summary', sa.Text(), nullable=True))

    # Rename project_count to total_projects if it exists and total_projects was just added
    # Actually, we added total_projects, so let's just keep both for now

    # Add missing columns to properties table
    op.add_column('properties', sa.Column('title', sa.String(length=255), nullable=True))
    op.add_column('properties', sa.Column('size_sqft', sa.Float(), nullable=True))
    op.add_column('properties', sa.Column('composite_score', sa.Float(), nullable=True, server_default='0'))
    op.add_column('properties', sa.Column('affiliate_url', sa.String(length=500), nullable=True))


def downgrade() -> None:
    # Remove added columns from properties table
    op.drop_column('properties', 'affiliate_url')
    op.drop_column('properties', 'composite_score')
    op.drop_column('properties', 'size_sqft')
    op.drop_column('properties', 'title')

    # Remove added columns from developers table
    op.drop_column('developers', 'ai_summary')
    op.drop_column('developers', 'total_projects')
    op.drop_column('developers', 'established_year')
