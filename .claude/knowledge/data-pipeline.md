# Data Pipeline Knowledge

Complete understanding of how data flows from scrapers to generated pages, including timing, costs, and failure modes.

---

## Pipeline Flow

```
Scrapers → Raw Data → Validator → Scorer → AI Enricher → Page Generator → CDN Cache → Users
  ↓          ↓         ↓          ↓          ↓            ↓               ↓
 2 AM    Database    Celery    Celery      Celery      Vercel         Cloudflare
        (PostgreSQL)  Beat      Beat        Beat                         
```

### Timing (All Dubai Time: UTC+4)

| Task | Time | Frequency | Duration | Next |
|------|------|-----------|----------|------|
| Google Places Scrape | 2:00 AM | Daily | 30 min | Bayut |
| Bayut Property Scrape | 3:00 AM | Every 2 days | 45 min | Visa |
| Visa Portal Scrape | 1:00 AM | Weekly (Sun) | 10 min | Companies |
| Company Scrape | 1:30 AM | Daily | 20 min | Scoring |
| **Scoring Engine** | **4:00 AM** | **Daily** | **5 min** | **Enrichment** |
| **AI Enrichment** | **5:00 AM** | **Daily** | **1 hour** | **Page Build** |
| **Next.js Page Build** | **6:00 AM** | **Daily** | **15 min** | **Deployment** |

### Execution Order

Scrapers run in **parallel** (different sources), but:
1. All scrapers must complete before scoring starts
2. Scoring must complete before enrichment starts
3. Enrichment must complete before page generation starts

---

## Celery Task Schedule

**File**: `backend/app/pipeline/schedule.py`

```python
CELERY_BEAT_SCHEDULE = {
    # Scrapers
    'scrape-google-places': {
        'task': 'app.pipeline.tasks.scrape_google_places',
        'schedule': crontab(hour=2, minute=0),  # 2 AM Dubai time
    },
    'scrape-bayut': {
        'task': 'app.pipeline.tasks.scrape_bayut',
        'schedule': crontab(hour=3, minute=0, day_of_week='0,2,4,6'),  # Every 2 days
    },
    'scrape-visa-portal': {
        'task': 'app.pipeline.tasks.scrape_visa_portal',
        'schedule': crontab(hour=1, minute=0, day_of_week=6),  # Sunday 1 AM
    },
    'scrape-companies': {
        'task': 'app.pipeline.tasks.scrape_companies',
        'schedule': crontab(hour=1, minute=30),  # 1:30 AM daily
    },
    # Processing pipeline
    'run-scoring-engine': {
        'task': 'app.pipeline.tasks.run_scoring',
        'schedule': crontab(hour=4, minute=0),  # 4 AM (after all scrapers)
    },
    'run-ai-enrichment': {
        'task': 'app.pipeline.tasks.run_ai_enrichment',
        'schedule': crontab(hour=5, minute=0),  # 5 AM (after scoring)
    },
    'trigger-nextjs-build': {
        'task': 'app.pipeline.tasks.trigger_nextjs_build',
        'schedule': crontab(hour=6, minute=0),  # 6 AM (after enrichment)
    },
}
```

---

## Scoring Engine

**File**: `backend/app/scoring/`

One scorer per entity type. All inherit from `BaseScorer`.

**Scores are 0-100** (stored as `composite_score` on entity).  
**DETERMINISTIC**: Same inputs always produce same score (no randomness).  
**Weights** defined in: `backend/app/scoring/weights.py`

### Scoring Algorithm (Venue Example)

```python
# backend/app/scoring/venue_scorer.py
composite_score = (
    (rating_normalized * 0.30) +           # 30% weight
    (review_count_normalized * 0.20) +     # 20% weight
    (recency_normalized * 0.20) +          # 20% weight
    (completeness_normalized * 0.15) +     # 15% weight
    (engagement_normalized * 0.15)         # 15% weight
) * 100  # Scale to 0-100

# Normalization (each factor 0-1)
rating_normalized = rating / 5.0  # 4.8/5 = 0.96
review_count_normalized = min(log(reviews + 1) / log(10000), 1.0)
recency_normalized = max(1 - (days_since_update / 365), 0)  # Recent = higher
completeness_normalized = filled_fields / total_fields  # What % of fields are filled
engagement_normalized = (page_views + clicks) / 1000  # Popularity metric
```

