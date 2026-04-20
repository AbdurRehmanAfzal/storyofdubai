# Architecture Rules

## Backend (FastAPI)
- **Entry point**: `backend/app/main.py` initializes FastAPI app, mounts routers, sets up middleware
- **Routes**: All under `app/api/v1/` — one file per resource (restaurants.py, properties.py, etc.)
- **Database**: SQLAlchemy ORM with async sessions, context managers for lifecycle
- **Models**: Pydantic v2 for request/response schemas (in `app/models/schemas.py`)
- **Database models**: SQLAlchemy in `app/models/db/` (one file per entity)
- **Business logic**: In `app/` subdirectories (scrapers/, pipeline/, scoring/, ai_enrichment/)
- **Error handling**: Raise HTTPException with proper status codes and detail messages
- **Logging**: Use `logging.getLogger(__name__)`, structured logs with context

## Frontend (Next.js)
- **Pages**: `pages/` directory (Pages Router for SSG at 10k+ pages, NOT App Router)
- **Components**: Reusable in `components/`, organized by feature
- **API client**: `lib/api.ts` — single source of truth for backend calls
- **Utils**: `lib/` for helpers (formatting, validation, fetching)
- **Styles**: TailwindCSS classes inline, CSS modules for complex styling
- **Static generation**: getStaticPaths + getStaticProps in pages/[...slug].tsx
- **ISR config**: revalidate: 86400 (24 hours) on all static pages

## Database Schema
- **Entities**: Pages, Restaurants, Properties, Visa_Info, Companies, Experiences
- **Scoring**: Separate scoring_results table, updated by scoring engine
- **AI Content**: ai_enrichments table (id, entity_id, entity_type, content, created_at, similarity_score)
- **Audit**: is_active, created_at, updated_at on all tables
- **No cascading deletes** — soft delete only (is_active=False)

## Data Pipeline
1. **Scraper** → raw data (PostgreSQL)
2. **Cleaning** → normalize, deduplicate, validate
3. **Scoring** → composite_score calculation
4. **Enrichment** → GPT-4o-mini generates unique content, saved with similarity_score
5. **Page Generation** → getStaticPaths/getStaticProps reads from PostgreSQL
6. **Serving** → Cloudflare → Vercel (frontend) or Hostinger (API)

## Celery Worker Pattern
- **Broker**: Redis (CELERY_BROKER_URL)
- **Result backend**: Redis (CELERY_RESULT_BACKEND)
- **Tasks**: In `app/tasks/` — long-running scrapers, enrichment, scoring
- **Schedules**: Configured in `celery_config.py` (e.g., scrape every 24h, enrich every 12h)
- **Error handling**: Retry on failure, log exceptions, never leave orphaned tasks
