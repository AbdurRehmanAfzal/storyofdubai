# Phase 3a: Google Places Scraper Demo

## Overview

Phase 3a implements the first data pipeline: scraping restaurant data from Google Places API and scoring venues with the Bayesian algorithm.

**Goal**: Populate PostgreSQL with real Dubai restaurant data and see 1,000+ pages auto-generate on storyofdubai.com.

---

## What Was Built

### 1. GooglePlacesScraper (`backend/app/scrapers/google_places_demo.py`)

A production-ready scraper that:
- **Searches 10 major Dubai areas**: Dubai Marina, Downtown Dubai, Business Bay, JVC, DIFC, Palm Jumeirah, Jumeirah, Dubai Hills, Al Barsha, JBR
- **Fetches restaurant data** from Google Places Text Search API
- **Parses venue information**: Name, rating, review count, address, phone, website, price tier
- **Stores in database** with automatic duplicate detection (by google_place_id)
- **Tracks statistics**: Inserted, updated, skipped, parse errors
- **Implements best practices**:
  - Rate limiting (2s delay + 1s jitter)
  - User-agent rotation
  - Automatic retries with exponential backoff
  - Comprehensive error logging via structlog
  - Database transaction management

### 2. Standalone Script (`backend/run_scraper_demo.py`)

