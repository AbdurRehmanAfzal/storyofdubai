# API Conventions — Story of Dubai

Standards for all REST API endpoints. Every endpoint follows these patterns.

---

## Base URL Structure

All API routes follow this pattern:

```
/api/v1/[resource]
```

**Examples**:
- `GET /api/v1/venues/` — List venues
- `GET /api/v1/venues/{slug}/` — Get single venue
- `GET /api/v1/properties/` — List properties
- `POST /api/v1/scraper/run/` — Start scraper (admin only)

### Authentication

**Public routes** (no auth required):
- All `GET` endpoints for SEO/programmatic access
- Read-only data (venues, properties, visa guides)
- Front-end page generation needs public access

**Protected routes** (Bearer token required):
- All `POST`, `PUT`, `DELETE` operations
- `/api/v1/scraper/*` endpoints
- `/api/v1/admin/*` endpoints

```python
# Example: Protected route
@router.post("/venues", response_model=VenueResponse)
async def create_venue(
    req: VenueCreate,
    current_user: User = Depends(get_current_user),  # ← Auth required
    session: AsyncSession = Depends(get_session)
):
    return await service.create(req, session)
```

---

## Standard Response Format

### Success Response (200, 201)

Every successful endpoint returns this envelope:

```json
{
  "success": true,
  "data": {
    "id": 123,
    "name": "Nobu",
    "slug": "nobu-dubai-marina",
    "rating": 4.8,
    "composite_score": 0.92
  },
  "meta": {
    "total": 1240,
    "page": 1,
    "per_page": 20,
    "has_next": true
  },
  "error": null
}
```

For list endpoints with pagination:

```json
{
  "success": true,
  "data": [
    { "id": 1, "name": "Venue A", ... },
    { "id": 2, "name": "Venue B", ... }
  ],
  "meta": {
    "total": 1240,
    "page": 1,
    "per_page": 20,
    "has_next": true
  },
  "error": null
}
```

### Error Response (4xx, 5xx)

```json
{
  "success": false,
  "data": null,
  "meta": null,
  "error": {
    "code": "VENUE_NOT_FOUND",
    "message": "Venue with slug 'nobu-invalid' not found",
    "details": {
      "slug": "nobu-invalid",
      "searched_in": "restaurants"
    }
  }
}
```

### Implementation

```python
# app/schemas/responses.py
from pydantic import BaseModel
from typing import Any, Optional

class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    meta: Optional[dict] = None
    error: Optional[dict] = None

class PaginationMeta(BaseModel):
    total: int
    page: int
    per_page: int
    has_next: bool

# In route
@router.get("/venues", response_model=ApiResponse)
async def list_venues(
    page: int = 1,
    per_page: int = 20,
    session: AsyncSession = Depends(get_session)
):
    venues, total = await service.list_venues(session, page, per_page)
    return ApiResponse(
        success=True,
        data=venues,
        meta=PaginationMeta(
            total=total,
            page=page,
            per_page=per_page,
            has_next=(page * per_page) < total
        ),
        error=None
    )
```

---

## Pagination

### Query Parameters

All list endpoints support:
- `?page=1` — Page number (default: 1, min: 1)
- `?per_page=20` — Items per page (default: 20, max: 100)

**Examples**:
```
GET /api/v1/venues/?page=1&per_page=50
GET /api/v1/properties/?page=2&per_page=20
GET /api/v1/visa-guides/?page=1
```

### Cursor-Based Pagination (for scrapers)

For very large datasets (10k+ records), use cursor-based pagination:

```
GET /api/v1/venues/export?cursor=abc123&limit=1000
```

Response includes `next_cursor` for fetching next batch:

```json
{
  "success": true,
  "data": [...],
  "meta": {
    "cursor": "abc123",
    "next_cursor": "def456",
    "limit": 1000,
    "has_more": true
  }
}
```

---

## Filtering and Sorting

### Filtering Query Parameters

```
GET /api/v1/venues/?area=dubai-marina&category=restaurants&min_score=70
GET /api/v1/properties/?area=downtown&bedrooms=2&price_min=500000&price_max=1000000
GET /api/v1/companies/?sector=fintech&employees_min=10
```

**Supported filters by resource**:

