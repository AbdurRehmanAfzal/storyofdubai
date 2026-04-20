# Database Rules

Standards for database schema, migrations, and data management. Every change follows these rules.

---

## Migration Rules

### The Golden Rule: ALWAYS use Alembic, NEVER raw SQL

All schema changes go through Alembic. Never modify database directly or use raw SQL ALTER TABLE statements.

### Migration Workflow

1. **Make model changes** in `app/models/`:
```python
# app/models/venue.py
class Venue(BaseModel):
    __tablename__ = "venues"
    
    name = Column(String(255), nullable=False)
    composite_score = Column(Float, nullable=False)  # NEW COLUMN
```

2. **Generate migration** (Alembic auto-generates the SQL):
```bash
cd backend
alembic revision --autogenerate -m "add_composite_score_to_venues"
```

3. **Review generated migration** in `alembic/versions/`:
```python
# Check that the migration looks correct
# Edit if needed (but usually Alembic gets it right)
```

4. **Test migration locally**:
```bash
alembic upgrade head          # Apply
alembic downgrade -1          # Rollback
alembic upgrade head          # Apply again
```

5. **Test against development data**:
```bash
# Verify the change works with actual queries
pytest tests/test_venue.py
```

6. **Commit migration with code change**:
```bash
git add app/models/venue.py alembic/versions/001_*.py
git commit -m "feat: add composite score to venues"
```

7. **Deploy to VPS**:
```bash
# SSH to VPS, pull code, run migration
ssh deploy@vps
cd /app/storyofdubai
git pull origin main
alembic upgrade head
```

### Migration Naming Convention

```
alembic/versions/
├── 001_initial_schema.py
├── 002_add_restaurants_table.py
├── 003_add_composite_score_to_venues.py
├── 004_create_scrape_jobs_table.py
└── 005_add_index_on_area_category.py
```

**Format**: `{number:03d}_{description}.py`

**Description**: Lowercase, underscores, specific action (add_, create_, remove_, rename_)

### Never Edit Existing Migrations

```python
# ❌ BAD: Editing migration 001
# Instead of fixing, create migration 006

# ✅ GOOD: Create new migration if mistake found
# Migration 001: initial schema (as is)
# Migration 006: fix initial schema error

def upgrade():
    op.alter_column('venues', 'rating', ...)

def downgrade():
    op.alter_column('venues', 'rating', ...)
```

**Why?** Once deployed to production, Alembic tracks which migrations have run. Editing old ones breaks the tracking.

### Testing Migrations

```bash
# In development
alembic upgrade head          # Apply all
pytest tests/                 # Run tests
alembic downgrade -1          # Rollback one
alembic upgrade head          # Reapply
pytest tests/                 # Verify tests still pass

# In staging (before VPS)
docker run -e DATABASE_URL=... myapp:latest
alembic upgrade head
pytest tests/
```

---

## Index Strategy (Performance at 10k+ Pages)

### Critical Indexes (Already Defined)

Every query that appears in getStaticPaths or page rendering needs an index.

**Venues table**:
```python
# app/models/venue.py
class Venue(BaseModel):
    __tablename__ = "venues"
    __table_args__ = (
        Index("idx_venue_area_category_score", "area_id", "category_id", "composite_score"),
        Index("idx_venue_slug", "slug", unique=True),
        Index("idx_venue_active", "is_active"),
    )
    
    id = Column(Integer, primary_key=True)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    composite_score = Column(Float, nullable=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
```

**Properties table**:
```python
# app/models/property.py
class Property(BaseModel):
    __tablename__ = "properties"
    __table_args__ = (
        Index("idx_property_area_bed_price", "area_id", "bedrooms", "price_aed"),
        Index("idx_property_slug", "slug", unique=True),
    )
    
    id = Column(Integer, primary_key=True)
    slug = Column(String(255), unique=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id"))
    bedrooms = Column(Integer)
    price_aed = Column(Integer)
    is_active = Column(Boolean, default=True, index=True)
```

### Index Best Practices

1. **Index columns used in WHERE clauses**:
```python
# This query needs an index on (area_id, composite_score)
query = select(Venue).where(
    Venue.area_id == area_id
).order_by(Venue.composite_score.desc())
```

