# Scraper Knowledge Base

Comprehensive documentation of all data scrapers, their configurations, rate limits, pricing, and operational procedures.

---

## Active Scrapers (4)

### 1. Google Places Scraper
**File**: `backend/app/scrapers/google_places.py`

**API Details**:
- API: Google Places API v1 (New) — NOT the legacy Places API
- Authentication: API key in `GOOGLE_PLACES_API_KEY` environment variable
- Base URL: `https://places.googleapis.com/v1/places:searchNearby`

**Rate Limiting**:
- Google's hard limit: 100 requests/second (very high)
- Our self-imposed limit: 1 request per 2 seconds (for cost control)
- Jitter: random 0-1 second added to each delay
- Budget guard: Stop and alert if daily spend exceeds $5 (tracked in Redis)

**Pricing**:
- Nearby Search: $0.017 per request
- Place Details: $0.003 per request
- Example: 100 venues × 2 requests = ~$3.40/day
- Monthly estimate: ~$100 (manageable at scale)

**Scope**: Dubai (radius 30km from center: 25.2048°N, 55.2708°E)

**Data Collected**:
```json
{
  "name": "Nobu Dubai Marina",
  "place_id": "ChIJ...",
  "rating": 4.8,
  "user_ratings_total": 1240,
  "price_level": 4,
  "geometry": {"location": {"latitude": 25.08, "longitude": 55.14}},
  "opening_hours": {"weekday_text": [...]},
  "photos": [{"name": "places/...", "height": 3024, "width": 4032}]
}
```

**Target Categories**:
- Restaurants, cafes, bakeries, desserts
- Hotels, hostels, resorts
- Attractions, parks, museums
- Shopping (malls, boutiques)
- Fitness (gyms, yoga studios)
- Health (clinics, dentists, pharmacies)

**Usage**:
```bash
python -m app.scrapers.google_places \
  --area dubai-marina \
  --category restaurants \
  --radius 5000 \
  --limit 50
```

### 2. Bayut Property Scraper
**File**: `backend/app/scrapers/bayut.py`

**Method**: Playwright (headless browser for JavaScript-heavy site)
- Target: `https://www.bayut.com/to-rent/property/dubai/` and `/for-sale/`
- Why Playwright? Dynamic content loaded after initial page load

**Rate Limiting**:
- Delay: 1 request per 3 seconds (stricter than others)
- Reason: Bayut actively detects and blocks scrapers
- User-Agent rotation: REQUIRED (prevents bot detection)
- Jitter: ±0.5 seconds

**Anti-Detection Measures**:
1. Randomize viewport (1920x1080, 1366x768, 1440x900)
2. Use realistic User-Agent (rotated from pool of 15+)
3. Random delays between actions (150-800ms between clicks)
4. Clear cookies between sessions
5. Never request same page twice in one session

**Data Collected**:
```json
{
  "title": "2BR Apartment in Downtown Dubai",
  "price": 85000,
  "currency": "AED",
  "area": "Downtown Dubai",
  "bedrooms": 2,
  "bathrooms": 1,
  "sqft": 980,
  "developer": "Emaar",
  "agent": "Agent Name",
  "url": "https://www.bayut.com/property/...",
  "property_type": "apartment",
  "availability": "Ready"
}
```

**Usage**:
```bash
python -m app.scrapers.bayut \
  --type rent \
  --area downtown-dubai \
  --bedrooms 2 \
  --price-min 500000 \
  --price-max 1000000
```

### 3. UAE Visa Portal Scraper
**File**: `backend/app/scrapers/visa_portal.py`

**Method**: httpx (static HTML pages from government portal)
- Source: ICP UAE official portal (`https://www.icp.gov.ae/en/services/`)
- Why httpx? Government pages are HTML, no JavaScript rendering needed

**Rate Limiting**:
- Delay: 1 request per 5 seconds (very conservative)
- Reason: Government infrastructure, built for human browsing not scraping
- robots.txt: ALWAYS checked before scraping

**Data Collected**:
```json
{
  "nationality": "United States",
  "visa_type": "Visit Visa",
  "duration_days": 30,
  "fees_aed": 100,
  "requirements": [
    "Valid passport (6 months validity)",
    "Return ticket or sufficient funds",
    "Proof of accommodation",
    "Bank statement"
  ],
  "processing_days": 1
}
```

**Update Frequency**: Weekly (visa rules change slowly)

**Usage**:
```bash
python -m app.scrapers.visa_portal --country all
```