```
venues:
  - area: area slug
  - category: restaurant, hotel, attraction, etc.
  - min_score: minimum composite score (0-100)
  - is_active: true/false

properties:
  - area: area slug
  - bedrooms: 1-5
  - price_min, price_max: AED amount
  - property_type: apartment, villa, townhouse
  - is_active: true/false

companies:
  - sector: fintech, logistics, retail, etc.
  - employees_min, employees_max: headcount
  - founded_year_min, founded_year_max: year
  - is_active: true/false
```

### Sorting

```
GET /api/v1/venues/?ordering=-composite_score
GET /api/v1/properties/?ordering=-price
GET /api/v1/companies/?ordering=name
```

**Format**:
- `-field_name` = descending (highest first)
- `field_name` = ascending (lowest first)
- Default if not specified: `-composite_score` (most relevant first)

**Sortable fields**:
- venues: composite_score, rating, review_count, created_at
- properties: price, bedrooms, created_at
- companies: founded_year, employee_count, name

### Full-Text Search

```
GET /api/v1/venues/?q=burj+khalifa
GET /api/v1/companies/?q=uber
```

Searches across: name, description, address fields. Case-insensitive, partial match.

---

## Key Endpoints (Frontend & Scraper)

### Venue Endpoints

```
GET  /api/v1/venues/                    List all venues with filters
GET  /api/v1/venues/{slug}/             Get single venue by slug
GET  /api/v1/areas/                     List all Dubai areas
GET  /api/v1/areas/{slug}/              Get area details
GET  /api/v1/categories/                List venue categories
```

**Example list request**:
```
GET /api/v1/venues/?area=dubai-marina&category=restaurants&ordering=-composite_score&page=1&per_page=20
```

### Property Endpoints

```
GET  /api/v1/properties/                List properties with filters
GET  /api/v1/properties/{slug}/         Get single property by slug
GET  /api/v1/developers/{slug}/         Get developer info (buildings)
```

**Example**:
```
GET /api/v1/properties/?area=marina&bedrooms=2&price_min=500000&price_max=1000000
```

### Visa Endpoints

```
GET  /api/v1/visa-guides/               List visa guides
GET  /api/v1/visa-guides/{slug}/        Get single visa guide
GET  /api/v1/nationalities/             List nationalities
```

### Company Endpoints

```
GET  /api/v1/companies/                 List companies
GET  /api/v1/companies/{slug}/          Get single company
GET  /api/v1/sectors/                   List sectors
```

### Static Path Generation (for Next.js getStaticPaths)

**High-performance, Redis-cached endpoints for page generation**:

```
GET  /api/v1/page-paths/venues/         Returns all venue paths
GET  /api/v1/page-paths/properties/     Returns all property paths
GET  /api/v1/page-paths/visa-guides/    Returns all visa paths
GET  /api/v1/page-paths/companies/      Returns all company paths
```

**Response format**:
```json
{
  "success": true,
  "data": [
    { "slug": "nobu-dubai-marina", "area": "marina", "category": "restaurants" },
    { "slug": "zuma-downtown", "area": "downtown", "category": "restaurants" },
    ...
  ],
  "meta": {
    "total": 1240,
    "cache_age_seconds": 300
  }
}
```

**Usage in Next.js**:
```typescript
export async function getStaticPaths() {
  const paths = await fetch(`${API_URL}/page-paths/venues`)
  return {
    paths: paths.data.map(p => ({
      params: { area: p.area, category: p.category, slug: p.slug }
    })),
    fallback: 'blocking'
  }
}
```

### Sitemap Endpoint

```
GET  /sitemap.xml                       Dynamic XML sitemap for all pages
GET  /sitemap-venues.xml                Venues sitemap (chunked by 50k)
GET  /sitemap-properties.xml            Properties sitemap
```

---

## HTTP Status Codes

| Code | Meaning | Response |
|------|---------|----------|
| **200** | OK | GET request succeeded |
| **201** | Created | POST created resource |
| **204** | No Content | DELETE successful |
| **400** | Bad Request | Invalid input (validation error) |
| **401** | Unauthorized | Missing/invalid token |
| **403** | Forbidden | User lacks permission |
| **404** | Not Found | Resource doesn't exist |
| **409** | Conflict | Duplicate slug, business rule violation |
| **429** | Too Many Requests | Rate limit exceeded |
| **500** | Server Error | Unexpected error (log it!) |
| **502** | Bad Gateway | External API unavailable (scraper) |
| **503** | Service Unavailable | Database/Redis down |