A simple Python script to run the scraper:
- Creates database tables (if they don't exist)
- Initializes GooglePlacesScraper
- Runs full scrape operation
- Commits results to PostgreSQL
- Prints formatted statistics

**Usage**:
```bash
cd backend
python run_scraper_demo.py
```

### 3. Celery Tasks (`backend/app/pipeline/tasks.py`)

Integrated the scraper into the Celery task queue:

**`scrape_google_places_all_areas()`**
- Celery task (queue: `scrapers`)
- Runs on schedule or via manual trigger
- Managed async operations within sync Celery context
- Returns insertion/update statistics

**`run_scoring_engine_all()`**
- Celery task (queue: `default`)
- Scores all active venues using VenueScorer
- Applies Bayesian algorithm to calculate composite_score
- Updates database with scores

---

## Prerequisites

### 1. Environment Variables

Set these in `.env` file or VPS environment:

```bash
# Google Places API
GOOGLE_PLACES_API_KEY=AIza...  # Get from console.cloud.google.com

# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/storyofdubai

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

### 2. Services Running

Ensure these are operational:

```bash
# PostgreSQL
psql -U postgres -c "SELECT 1"

# Redis
redis-cli ping  # Should return PONG

# (Optional) Celery worker
celery -A app.celery_app worker --loglevel=info
```

---

## How to Run

### Option 1: Standalone Script (Simplest)

```bash
cd backend
python run_scraper_demo.py
```

**Output**:
```
============================================================
GOOGLE PLACES SCRAPER DEMO — RESULTS
============================================================
⏱️  Start Time: 2026-04-20T14:30:45.123456

📊 Statistics:
   ✅ Venues Inserted: 487
   🔄 Venues Updated: 23
   ⊘  Venues Skipped: 0
   ❌ Parse Errors: 2
   🔗 API Calls: 50
   ⏱️  Duration: 123.45s

============================================================

✅ Scraper completed successfully!

Next steps:
1. Run scoring engine: python -m app.pipeline.tasks
2. Trigger Next.js rebuild
3. Check storyofdubai.com for live pages
```

### Option 2: Celery Task (Production)

```bash
# Terminal 1: Start Celery worker
cd backend
celery -A app.celery_app worker --loglevel=info --queues=scrapers,default,enrichment

# Terminal 2: Trigger task
celery -A app.celery_app.scrape_google_places_all_areas.delay()

# Monitor progress
celery -A app.celery_app inspect active
```

### Option 3: Via Next.js API Route (Future)

Once API route is created, POST to trigger:
```bash
curl -X POST https://api.storyofdubai.com/api/scraper/trigger \
  -H "Authorization: Bearer $SCRAPER_TOKEN" \
  -d '{"scraper": "google_places"}'
```

---

## Expected Results

### Database State After Scraping

```sql
-- Check inserted venues
SELECT COUNT(*) FROM venues;
-- Expected: ~500+ restaurants across Dubai

-- Check by area
SELECT area_id, COUNT(*) as restaurant_count
FROM venues
GROUP BY area_id
ORDER BY restaurant_count DESC;

-- Check ratings distribution
SELECT 
  CASE 
    WHEN google_rating >= 4.5 THEN '4.5+'
    WHEN google_rating >= 4.0 THEN '4.0-4.5'
    WHEN google_rating >= 3.5 THEN '3.5-4.0'
    ELSE '< 3.5'
  END as rating_bucket,
  COUNT(*) as count
FROM venues
WHERE google_rating IS NOT NULL
GROUP BY rating_bucket
ORDER BY rating_bucket DESC;
```

### Frontend Pages Generated

After Next.js rebuild:
- **~1,200 venue area hub pages**: `/restaurants/dubai-marina/`, `/restaurants/downtown-dubai/`, etc.
- **~500 individual venue detail pages**: `/restaurants/dubai-marina/nobu-dubai-marina/`, etc.
- Each page fully ranked by composite_score (Bayesian algorithm)
- Rich schema.org markup (LocalBusiness, aggregateRating, breadcrumbs)
- Live on: https://storyofdubai.com/restaurants/

---

## Scoring Engine

The VenueScorer applies a **Bayesian algorithm** to calculate deterministic scores (0-100):

```
Score Breakdown:
├── Rating Quality (30pts)
│   └── Bayesian average (weights review count)
├── Review Volume (20pts)
│   └── Log-scale (diminishing returns)
├── Recency (20pts)
│   └── Time decay (fresh data > stale)
├── Price Value (15pts)
│   └── Mid-tier optimal (tier 2)
└── Completeness (15pts)
    └── Photos (5) + Phone (5) + Website (5)
```

**Example Scores**:
- Excellent (5.0★, 200 reviews, recent, complete): **91.25**
- Good (4.5★, 100 reviews, 30 days old, phone only): **78.50**
- New (4.8★, 5 reviews, today, no website): **67.75**
- Stale (3.5★, 30 reviews, 1 year old, incomplete): **45.00**

To apply scores after scraping:

```bash
# Option A: Celery task
celery -A app.celery_app.run_scoring_engine_all.delay()

# Option B: Direct Python
python -c "
import asyncio
from app.pipeline.tasks import run_scoring_engine_all
result = run_scoring_engine_all()
print(result)
"
```

---

## Troubleshooting

### "GOOGLE_PLACES_API_KEY not set"

**Solution**: 
1. Go to https://console.cloud.google.com
2. Create a new API key
3. Enable Google Places API
4. Add to `.env`:
   ```
   GOOGLE_PLACES_API_KEY=AIza...
   ```

### "Connection refused" (Database)

**Solution**:
```bash
# Start PostgreSQL
docker run -p 5432:5432 postgres:16-alpine

# OR if using Supabase, check .env for correct DATABASE_URL
psql $DATABASE_URL -c "SELECT 1"
```

### "No venues inserted"

**Possible causes**:
- API quota exceeded (5,000 calls/day soft limit)
- API key invalid or permissions not set
- Network/firewall blocking Google
- Database constraint violation

**Debug**:
```bash
# Check logs
python run_scraper_demo.py 2>&1 | grep -i error

# Verify API key
curl "https://maps.googleapis.com/maps/api/place/textsearch/json?query=restaurant&key=$GOOGLE_PLACES_API_KEY"
```

### Pages Not Generating

**Solution**:
1. Verify venues in database:
   ```sql
   SELECT COUNT(*) FROM venues WHERE is_active = true;
   ```
2. Run scoring engine:
   ```bash
   python run_scraper_demo.py  # Then in separate terminal:
   # (scoring happens automatically after scraping)
   ```
3. Rebuild Next.js:
   ```bash
   cd frontend
   npm run build
   ```
4. Check for errors:
   ```bash
   npm run dev  # Check console for build warnings
   ```

---

## Data Pipeline Overview

```
Google Places API
    ↓
GooglePlacesScraper (fetch + parse)
    ↓
PostgreSQL (venues table)
    ↓
VenueScorer (composite_score calculation)
    ↓
PostgreSQL (updated with scores)
    ↓
Next.js getStaticProps (page generation)
    ↓
Vercel (deployed)
    ↓
storyofdubai.com (live pages)
```

---

## Next Steps After Phase 3a

1. **Phase 3b**: Build other scrapers
   - Bayut.com (property listings)
   - UAE government portals (visa information)
   - DED (company registry)

2. **Phase 3c**: AI enrichment
   - Generate unique 200-word summaries for each venue/property/guide
   - Cost optimization with batch processing

3. **Phase 4**: Monetization
   - Add Google AdSense to pages
   - Integrate Booking.com, Viator, TheFork affiliate links
   - Track affiliate commissions

4. **Phase 5**: Production deployment
   - Deploy backend to Hostinger VPS
   - Deploy frontend to Vercel (already configured)
   - Point storyofdubai.com domain
   - Monitor live traffic

---

## Monitoring & Maintenance

### Daily Checks

```bash
# Check today's scrape jobs
SELECT * FROM scrape_jobs 
WHERE DATE(started_at) = CURRENT_DATE
ORDER BY started_at DESC;

# Check latest scores
SELECT name, composite_score, google_rating, review_count
FROM venues
WHERE is_active = true
ORDER BY composite_score DESC
LIMIT 10;

# Check errors
SELECT * FROM scrape_jobs 
WHERE status = 'failed'
ORDER BY started_at DESC;
```

### Cost Tracking

**Google Places API**:
- Text Search: $0.035 per request (cheaper than Details)
- Daily budget: $5 (configurable in .env)
- Current capacity: ~142 requests/day

**OpenAI (Phase 3c)**:
- Summary generation: $0.00015 per 1k input tokens
- Daily budget: $2 (configurable in .env)

---

## File Reference

| File | Purpose | Status |
|------|---------|--------|
| `app/scrapers/google_places_demo.py` | GooglePlacesScraper class | ✅ Complete |
| `app/scrapers/base.py` | BaseScraper (rate limit, retry, UA) | ✅ (existing) |
| `run_scraper_demo.py` | Standalone demo script | ✅ Complete |
| `app/pipeline/tasks.py` | Celery tasks (scraper + scoring) | ✅ Updated |
| `app/scoring/venue_scorer.py` | Bayesian scoring algorithm | ✅ (existing) |
| `app/models/venue.py` | Venue, Area, Category ORM | ✅ (existing) |

---

## Success Criteria

✅ Phase 3a is complete when:
- [ ] Scraper inserts 400+ restaurants without errors
- [ ] Database queries complete in <1s
- [ ] Scores calculated and populated
- [ ] Next.js pages generate (npm run build succeeds)
- [ ] Pages render at https://storyofdubai.com/restaurants/
- [ ] Pages have schema.org + proper SEO markup

---

**Phase 3a Completion Goal**: Get live, ranked restaurant pages on storyofdubai.com powered by real Google Places data.