### Key Metrics Stored

For each venue:
- `rating` — Google Places rating (0-5)
- `review_count` — Number of reviews
- `last_updated_at` — When data was last scraped
- `fields_populated` — How many data fields are filled
- `composite_score` — Final 0-100 score (stored in DB)

### Usage

```python
# Run scoring
python -m app.scoring.run --entity-type venue --recalculate

# Check top-scored venues
SELECT name, area, composite_score FROM venues
  WHERE is_active = true
  ORDER BY composite_score DESC
  LIMIT 20;
```

---

## AI Enrichment Pipeline

**File**: `backend/app/ai_enrichment/`

Generates unique 200-word page introductions for each entity using GPT-4o-mini.

### Configuration

```python
# backend/app/ai_enrichment/config.py
MODEL = "gpt-4o-mini"  # Cost ~$0.0002 per page
ONLY_ENRICH_ABOVE_SCORE = 0.60  # Only enrich top 60% by composite_score
MAX_COST_PER_RUN = 2.00  # Hard stop at $2/day (Redis counter)
MIN_CONTENT_LENGTH = 150  # Words (reject shorter outputs)
SIMILARITY_THRESHOLD = 0.85  # Max allowed cosine similarity to other intros
```

### Process

1. **Fetch entities** missing `ai_summary` or older than 30 days
   ```sql
   SELECT * FROM venues
     WHERE is_active = true
     AND composite_score > 60
     AND (ai_summary IS NULL OR updated_ai_at < NOW() - INTERVAL '30 days')
     LIMIT 100;
   ```

2. **Build prompt** with entity context
   ```
   Write a unique, engaging 200-word introduction for [Restaurant Name] in [Area].
   
   Details:
   - Cuisine: {cuisine_type}
   - Rating: {rating}/5 ({review_count} reviews)
   - Address: {address}
   - Price range: {price_range}
   - Highlights: {highlights}
   
   Requirements:
   - SEO-friendly (include "{cuisine_type} restaurant in {area}" naturally)
   - Engaging, authentic tone
   - Include call-to-action
   - ~200 words
   ```

3. **Call OpenAI** with GPT-4o-mini (fast + cheap)

4. **Check similarity** (cosine similarity to other intros)
   - If similarity < 0.85: SAVE (unique content)
   - If similarity >= 0.85: SKIP (too similar to existing)

5. **Validate output**
   - Check word count >= 150
   - Check no jailbreak attempts
   - Check contains required keywords

6. **Store** in `ai_enrichments` table
   ```python
   class AIEnrichment(Base):
       __tablename__ = "ai_enrichments"
       
       entity_id: int        # Venue, Property, etc.
       entity_type: str      # "venue", "property", "visa"
       ai_summary: str       # Generated content
       similarity_score: float  # Cosine similarity to others
       cost_usd: float       # ~$0.0002
       created_at: datetime
   ```

### Cost Example

- 500 pages × $0.0002 = $0.10/day
- 500 pages × 7 days = $0.70/week
- 500 pages × 30 days = $3.00/month

**Budget**: $3-5/month (sustainable)

---

## Redis Cache Strategy

**Cache Keys & TTLs**:

```python
# Individual entity data (rarely changes)
f"venue:{slug}" → JSON of venue
TTL: 24 hours

# Rankings/lists (updated by scoring)
f"venue_rankings:{area_slug}:{category_slug}" → Sorted list
TTL: 1 hour

# Page paths (used by getStaticPaths)
f"page_paths:venue_area" → List of all venue paths
TTL: 6 hours

# Budget trackers (reset daily)
f"scrape_cost:{YYYY-MM-DD}" → Daily spend counter
f"enrichment_cost:{YYYY-MM-DD}" → Daily OpenAI spend
TTL: 86400 seconds

# Session/temp (short lived)
f"scraper_session:{scraper_id}" → Session state
TTL: 3600 seconds
```

