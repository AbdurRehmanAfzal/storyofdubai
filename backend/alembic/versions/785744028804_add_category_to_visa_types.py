"""add_category_to_visa_types

Revision ID: 785744028804
Revises: 7750362af4a3
Create Date: 2026-04-21 13:44:56.292314

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '785744028804'
down_revision = '7750362af4a3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add category column to visa_types table
    op.add_column('visa_types', sa.Column('category', sa.String(length=50), nullable=False, server_default='tourist'))
    op.create_index('ix_visa_types_category', 'visa_types', ['category'])


def downgrade() -> None:
    op.drop_index('ix_visa_types_category', 'visa_types')
    op.drop_column('visa_types', 'category')
