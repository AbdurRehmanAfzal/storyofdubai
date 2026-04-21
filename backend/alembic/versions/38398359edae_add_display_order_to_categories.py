"""add_display_order_to_categories

Revision ID: 38398359edae
Revises: a61fe9578246
Create Date: 2026-04-20 19:58:51.246471

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '38398359edae'
down_revision = 'a61fe9578246'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add display_order column to categories table with default value 0
    op.add_column('categories', sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    # Drop the added column
    op.drop_column('categories', 'display_order')
