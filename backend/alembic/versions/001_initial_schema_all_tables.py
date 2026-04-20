"""initial_schema_all_tables

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-04-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create areas table
    op.create_table(
        'areas',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug', name='uq_areas_slug'),
    )
    op.create_index('ix_areas_slug', 'areas', ['slug'], unique=True)

    # Create categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon', sa.String(length=100), nullable=True),
        sa.Column('parent_id', sa.UUID(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug', name='uq_categories_slug'),
    )
    op.create_index('ix_categories_slug', 'categories', ['slug'], unique=True)

    # Create venues table
    op.create_table(
        'venues',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('review_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('composite_score', sa.Float(), nullable=False),
        sa.Column('area_id', sa.UUID(), nullable=False),
        sa.Column('category_id', sa.UUID(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_scraped_at', sa.String(length=30), nullable=True),
        sa.Column('affiliate_url_thefork', sa.String(length=500), nullable=True),
        sa.Column('affiliate_url_booking', sa.String(length=500), nullable=True),
        sa.Column('google_place_id', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['area_id'], ['areas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_venues_slug', 'venues', ['slug'], unique=True)
    op.create_index('ix_venues_composite_score', 'venues', ['composite_score'])
    op.create_index('idx_venue_area_category_score', 'venues', ['area_id', 'category_id', 'composite_score'])

    # Create developers table
    op.create_table(
        'developers',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('project_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_developers_slug', 'developers', ['slug'], unique=True)

    # Create properties table
    op.create_table(
        'properties',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('area_id', sa.UUID(), nullable=False),
        sa.Column('developer_id', sa.UUID(), nullable=True),
        sa.Column('bedrooms', sa.Integer(), nullable=True),
        sa.Column('bathrooms', sa.Integer(), nullable=True),
        sa.Column('price_aed', sa.Integer(), nullable=True),
        sa.Column('price_bucket', sa.String(length=50), nullable=True),
        sa.Column('property_type', sa.String(length=50), nullable=True),
        sa.Column('completion_year', sa.Integer(), nullable=True),
        sa.Column('rental_yield', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_scraped_at', sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(['area_id'], ['areas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['developer_id'], ['developers.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_properties_slug', 'properties', ['slug'], unique=True)
    op.create_index('idx_property_area_bed_price', 'properties', ['area_id', 'bedrooms', 'price_aed'])

    # Create nationalities table
    op.create_table(
        'nationalities',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('iso_code', sa.String(length=2), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_nationalities_slug', 'nationalities', ['slug'], unique=True)
    op.create_index('ix_nationalities_iso_code', 'nationalities', ['iso_code'], unique=True)

    # Create visa_types table
    op.create_table(
        'visa_types',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('duration_months', sa.Integer(), nullable=True),
        sa.Column('processing_time_days', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_visa_types_slug', 'visa_types', ['slug'], unique=True)

    # Create visa_nationality_guides table
    op.create_table(
        'visa_nationality_guides',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('nationality_id', sa.UUID(), nullable=False),
        sa.Column('visa_type_id', sa.UUID(), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('requirements', sa.Text(), nullable=True),
        sa.Column('ai_guide', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['nationality_id'], ['nationalities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['visa_type_id'], ['visa_types.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_visa_nationality_guides_slug', 'visa_nationality_guides', ['slug'], unique=True)
    op.create_index('idx_visa_nationality_unique', 'visa_nationality_guides', ['nationality_id', 'visa_type_id'], unique=True)

    # Create companies table
    op.create_table(
        'companies',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('sector', sa.String(length=100), nullable=False),
        sa.Column('registration_year', sa.Integer(), nullable=True),
        sa.Column('freezone', sa.String(length=100), nullable=True),
        sa.Column('is_mainland', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('employee_count_range', sa.String(length=50), nullable=True),
        sa.Column('ai_summary', sa.Text(), nullable=True),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_scraped_at', sa.String(length=30), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_companies_slug', 'companies', ['slug'], unique=True)
    op.create_index('idx_company_sector_active', 'companies', ['sector', 'is_active'])

    # Create scrape_jobs table
    op.create_table(
        'scrape_jobs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('scraper_name', sa.String(length=100), nullable=False),
        sa.Column('started_at', sa.String(length=30), nullable=False),
        sa.Column('completed_at', sa.String(length=30), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('records_collected', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('records_failed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_log', sa.Text(), nullable=True),
        sa.Column('metadata_', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_scrape_job_scraper_name', 'scrape_jobs', ['scraper_name'])


def downgrade() -> None:
    op.drop_table('scrape_jobs')
    op.drop_table('visa_nationality_guides')
    op.drop_table('visa_types')
    op.drop_table('nationalities')
    op.drop_table('properties')
    op.drop_table('developers')
    op.drop_table('venues')
    op.drop_table('categories')
    op.drop_table('areas')
