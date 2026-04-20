# Database Rules

## PostgreSQL Setup
- **Version**: 16+
- **Encoding**: UTF-8
- **Collation**: en_US.UTF-8
- **Extensions**: None required initially (pg_trgm if doing full-text search later)

## Schema Design Principles
- **Denormalize strategically**: Store computed fields (composite_score) for performance
- **Temporal data**: Always include created_at, updated_at (NOT NULL, with defaults)
- **Soft deletes**: is_active (BOOLEAN NOT NULL DEFAULT true), never CASCADE DELETE
- **Indexing**: Add indexes only for queried columns (avoid over-indexing)
- **No nullable foreign keys**: If a relationship is required, NOT NULL the FK

## Core Tables

### pages
```
id (BIGSERIAL PRIMARY KEY)
slug (VARCHAR UNIQUE NOT NULL)
title (VARCHAR NOT NULL)
meta_description (TEXT)
content (TEXT)
composite_score (DECIMAL)
page_type (VARCHAR: 'restaurant', 'property', 'visa', 'company', 'experience')
is_active (BOOLEAN DEFAULT true)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

### restaurants
```
id (BIGSERIAL PRIMARY KEY)
page_id (BIGINT FK → pages)
name (VARCHAR NOT NULL)
area (VARCHAR)
cuisine_type (VARCHAR)
rating (DECIMAL)
review_count (INTEGER)
google_places_id (VARCHAR UNIQUE)
address (TEXT)
phone (VARCHAR)
website (VARCHAR)
is_active (BOOLEAN DEFAULT true)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

### ai_enrichments
```
id (BIGSERIAL PRIMARY KEY)
page_id (BIGINT FK → pages)
content (TEXT NOT NULL)
similarity_score (DECIMAL) # 0-1, check before saving
model_used (VARCHAR: 'gpt-4o-mini')
is_active (BOOLEAN DEFAULT true)
created_at (TIMESTAMP)
```

### scoring_results
```
id (BIGSERIAL PRIMARY KEY)
page_id (BIGINT FK → pages)
factor_name (VARCHAR)
factor_value (DECIMAL)
composite_score (DECIMAL)
created_at (TIMESTAMP)
```

## Migrations
- **Tool**: Alembic
- **Location**: `backend/alembic/versions/`
- **Naming**: `001_create_pages_table.py`
- **Command**: `alembic upgrade head`
- **Rollback**: `alembic downgrade -1`
- **Never modify existing migrations** — create new ones if needed

## Query Best Practices
- **Always use async**: `async with AsyncSession() as session:`
- **Limit results**: Never SELECT * without LIMIT (500 max default)
- **Use indexes**: Query planner should show index scans, not seq scans
- **Batch inserts**: Use executemany, not individual inserts
- **Connection pooling**: FastAPI handles this with async sessions
- **No N+1 queries**: Use joinedload, selectinload for relationships

## Backup Strategy
- **Frequency**: Daily automated backup (Supabase handles this initially)
- **Retention**: 7 days
- **Restore**: Test restore monthly
- **Migration to self-hosted**: When moving to Hostinger, set up pg_dump daily

## Performance Considerations
- **Slow query log**: Log queries >1 second
- **Index on**: id, slug, page_type, is_active, created_at
- **Avoid full-text search** until data > 100k rows (use LIKE with LIMIT instead)
- **Vacuum**: Autovacuum enabled (default)
- **Connection limit**: 20 concurrent connections (Supabase free tier)