### Cache Invalidation

When data changes, invalidate cache:

```python
# After scraper updates venue
await cache.delete(f"venue:{venue.slug}")
await cache.delete(f"page_paths:venue_area")  # Full list changed
await cache.delete(f"venue_rankings:{area}:{category}")

# After scoring runs
await cache.delete(f"venue_rankings:*")  # All rankings changed

# After AI enrichment
await cache.delete(f"venue:{venue.slug}")  # Content changed
```

---

## Page Generation

**Framework**: Next.js 14 with Pages Router

### getStaticPaths

```typescript
// frontend/pages/venues/[area]/[slug].tsx
export async function getStaticPaths() {
  // Fetch all active venue paths from API
  const paths = await fetch(`${API_URL}/api/v1/page-paths/venues/`)
    .then(r => r.json())
    .then(data => data.data);
  
  return {
    paths: paths.map(p => ({
      params: {
        area: p.area,
        slug: p.slug
      }
    })),
    fallback: 'blocking'  // Generate new pages on-demand
  }
}
```

### getStaticProps

```typescript
export async function getStaticProps({ params }) {
  // Fetch venue data from API
  const venue = await fetch(
    `${API_URL}/api/v1/venues/${params.slug}/`
  ).then(r => r.json()).then(d => d.data);
  
  if (!venue) {
    return { notFound: true }  // 404
  }
  
  return {
    props: { venue },
    revalidate: 86400  // ISR: refresh every 24 hours
  }
}
```

### Build Performance

- **getStaticPaths**: Fetch 10k paths = ~5 seconds
- **getStaticProps**: Fetch + render 10k pages = ~15 minutes
- **Fallback**: New/updated pages generated on-demand (blocking)
- **Total build time**: ~20 minutes

---

## Data Volume & Performance

| Stage | Input | Output | Time | Cost |
|-------|-------|--------|------|------|
| **Scrape** | APIs | 1,000 new entities | 30 min | $0.07 (Google Places) |
| **Validate** | 1,000 raw | 950 valid (95%) | 2 min | $0 |
| **Score** | 950 valid | 950 scored | 3 min | $0 |
| **Enrich** | 950 scored | 600 enriched* | 30 min | $0.12 (OpenAI) |
| **Generate** | 600 + 9k old | 10k pages | 15 min | $0 |
| **Serve** | 10k pages | CDN cache | — | $0.50/mo |

*Only top 60% by score get AI enrichment (limit cost)

**Monthly cost**: ~$5 (Google Places) + ~$3 (OpenAI) + $0.50 (CDN) = **~$8.50/month**

---

## Monitoring & Health Checks

```bash
# Check scraper job status
psql $DATABASE_URL -c "
  SELECT scraper_name, status, COUNT(*) FROM scrape_jobs
  WHERE started_at > NOW() - INTERVAL '24 hours'
  GROUP BY scraper_name, status;
"

# Check data freshness
psql $DATABASE_URL -c "
  SELECT entity_type, COUNT(*), MAX(updated_at) as last_update
  FROM entities
  WHERE is_active = true
  GROUP BY entity_type;
"

# Check enrichment coverage
psql $DATABASE_URL -c "
  SELECT 
    entity_type,
    COUNT(*) as total,
    COUNT(ai_summary) as enriched,
    ROUND(100.0 * COUNT(ai_summary) / COUNT(*), 1) as pct_enriched
  FROM entities
  WHERE is_active = true
  GROUP BY entity_type;
"

# Check page generation status (from Vercel)
curl https://api.vercel.com/v6/deployments \
  -H "Authorization: Bearer $VERCEL_TOKEN" | jq '.deployments[0]'
```

---