### 4. Company Registry Scraper
**File**: `backend/app/scrapers/companies.py`

**Method**: httpx + BeautifulSoup (static HTML parsing)

**Sources**:
1. **DED Dubai** (Department of Economic Development)
   - URL: `https://www.ded.ae/`
   - Coverage: All registered Dubai companies
   - Rate: 1 req/3s

2. **Freezone Portals** (JAFZA, DSO, Dubai Airport Freezone, etc.)
   - Individual freezone websites
   - Rate: 1 req/5s (more conservative)

**Data Collected**:
```json
{
  "name": "Uber Middle East",
  "sector": "Transportation & Logistics",
  "registration_year": 2014,
  "freezone": "Dubai Silicon Oasis",
  "license_type": "Professional License",
  "status": "Active",
  "employee_count_estimate": "1000-5000",
  "description": "Ride-sharing and delivery services"
}
```

**Update Frequency**: Every 30 days (registrations change slowly)

**Usage**:
```bash
python -m app.scrapers.companies --sector fintech --freezone "Dubai Silicon Oasis"
```  

---

## BaseScraper Contract

All scrapers MUST inherit from `BaseScraper` in `backend/app/scrapers/base.py` and implement this contract:

### Required Methods

```python
from app.scrapers.base import BaseScraper

class YourScraper(BaseScraper):
    
    async def scrape(self, **kwargs) -> List[dict]:
        """Main scraping method. Must return list of dicts."""
        results = []
        
        for item in items:
            await self.rate_limit_delay()  # MANDATORY between requests
            try:
                data = await self.fetch(url)
                parsed = await self.parse(data)
                results.append(parsed)
            except Exception as e:
                logger.error(f"Parse failed: {e}")
        
        return results
    
    async def parse(self, raw_data: str) -> dict:
        """Parse raw response into data dict. Must validate."""
        # Parse logic
        return validated_dict
```

### Inherited Methods from BaseScraper

```python
# Rate limiting with jitter
await self.rate_limit_delay()  # Uses self.delay_seconds + random(0, 1)

# Fetching with retry logic (max_retries = 3 by default)
data = await self.fetch(url)

# Logging scrape jobs
self.log_job_start(name="google_places", area="dubai-marina")
self.log_job_end(name="google_places", collected=50, failed=2, errors=[...])

# Budget tracking (prevents overspend)
self.check_daily_budget(service="google_places", max_daily_cost=5.00)
```

### Required Class Variables

```python
class YourScraper(BaseScraper):
    delay_seconds = 2              # Base delay between requests (seconds)
    max_retries = 3                # Max retry attempts on failure
    timeout_seconds = 30           # Request timeout (seconds)
    api_key = None                 # If API-based
```

### Error Handling Pattern

All scrapers MUST handle common exceptions:

```python
from httpx import TimeoutException, HTTPStatusError
from playwright.async_api import TimeoutError as PlaywrightTimeout

try:
    response = await self.fetch(url)
except TimeoutException:
    logger.warning(f"Timeout on {url}, retrying...")
    # Will be retried automatically by fetch()
except HTTPStatusError as e:
    if e.response.status_code == 429:
        logger.warning("Rate limited (429), backing off...")
        await asyncio.sleep(60)  # Wait before retry
    elif e.response.status_code == 401:
        logger.error("Authentication failed, check API key")
        return []  # Stop scraping
except PlaywrightTimeout:
    logger.warning("Playwright page timeout, skipping...")
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    # Continue to next item
```

---

## User Agent Pool

**File**: `backend/app/scrapers/user_agents.py`

15+ realistic browser User-Agent strings, rotated randomly on each request.

```python
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) Firefox/121.0",
    # ... 12 more
]

# Usage
headers = {"User-Agent": random.choice(USER_AGENTS)}
```

**Why**: Single User-Agent is easily detected. Rotation mimics real user traffic.

---

## ScrapeJob Tracking

Every scrape run creates a `ScrapeJob` record in database:

```python
class ScrapeJob(Base):
    __tablename__ = "scrape_jobs"
    
    scraper_name: str        # "google_places", "bayut", etc.
    started_at: datetime
    completed_at: datetime
    status: str              # "running", "success", "failed"
    records_collected: int
    records_failed: int
    records_updated: int
    error_log: str           # Concatenated error messages
    cost_usd: float          # For API-based scrapers
```

**Used for**:
- Debugging failed scrapes
- Monitoring health (failure rates, latency)
- Cost tracking (OpenAI, Google Places spend)
- Rate limiting decisions (if failures spike, reduce concurrency)