2. **Use composite indexes for common filter combinations**:
```python
# Index on (area_id, category_id, composite_score)
# This index covers all these queries:
# - WHERE area_id = ? AND category_id = ?
# - WHERE area_id = ? ORDER BY composite_score DESC
# - WHERE area_id = ? AND category_id = ? ORDER BY composite_score
```

3. **Unique indexes for natural keys** (not just PK):
```python
# Slug is unique per area+category
slug = Column(String(255), unique=True, index=True)
```

4. **Don't over-index** — too many indexes slow down writes:
```python
# ❌ BAD: Index every column
Index("idx_name"), Index("idx_rating"), Index("idx_review_count"), ...

# ✅ GOOD: Index columns used in queries
Index("idx_rating_score", "rating", "composite_score")
```

### Migration with Index

```python
# alembic/versions/006_add_composite_score_index.py
def upgrade():
    op.create_index(
        'idx_venue_area_category_score',
        'venues',
        ['area_id', 'category_id', 'composite_score']
    )

def downgrade():
    op.drop_index('idx_venue_area_category_score', 'venues')
```

---

## Data Retention Rules

### The Golden Rule: NEVER Hard Delete — Only Soft Delete

```python
# ❌ BAD: Hard delete (data is gone forever!)
await session.delete(venue)
await session.commit()

# ✅ GOOD: Soft delete (data preserved for audit trail)
venue.is_active = False
await session.commit()
```

### Soft Delete Pattern

Every model has `is_active` column:

```python
class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
```

When displaying data, always filter:

```python
# In services
stmt = select(Venue).where(Venue.is_active == True)

# In queries for page generation
all_venues = await session.execute(
    select(Venue).where(Venue.is_active == True)
)
```

### Data Retention by Type

| Data Type | Retention | Reason |
|-----------|-----------|--------|
| Venues/Properties/Companies | Forever (soft delete) | Need for page generation, audit trail |
| ScrapeJob records | Forever | Track what was scraped when |
| AI enrichment content | Last 3 versions | Can rollback if generation fails |
| Raw scrape HTML | 7 days | Disk space, can always re-scrape |
| API logs | 30 days | Compliance, troubleshooting |
| Error logs | 90 days | Debugging, compliance |

### Example: Soft Delete in Service

```python
# app/services/venue_service.py
class VenueService:
    async def delete(self, venue_id: int, session: AsyncSession):
        """Soft delete: mark inactive"""
        venue = await self.get_by_id(venue_id, session)
        if not venue:
            raise ValueError(f"Venue {venue_id} not found")
        
        venue.is_active = False
        venue.updated_at = datetime.utcnow()
        session.add(venue)
        await session.commit()
        
        # Invalidate cache
        await cache.delete(f"venue:{venue.slug}")
        
        return venue
```

---

## Connection & Session Rules

### In FastAPI Routes (Use Async)

```python
from app.database import AsyncSession

@router.get("/venues")
async def list_venues(
    session: AsyncSession = Depends(get_session),  # Injected
):
    # Async session automatically closed after response
    stmt = select(Venue).where(Venue.is_active == True)
    result = await session.execute(stmt)
    return result.scalars().all()
```

### In Celery Tasks (Use Sync)

```python
# Celery is synchronous, can't use async sessions
from app.database import SessionLocal

@app.task
def scrape_venues():
    session = SessionLocal()  # Sync session
    try:
        stmt = select(Venue).where(Venue.is_active == True)
        venues = session.execute(stmt).scalars().all()
        # Do work
    finally:
        session.close()  # ALWAYS close
```

### Connection Pool Settings

```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine

# Async engine (FastAPI)
async_engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,          # Max connections in pool
    max_overflow=5,        # Extra connections if needed
    pool_pre_ping=True,    # Verify connections before use
    echo=DEBUG,            # Log SQL if debugging
)

# Sync engine (Celery)
sync_engine = create_engine(
    SYNC_DATABASE_URL,
    pool_size=5,
    max_overflow=2,
    pool_recycle=3600,  # Recycle connections every hour
)
```

### Session Lifecycle