## Error Handling & Recovery

```
Scraper fails
  ↓
  Log to app.log
  ↓
  Send Sentry alert
  ↓
  Skip that source, continue with others
  ↓
  If all fail: manual investigation next morning

Scoring fails
  ↓
  Log error
  ↓
  Use default score (0.5)
  ↓
  Continue to next entity

Enrichment fails
  ↓
  Log error + entity_id
  ↓
  Fallback to entity description (first 200 chars)
  ↓
  Continue to next entity

Page generation fails
  ↓
  Log to Vercel build logs
  ↓
  Try next page
  ↓
  Flag failed pages for manual review
  ↓
  Use ISR to regenerate on next access
```

---

## Adding a New Data Source

1. **Create scraper**: `backend/app/scrapers/new_source.py`
2. **Implement BaseScraper**: `async def scrape()` and `async def parse()`
3. **Create model**: `backend/app/models/new_entity.py`
4. **Create Alembic migration**: Define table schema
5. **Create scorer**: `backend/app/scoring/new_scorer.py`
6. **Update pipeline scheduler**: Add to `backend/app/pipeline/schedule.py`
7. **Create page template**: `frontend/pages/new-entity/[slug].tsx`
8. **Test end-to-end**:
   - Run scraper locally: `python -m app.scrapers.new_source --dry-run`
   - Run scorer: `python -m app.scoring.run --entity-type new_entity`
   - Generate pages: `npm run build` in frontend
9. **Monitor**: Check ScrapeJob records and page generation

---

**Last Updated**: 2026-04-20  
**For**: Story of Dubai Data Pipeline  
**Daily Volume**: ~1,000 new entities, 50+ updates  
**Monthly Cost**: ~$8.50  
**Page Coverage**: 10,000+ static pages generated daily

### 1. Raw Data (Scrapers)
**Input**: External APIs (Google Places, Bayut, etc.)  
**Output**: PostgreSQL tables (restaurants, properties, visa_info, etc.)  
**Frequency**: Daily at off-peak hours (2-4 AM Dubai time)  
**Format**: Structured, schema-validated

### 2. Cleaning
**Task**: Normalize, validate, deduplicate  
**Runs after**: Scraper completes  
**Actions**:
- Trim whitespace, standardize text encoding (UTF-8)
- Validate required fields (name, location, etc.)
- Lowercase lowercase categories (cuisine_type, area)
- Remove duplicates (by unique_key: google_places_id, url, etc.)
- Merge data if same entity found in multiple sources

### 3. Scoring
**Task**: Calculate composite_score for each entity  
**Runs**: Every 12 hours (after cleaning)  
**Algorithm**: Weighted combination of factors
```python
composite_score = (
    (rating_normalized * 0.3) +
    (review_count_normalized * 0.2) +
    (recency_score * 0.2) +
    (completeness_score * 0.15) +
    (engagement_score * 0.15)
)
```

**Scoring factors**:
- **rating_normalized**: (rating / 5) → 0-1
- **review_count_normalized**: log(review_count + 1) / log(10000) → capped 0-1
- **recency_score**: (1 - days_since_update / 365) → 0-1
- **completeness_score**: (fields_filled / total_fields) → 0-1
- **engagement_score**: (clicks + shares + affiliate clicks) / 100 → 0-1

### 4. Enrichment (AI Content Generation)
**Task**: Generate unique 200-word page intro for each entity  
**Runs**: Every 6 hours for entities with score > 0.6  
**Model**: GPT-4o-mini (cost: ~$0.0002 per page)  

**Process**:
```
1. Fetch entity from DB (restaurant, property, visa type, etc.)
2. Build prompt with entity data (name, rating, address, cuisine, etc.)
3. Call OpenAI with GPT-4o-mini
4. Calculate similarity_score (cosine similarity to other intros)
5. If similarity < 0.85: Save to ai_enrichments table
6. If similarity >= 0.85: Log and skip (duplicate content)
```

