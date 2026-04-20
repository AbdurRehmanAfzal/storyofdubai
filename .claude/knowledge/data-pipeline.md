# Data Pipeline Architecture

## Pipeline Stages
```
Raw Data → Cleaning → Scoring → Enrichment → Page Generation → Serving
```

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
