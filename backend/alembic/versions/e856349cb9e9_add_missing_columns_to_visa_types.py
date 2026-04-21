"""add_missing_columns_to_visa_types

Revision ID: e856349cb9e9
Revises: 785744028804
Create Date: 2026-04-21 14:00:33.770296

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = 'e856349cb9e9'
down_revision = '785744028804'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing columns to visa_types table (per updated ORM model)
    op.add_column('visa_types', sa.Column('duration_days', sa.Integer(), nullable=True))
    op.add_column('visa_types', sa.Column('cost_aed', sa.Integer(), nullable=True))
    op.add_column('visa_types', sa.Column('processing_days', sa.Integer(), nullable=True))
    op.add_column('visa_types', sa.Column('ai_guide', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('visa_types', 'ai_guide')
    op.drop_column('visa_types', 'processing_days')
    op.drop_column('visa_types', 'cost_aed')
    op.drop_column('visa_types', 'duration_days')