```python
# ✅ GOOD: Context manager (auto-closes)
async with AsyncSession(async_engine) as session:
    result = await session.execute(stmt)
    await session.commit()
    # Session auto-closed

# ✅ GOOD: Dependency injection (FastAPI auto-closes)
@router.get("/")
async def get_data(session: AsyncSession = Depends(get_session)):
    # Use session
    # FastAPI closes after response
    pass

# ❌ BAD: Manual session not closed
session = SessionLocal()
result = session.execute(stmt)
# Session never closed! Connection leak!
```

---

## Naming Conventions

### Tables

```
# ✅ GOOD: Plural snake_case
venues              # Restaurant/venue/attraction listings
properties          # Real estate listings
visa_guides         # Visa information by country
companies           # Company registry
scrape_jobs         # Scraper execution records
ai_enrichments      # AI-generated content versions
areas               # Dubai areas/neighborhoods
categories          # Venue categories (restaurant, hotel, etc.)

# ❌ BAD
venue               # Singular (should be venues)
VenueData           # CamelCase (should be snake_case)
restaurant_venue    # Redundant (use venues)
```

### Columns

```
# ✅ GOOD: snake_case, descriptive
id                      # Primary key
created_at              # Timestamp
updated_at              # Timestamp
is_active               # Boolean flag
composite_score         # Calculated score
area_id                 # Foreign key (singular_id)
category_id             # Foreign key
last_scraped_at         # Specific timestamp

# ❌ BAD
Id                      # CamelCase
created                 # Missing _at
score                   # Too generic (composite_score?)
active                  # Missing is_ prefix
area_code               # Wrong suffix (should be area_id)
```

### Foreign Keys

```
# Pattern: {table_singular}_id

class Venue(Base):
    __tablename__ = "venues"
    
    area_id = Column(Integer, ForeignKey("areas.id"))      # ✓ Correct
    category_id = Column(Integer, ForeignKey("categories.id"))
    developer_id = Column(Integer, ForeignKey("developers.id"))
    
    # NOT: area_fk, areaId, AreaId, area

class Review(Base):
    __tablename__ = "reviews"
    
    venue_id = Column(Integer, ForeignKey("venues.id"))    # ✓ Correct
```

### Junction Tables (Many-to-Many)

```
# Pattern: {table1}_{table2} alphabetically

# If venues have multiple tags and vice versa:
# Table name: area_category (areas + categories, alphabetically)

class AreaCategory(Base):
    __tablename__ = "area_category"  # Not category_area
    
    area_id = Column(Integer, ForeignKey("areas.id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), primary_key=True)
```

---

## Query Performance

### Measuring Query Speed

```python
import time
from sqlalchemy import event

# Enable query logging
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Or manually time
start = time.time()
venues = await session.execute(stmt)
elapsed = time.time() - start
print(f"Query took {elapsed:.3f}s")
```

### Query Optimization Checklist

- [ ] Indexes on WHERE clause columns
- [ ] Use `joinedload()` instead of lazy loading
- [ ] Limit result set (getStaticPaths shouldn't fetch ALL venues)
- [ ] Use EXPLAIN ANALYZE to verify index usage
- [ ] Cache frequently-accessed data
- [ ] Consider pagination for large result sets

### Common Performance Problems

| Problem | Cause | Solution |
|---------|-------|----------|
| Slow list queries | Missing index | Add index on filter columns |
| N+1 queries | Lazy loading relationships | Use joinedload() or selectinload() |
| Timeout on page gen | Fetching all 10k at once | Use pagination or cursor-based export |
| High connection pool exhaustion | Unclosed sessions | Use context managers, verify .close() |

---

## Backup Strategy

### Development (Supabase free tier)
Automatic daily backups, 7-day retention. Accessible via Supabase dashboard.

### Production (Self-hosted PostgreSQL)

```bash
# Daily backup script: /app/scripts/backup-db.sh
#!/bin/bash
pg_dump -h localhost -U postgres storyofdubai > \
  /backups/storyofdubai_$(date +%Y%m%d_%H%M%S).sql

# Keep only last 7 days
find /backups -name "storyofdubai_*.sql" -mtime +7 -delete
```

**Cron job**:
```
0 2 * * * /app/scripts/backup-db.sh  # 2 AM daily
```

---

**Last Updated**: 2026-04-20  
**For**: Story of Dubai Database  
**Enforced by**: Alembic, code review, migration testing
