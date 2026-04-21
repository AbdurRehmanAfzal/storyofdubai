"""fix_venue_slug_unique_constraint

Revision ID: 072a5b02f46f
Revises: 38398359edae
Create Date: 2026-04-21 10:22:43.887048

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '072a5b02f46f'
down_revision = '38398359edae'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the global unique constraint on slug
    op.drop_index('ix_venues_slug', table_name='venues')

    # Add a simple index on slug (not unique, allows duplicates per area)
    op.create_index('ix_venues_slug', 'venues', ['slug'], unique=False)

    # The composite unique constraint (slug, area_id) is already in the table via UniqueConstraint


def downgrade() -> None:
    # Restore the old unique index
    op.drop_index('ix_venues_slug', table_name='venues')
    op.create_index('ix_venues_slug', 'venues', ['slug'], unique=True)
