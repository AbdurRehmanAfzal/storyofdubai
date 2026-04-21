"""fix_properties_name_column

Revision ID: 7750362af4a3
Revises: 76414fec9ddc
Create Date: 2026-04-21 13:12:22.874903

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '7750362af4a3'
down_revision = '76414fec9ddc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Make the name column nullable (it's a legacy column we're replacing with title)
    op.alter_column('properties', 'name',
               existing_type=sa.String(length=255),
               nullable=True)


def downgrade() -> None:
    # Make name non-null again
    op.alter_column('properties', 'name',
               existing_type=sa.String(length=255),
               nullable=False)
