# Scraper Implementation Guide

## Overview
Scrapers collect raw data from external sources (Google Places, Bayut, UAE government portals) and store it in PostgreSQL. Each scraper runs on a Celery schedule, handles rate limiting, errors, and deduplication.

## Data Sources & Strategies

### 1. Google Places API (Structured Data)
**What**: Restaurants, hotels, attractions with ratings, reviews, contact info  
**Method**: Official API (authenticated, requires key)  
**Rate limit**: 100 QPS globally, 150/sec per user  
**Cost**: $7 per 1000 requests (Places Details)  
**Scope**: Dubai (26.144° N, 55.243° E), radius 30km  

```python
# Example query
service.places(
    location="25.2048,55.2708",  # Dubai coordinates
    radius=30000,  # 30km
    type="restaurant",
    key=API_KEY
)
```

### 2. Bayut.com (Web Scraping)
**What**: Property listings with prices, amenities, photos  
**Method**: Playwright (JavaScript rendering required)  
**Rate limit**: Not published, use 3s delay minimum  
**Cost**: Free  
**Example URL**: `https://www.bayut.com/search/rent/villa/dubai/`  

```python
# Selector strategy
page.goto(url)
page.wait_for_load_state("networkidle")
listings = page.query_selector_all("article[data-ad]")
for listing in listings:
    title = listing.query_selector("h2 a").text_content()
    price = listing.query_selector(".price").text_content()
```

### 3. DED Dubai (Business Registry)
**What**: Company registration data, sectors, contact info  
**Method**: HTTPS + parsing (may require login)  
**Status**: Research required — may need partnership  
**Alternative**: Use cached public company lists from Wikipedia/LinkedIn

### 4. Visa Information (UAE Government)
**What**: Visa types, requirements, processing time  
**Method**: Static HTML parsing (https://www.icp.gov.ae)  
**Rate limit**: Standard (1-2s delay)  
**Cost**: Free  

## Scraper Architecture

### Base Scraper Class
```python
# app/scrapers/base.py
class BaseScraper:
    async def scrape(self) -> list[dict]:
        """Override in subclasses"""
        pass
    
    async def _rate_limit(self):
        """Enforce minimum delay between requests"""
        await asyncio.sleep(self.delay_seconds)
    
    async def _fetch(self, url: str) -> str:
        """Fetch with retry logic and error handling"""
        pass
    
    def _deduplicate(self, items: list) -> list:
        """Remove duplicates based on unique_key"""
        pass
```

### Scraper Execution Pattern
1. **Fetch** → Get raw data from source
2. **Parse** → Extract relevant fields
3. **Validate** → Check required fields, format
4. **Deduplicate** → Check if already in DB (by unique key)
5. **Store** → Insert new records, update existing (by unique_key)
6. **Log** → Record success/failure with counts

### Deduplication Strategy
```python
# Each scraper defines a unique_key
# Example: restaurants use google_places_id

existing = await db.query(Restaurant).filter(
    Restaurant.google_places_id == item["google_places_id"]
).first()

if existing:
    # Update existing (keep is_active=true)
    existing.updated_at = now()
    existing.rating = item["rating"]
else:
    # Insert new
    db.add(Restaurant(**item))
```

### Error Handling
- **Network errors**: Retry 3x with exponential backoff
- **Parse errors**: Log and skip item (don't crash scraper)
- **Rate limits**: Respect 429 responses, exponential backoff
- **Data validation**: Log mismatches, don't store incomplete records

## Celery Task Example
```python
# app/tasks/scrapers.py
from celery import shared_task
from app.scrapers.google_places import GooglePlacesScraper

@shared_task
def scrape_restaurants():
    scraper = GooglePlacesScraper(
        api_key=settings.GOOGLE_PLACES_API_KEY
    )
    result = asyncio.run(scraper.scrape())
    return {
        "inserted": result["inserted"],
        "updated": result["updated"],
        "errors": result["errors"]
    }

# Schedule in settings
CELERY_BEAT_SCHEDULE = {
    'scrape-restaurants': {
        'task': 'app.tasks.scrapers.scrape_restaurants',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
}
```

## Testing Scrapers
```python
# backend/tests/test_scrapers/test_google_places.py
def test_scraper_handles_missing_fields():
    """Scraper should skip items with missing required fields"""
    pass

def test_scraper_respects_rate_limit():
    """Scraper should enforce delay_seconds between requests"""
    pass

def test_scraper_deduplicates_by_unique_key():
    """Scraper should not insert duplicates"""
    pass
```

## Monitoring Scrapers
- **Task result**: Check task.result() in Celery Flower UI
- **Logs**: Review app logs for scraper execution (INFO: "Scraped 150 restaurants")
- **Error tracking**: Sentry alerts for failed tasks
- **Database counts**: SELECT COUNT(*) FROM restaurants WHERE is_active=true

## Common Issues & Fixes
| Issue | Cause | Fix |
|-------|-------|-----|
| 429 Too Many Requests | Not respecting rate limit | Increase delay_seconds |
| "No such element" | Selector changed | Inspect site, update XPath/CSS |
| Empty results | Session cookie expired | Add login logic or use API |
| Duplicate entries | Dedup logic broken | Verify unique_key matches actual data |

## Future Enhancements
- Proxy rotation for Bayut (residential proxies)
- Session management for sites requiring login
- Image scraping and storage (S3/Cloudflare R2)
- Scheduled re-scraping of older data (monthly)