**Example error handling**:
```python
@router.get("/venues/{slug}", response_model=ApiResponse)
async def get_venue(slug: str, session: AsyncSession = Depends(get_session)):
    try:
        venue = await service.get_by_slug(slug, session)
        if not venue:
            raise HTTPException(
                status_code=404,
                detail=f"Venue {slug} not found"
            )
        return ApiResponse(success=True, data=venue)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal error")
```

---

## Rate Limiting

Global rate limits:

```
Anonymous users: 100 requests/minute per IP
Authenticated: 1000 requests/minute
Scraper token: 10 requests/minute (prevent DoS)
```

**Headers in response**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1713607200
```

When rate limited:
```
HTTP 429 Too Many Requests
X-RateLimit-Retry-After: 60
```

---

## Request/Response Examples

### GET Venues List (Paginated)

**Request**:
```
GET /api/v1/venues/?area=dubai-marina&category=restaurants&page=1&per_page=5
```

**Response (200)**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "slug": "nobu-dubai-marina",
      "name": "Nobu",
      "rating": 4.8,
      "review_count": 1240,
      "area": "Dubai Marina",
      "category": "Restaurants",
      "composite_score": 92,
      "created_at": "2026-04-20T12:00:00Z"
    },
    {
      "id": 2,
      "slug": "zuma-dubai-marina",
      "name": "Zuma",
      "rating": 4.7,
      "review_count": 890,
      "area": "Dubai Marina",
      "category": "Restaurants",
      "composite_score": 85,
      "created_at": "2026-04-20T12:05:00Z"
    }
  ],
  "meta": {
    "total": 45,
    "page": 1,
    "per_page": 5,
    "has_next": true
  },
  "error": null
}
```

### GET Single Venue

**Request**:
```
GET /api/v1/venues/nobu-dubai-marina/
```

**Response (200)**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "slug": "nobu-dubai-marina",
    "name": "Nobu",
    "rating": 4.8,
    "review_count": 1240,
    "area": "Dubai Marina",
    "cuisine": "Japanese",
    "address": "Al Marjan Island, Dubai Marina",
    "phone": "+971 4 777 6777",
    "website": "https://www.noburestaurants.com",
    "price_range": "$$$",
    "highlights": ["Fine dining", "Michelin-starred", "Sushi"],
    "composite_score": 92
  },
  "meta": null,
  "error": null
}
```

### GET Venue Not Found

**Request**:
```
GET /api/v1/venues/invalid-slug-xyz/
```

**Response (404)**:
```json
{
  "success": false,
  "data": null,
  "meta": null,
  "error": {
    "code": "VENUE_NOT_FOUND",
    "message": "Venue with slug 'invalid-slug-xyz' not found",
    "details": {
      "slug": "invalid-slug-xyz"
    }
  }
}
```

---

## Caching Rules

### Redis Cache Strategy

**Cache TTL by resource type**:
- Individual venue/property/company data: **24 hours** (rarely changes)
- Area/category lists: **1 hour** (categories don't change)
- Page-paths endpoints: **6 hours** (used by Next.js build, shouldn't change often)
- Composite scores: **1 hour** (updated by scoring engine)

### Cache Key Format

```
venue:{slug}
property:{slug}
area:{slug}
category:{category_name}
page_paths:venues:v1
composite_score_cache:venue:{area_slug}:{category_slug}
```

### Cache Invalidation

When scraper updates data:

```python
# In scraper task
await cache.delete(f"venue:{venue.slug}")
await cache.delete(f"page_paths:venues:v1")  # Refresh page generation cache
await cache.delete(f"composite_score_cache:*")
```

When admin edits data:

```python
# In service.update()
venue = await db.session.execute(update_query)
await cache.delete(f"venue:{venue.slug}")
await cache.delete(f"page_paths:venues:v1")
```

---

## Health Check Endpoint

```
GET  /api/v1/health/
```

**Response (200)**:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "version": "0.1.0",
  "uptime_seconds": 123456
}
```

Used by:
- Load balancer health checks
- Monitoring alerts
- Deployment verification

---

**Last Updated**: 2026-04-20  
**For**: Story of Dubai API  
**Enforced by**: Route implementation, tests, documentation