**Prompt template** (restaurant example):
```
Write a unique, engaging 200-word introduction for a Dubai restaurant web page.

Restaurant: {name}
Area: {area}
Cuisine: {cuisine_type}
Rating: {rating}/5 ({review_count} reviews)
Address: {address}
Highlights: {highlights}

Requirements:
- SEO-friendly (include "{cuisine_type} restaurant in {area}" naturally)
- Engaging tone for tourists and locals
- Include call-to-action (reservation link)
- No marketing jargon, be authentic
- Unique angle (not generic "Dubai is great" content)

Content:
```

### 5. Page Generation
**Task**: Build 10,000+ static HTML pages from database  
**Runs**: Next.js build (Vercel)  
**Method**: getStaticPaths (fetch slug list) + getStaticProps (fetch entity data)  

**Page generation flow**:
```typescript
// pages/[entity-type]/[...slug].tsx
export async function getStaticPaths() {
  // Fetch all active pages from API
  const pages = await fetch('/api/v1/pages?limit=10000')
  return {
    paths: pages.map(p => ({
      params: {
        'entity-type': p.page_type,
        slug: p.slug.split('/')
      }
    })),
    fallback: 'blocking'  // Generate pages on-demand if new
  }
}

export async function getStaticProps({ params }) {
  const entity = await fetch(`/api/v1/${params['entity-type']}/${params.slug}`)
  return {
    props: { entity },
    revalidate: 86400  // Refresh daily
  }
}
```

### 6. Serving
**CDN**: Cloudflare (sits in front of Vercel)  
**Caching**: 
- Vercel CDN: Vercel edge nodes (smart cache)
- Cloudflare: 24-hour cache for static pages
- Browser: 1-hour cache control

## Data Volume & Performance
| Stage | Input | Output | Time | Cost |
|-------|-------|--------|------|------|
| Scrape | APIs | 10k entities | 30 min | $0.07 |
| Clean | 10k raw | 9.5k cleaned | 5 min | $0 |
| Score | 9.5k clean | 9.5k scored | 2 min | $0 |
| Enrich | 9.5k scored | 5k enriched* | 1 hour | $1.00 |
| Generate | 5k enriched | 10k pages | 2 hours | $0 |
| Serve | 10k pages | CDN cache | — | $0.50/mo (Cloudflare) |

*Only top 5k by score get AI enrichment

## Error Handling Strategy
1. **Scraper fails** → Log, send Sentry alert, skip that source
2. **Cleaning fails** → Log malformed data, manual review later
3. **Scoring fails** → Use default score (0.5), proceed
4. **Enrichment fails** → Log, use fallback text (entity description)
5. **Page generation fails** → Log, try next page, flag for manual fix
6. **Serving fails** → Cloudflare returns cached version (stale OK)

## Monitoring Pipeline
```sql
-- Check scraper health
SELECT source, COUNT(*) as count, MAX(updated_at) as last_update
FROM restaurants
GROUP BY source;

-- Check enrichment coverage
SELECT 
  COUNT(DISTINCT page_id) as enriched_pages,
  AVG(similarity_score) as avg_similarity,
  MIN(created_at) as earliest
FROM ai_enrichments;

-- Check page generation status
SELECT page_type, COUNT(*) as total_pages
FROM pages
WHERE is_active = true
GROUP BY page_type;
```

## Rollback Strategy
If data corrupted:
1. **Stop scrapers** (disable Celery tasks)
2. **Identify problem** (check logs)
3. **Rollback DB** (Supabase backup restore)
4. **Fix code** (bug fix or data validation)
5. **Rerun pipeline** (manual trigger or wait for next schedule)

## Cost Optimization
- **Scraping**: Use Google Places API (structured) instead of Playwright (avoid 50+ requests)
- **Enrichment**: Only enrich top 50% by score (save $1/day)
- **Page generation**: ISR (revalidate: 86400) instead of hourly rebuilds (save bandwidth)
- **Serving**: Cloudflare free tier (handles 10k pages, 100k requests/day)