**Query examples**:
```python
# Check if scraper failed recently
failed_jobs = session.execute(
    select(ScrapeJob)
    .where(ScrapeJob.scraper_name == "google_places")
    .where(ScrapeJob.status == "failed")
    .where(ScrapeJob.started_at > datetime.utcnow() - timedelta(hours=24))
).scalars().all()

# Estimate costs for the week
weekly_cost = session.execute(
    select(func.sum(ScrapeJob.cost_usd))
    .where(ScrapeJob.started_at > datetime.utcnow() - timedelta(days=7))
).scalar()
```

---

## Execution Pattern

Every scraper follows this pattern:

1. **Validate** → Check API keys/credentials set, check database connection
2. **Fetch** → Get raw data from source with rate limiting
3. **Parse** → Extract relevant fields, validate format
4. **Deduplicate** → Check if record already exists by unique key
5. **Store** → Insert new records or update existing (soft update: is_active = True)
6. **Log** → Create ScrapeJob record with counts/errors
7. **Invalidate Cache** → Clear Redis cache for pages/lists

---

## Celery Schedule

**File**: `backend/app/pipeline/schedule.py`

```python
CELERY_BEAT_SCHEDULE = {
    'scrape-google-places': {
        'task': 'app.pipeline.tasks.scrape_google_places',
        'schedule': crontab(hour=2, minute=0, tz=pytz.timezone('Asia/Dubai')),
        'kwargs': {}
    },
    'scrape-bayut': {
        'task': 'app.pipeline.tasks.scrape_bayut',
        'schedule': crontab(hour=3, minute=0),  # 3 AM Dubai time
    },
    'scrape-visa-portal': {
        'task': 'app.pipeline.tasks.scrape_visa_portal',
        'schedule': crontab(day_of_week=6, hour=1, minute=0),  # Sunday 1 AM
    },
    'scrape-companies': {
        'task': 'app.pipeline.tasks.scrape_companies',
        'schedule': crontab(hour=1, minute=30),  # 1:30 AM (between other scrapers)
    },
}
```

---

## Monitoring & Health

Check scraper health:

```bash
# View recent scrape jobs
curl http://localhost:8000/api/v1/admin/scrape-jobs/?limit=10

# Count records by scraper
SELECT scraper_name, COUNT(*) FROM scrape_jobs 
  WHERE started_at > NOW() - INTERVAL '7 days'
  GROUP BY scraper_name;

# Calculate weekly spend
SELECT scraper_name, SUM(cost_usd) FROM scrape_jobs
  WHERE started_at > NOW() - INTERVAL '7 days'
  GROUP BY scraper_name;
```

---

## Common Issues & Fixes

| Problem | Cause | Fix |
|---------|-------|-----|
| "Rate limited (429)" | Too many requests too fast | Increase delay_seconds |
| "Page timeout" | Site is slow or blocking | Increase timeout_seconds in config |
| "Cloudflare challenge" | IP detected as bot | Add rotation, randomize delays, wait before retry |
| "No results found" | Search parameters wrong | Verify area/category exist, check site layout |
| "Parse error" | Site HTML changed | Update CSS selectors, inspect live site |
| "IP banned" | Scraped too aggressively | Wait 24h before retry, consider proxy rotation |
| "Memory leak" | Playwright context not closed | Always use `async with` or explicit `.close()` |

---

## Adding a New Scraper

1. **Create file**: `backend/app/scrapers/new_source.py`
2. **Inherit from BaseScraper**
3. **Implement `scrape()` and `parse()`**
4. **Add rate limiting**: `await self.rate_limit_delay()` between requests
5. **Add error handling**: Try/except with logging
6. **Add job tracking**: `self.log_job_start()` and `self.log_job_end()`
7. **Test locally**: `python -m app.scrapers.new_source --dry-run --limit 5`
8. **Add to scheduler**: Edit `backend/app/pipeline/schedule.py`
9. **Document**: Update this knowledge base file
10. **Test in CI**: Add tests to `backend/tests/test_scrapers/`

---

**Last Updated**: 2026-04-20  
**For**: Story of Dubai Data Collection  
**Active Scrapers**: 4 (Google Places, Bayut, Visa Portal, Companies)  
**Estimated Daily Collection**: ~500 new venues + properties, ~20 updates  
**Monthly Cost**: ~$100 (Google Places) + $0 (others = free sources)
