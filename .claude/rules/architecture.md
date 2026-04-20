# Architecture Rules

Design decisions that shape how code is organized and built. Every new module follows these patterns.

---

## Backend Structure (FastAPI)

```
app/
├── main.py              — FastAPI app init, middleware, router registration
├── config.py            — Settings via pydantic-settings (reads .env)
├── database.py          — SQLAlchemy async engine and session factory
├── models/
│   ├── base.py          — Base class for all ORM models
│   ├── restaurant.py     — Restaurant entity
│   ├── property.py       — Property/Real estate entity
│   ├── visa_info.py      — Visa information entity
│   └── ...               — One file per domain entity
├── schemas/
│   ├── restaurant.py     — Pydantic request/response models for restaurants
│   ├── property.py       — Pydantic models for properties
│   └── ...               — One file per entity
├── api/v1/
│   ├── __init__.py
│   ├── restaurants.py    — GET /restaurants, POST, PUT, DELETE routes
│   ├── properties.py     — Property CRUD routes
│   ├── search.py         — Search/filter endpoints
│   └── health.py         — Health check endpoint
├── services/
│   ├── restaurant_service.py     — Business logic for restaurants
│   ├── property_service.py       — Business logic for properties
│   └── ...                       — One file per domain
├── scrapers/
│   ├── base.py                   — BaseScraper abstract class
│   ├── google_places.py          — Google Places API scraper
│   ├── bayut.py                  — Bayut.com scraper
│   └── ...                       — One file per data source
├── scoring/
│   ├── base.py                   — Base scoring logic
│   ├── restaurant_scorer.py      — Restaurant-specific scoring
│   ├── property_scorer.py        — Property-specific scoring
│   └── ...                       — One scorer per entity type
├── pipeline/
│   ├── tasks.py                  — Celery tasks, @app.task definitions
│   ├── orchestration.py          — Task scheduling and dependencies
│   └── ...
├── ai_enrichment/
│   ├── enricher.py               — GPT-4o-mini content generation
│   ├── similarity.py             — Cosine similarity checking
│   └── ...
└── utils/
    ├── logger.py                 — Structured logging
    ├── errors.py                 — Custom exceptions
    └── ...
```

### The Golden Rule: Thin Routes, Fat Services

**Routes do:**
- Validate input (Pydantic models)
- Call service methods
- Return response with proper status code
- Handle HTTP-specific logic (auth, CORS)

**Routes NEVER do:**
- Database queries (use services)
- Business logic (use services)
- External API calls (use services)
- Retry logic (use services)

**Services do:**
- All business logic
- All database operations
- All external API calls
- Error handling and retry logic

**Example:**

```python
# ❌ BAD: Business logic in route
@router.post("/restaurants")
async def create_restaurant(req: RestaurantCreate, session: AsyncSession):
    # Database query in route!
    existing = await session.execute(
        select(Restaurant).where(Restaurant.name == req.name)
    )
    if existing.scalar():
        raise HTTPException(400, "Already exists")
    
    # Calculation in route!
    score = req.rating * 0.3 + req.reviews * 0.7
    
    restaurant = Restaurant(**req.dict(), composite_score=score)
    session.add(restaurant)
    await session.commit()
    return restaurant

# ✅ GOOD: Thin route, fat service
@router.post("/restaurants", response_model=RestaurantResponse)
async def create_restaurant(
    req: RestaurantCreate,
    service: RestaurantService = Depends(get_restaurant_service)
):
    restaurant = await service.create(req)
    return restaurant

# In services/restaurant_service.py
class RestaurantService:
    async def create(self, req: RestaurantCreate) -> Restaurant:
        # Check for duplicates
        existing = await self._get_by_name(req.name)
        if existing:
            raise ValueError(f"Restaurant {req.name} already exists")
        
        # Calculate score
        score = self._calculate_score(req)
        
        # Database operation
        restaurant = Restaurant(**req.dict(), composite_score=score)
        self.session.add(restaurant)
        await self.session.commit()
        return restaurant
    
    def _calculate_score(self, req: RestaurantCreate) -> float:
        return req.rating * 0.3 + req.reviews * 0.7
```

---

## Scraper Architecture

Every scraper follows this pattern:

```python
# app/scrapers/base.py
class BaseScraper:
    delay_seconds: int = 2
    max_retries: int = 3
    
    async def scrape(self) -> dict:
        """Implemented by subclasses"""
        raise NotImplementedError
    
    async def _fetch(self, url: str) -> str:
        """Fetch with retry logic, rate limiting, user agent rotation"""
        pass
    
    async def _rate_limit(self):
        """Enforce delay between requests"""
        await asyncio.sleep(self.delay_seconds)
    
    def _log_scrape_job(self, start, end, records, errors):
        """Create ScrapeJob record in DB"""
        pass

# app/scrapers/google_places.py
class GooglePlacesScraper(BaseScraper):
    def __init__(self, api_key: str, session: AsyncSession):
        self.api_key = api_key
        self.session = session
    
    async def scrape(self) -> dict:
        """Return: {"inserted": 150, "updated": 30, "errors": 2}"""
        start_time = datetime.utcnow()
        inserted = 0
        updated = 0
        errors = []
        
        try:
            restaurants = await self._fetch_all_restaurants()
            
            for venue in restaurants:
                try:
                    await self._rate_limit()
                    await self.service.create_or_update(venue)
                    inserted += 1
                except Exception as e:
                    logger.error(f"Error processing {venue}: {e}")
                    errors.append(str(e))
            
            end_time = datetime.utcnow()
            self._log_scrape_job(start_time, end_time, inserted, errors)
            
            return {
                "inserted": inserted,
                "updated": updated,
                "errors": len(errors)
            }
        except Exception as e:
            logger.error(f"Scraper failed: {e}", exc_info=True)
            raise
```

### Scraper Rules
- Every scraper inherits from `BaseScraper` (enforces rate limiting, retries)
- Scrapers write to DB via services, never directly
- Every scraper run creates a `ScrapeJob` record (tracking)
- Scrapers run via Celery periodic tasks in `pipeline/tasks.py`
- All errors are logged and reported

---

## Database & ORM Rules

### Base Model (every ORM model inherits from this)

```python
# app/models/base.py
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, nullable=False)

# app/models/restaurant.py
class Restaurant(BaseModel):
    __tablename__ = "restaurants"
    
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    rating = Column(Float)
    composite_score = Column(Float, nullable=False, index=True)
    
    # Foreign key with explicit ondelete
    area_id = Column(Integer, ForeignKey("areas.id", ondelete="CASCADE"))
```

### Database Rules
- All models inherit from `BaseModel` (provides id, created_at, updated_at, is_active)
- Every entity has a `slug` field that is unique and indexed
- Composite scores are **stored** in DB (never calculated at request time)
- **Soft delete only**: set `is_active=False`, never hard delete
- Foreign keys always have explicit `ondelete` behavior
- All frequently-queried columns are indexed

### Migrations with Alembic
- All schema changes go through Alembic migrations
- Never modify tables directly via raw SQL
- Command: `alembic revision --autogenerate -m "add email column"`
- Command: `alembic upgrade head` (apply migrations)

---

## Frontend Architecture (Next.js)

```
frontend/
├── pages/
│   ├── index.tsx                      — Homepage
│   ├── restaurants/
│   │   └── [area]/[name].tsx          — Venue detail page (SSG)
│   ├── apartments/
│   │   └── [area]/[bedroom]/[name].tsx — Property page (SSG)
│   ├── api/
│   │   └── health.ts                  — Health check endpoint
│   └── _app.tsx                       — App wrapper, global styles
├── components/
│   ├── VenueCard.tsx                  — Purely presentational
│   ├── PropertyList.tsx                — Presentational component
│   ├── Header.tsx                      — Layout component
│   └── ...
├── lib/
│   ├── api.ts                         — All API calls, typed
│   ├── types.ts                       — TypeScript interfaces
│   ├── formatters.ts                  — Utility functions
│   └── ...
├── styles/
│   ├── globals.css                    — Global TailwindCSS
│   └── components/
│       └── VenueCard.module.css       — Component CSS (if needed)
├── public/
│   └── robots.txt                     — SEO file
├── next.config.js
├── tsconfig.json
└── package.json
```

### Frontend Rules

**lib/api.ts** — Single source of truth for all backend calls:

```typescript
// ✅ All API calls typed and centralized
import { Venue, Property, ApiResponse } from './types'

export const api = {
  venues: {
    getById: async (id: string): Promise<Venue> => {
      const res = await fetch(`${API_URL}/venues/${id}`)
      return res.json()
    },
    list: async (limit = 50) => {
      const res = await fetch(`${API_URL}/venues?limit=${limit}`)
      return res.json()
    }
  },
  properties: {
    getById: async (id: string): Promise<Property> => {
      // ...
    }
  }
}

// In pages/venues/[id].tsx
export async function getStaticProps({ params }) {
  const venue = await api.venues.getById(params.id)
  return { props: { venue }, revalidate: 86400 }
}
```

**lib/types.ts** — All interfaces matching backend schemas:

```typescript
// lib/types.ts
export interface Venue {
  id: number
  name: string
  slug: string
  rating: number
  address: string
  area: Area
  composite_score: number
}

export interface ApiResponse<T> {
  status: 'success' | 'error'
  data: T
}
```

**Components** — Purely presentational:

```typescript
// ❌ BAD: Component does data fetching
export default function VenueCard({ venueId }) {
  const [venue, setVenue] = useState(null)
  useEffect(() => {
    fetch(`/api/venues/${venueId}`).then(v => setVenue(v))
  }, [venueId])
  return <div>{venue?.name}</div>
}

// ✅ GOOD: Component receives data as prop
export default function VenueCard({ venue }: { venue: Venue }) {
  return (
    <div>
      <h1>{venue.name}</h1>
      <p>Rating: {venue.rating}/5</p>
    </div>
  )
}
```

**Pages** — Data fetching via getStaticProps:

```typescript
// pages/venues/[slug].tsx
export async function getStaticPaths() {
  const venues = await api.venues.list(10000)
  return {
    paths: venues.map(v => ({ params: { slug: v.slug } })),
    fallback: 'blocking'
  }
}

export async function getStaticProps({ params }) {
  const venue = await api.venues.getBySlug(params.slug)
  return {
    props: { venue },
    revalidate: 86400
  }
}

export default function VenuePage({ venue }: { venue: Venue }) {
  return (
    <>
      <Head>
        <title>{venue.name} — Story of Dubai</title>
        <meta name="description" content={`Best ${venue.name} in Dubai`} />
        <link rel="canonical" href={`${SITE_URL}/venues/${venue.slug}`} />
      </Head>
      <VenueCard venue={venue} />
    </>
  )
}
```

---

## Dependency Injection Pattern

**Backend**: Use FastAPI Depends:

```python
def get_db_session() -> AsyncSession:
    return SessionLocal()

def get_restaurant_service(session: AsyncSession = Depends(get_db_session)):
    return RestaurantService(session)

@router.get("/restaurants")
async def list_restaurants(
    service: RestaurantService = Depends(get_restaurant_service)
):
    return await service.list()
```

**Frontend**: Use api.ts singleton + React hooks:

```typescript
export const useVenue = (id: string) => {
  const [venue, setVenue] = useState<Venue | null>(null)
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    api.venues.getById(id).then(v => {
      setVenue(v)
      setLoading(false)
    })
  }, [id])
  
  return { venue, loading }
}
```

---

## Error Handling Strategy

**Backend**: Custom exception hierarchy in app/utils/errors.py:

```python
class StoryOfDubaiError(Exception):
    """Base exception"""
    pass

class ScraperError(StoryOfDubaiError):
    """Scraper failures"""
    pass

class ValidationError(StoryOfDubaiError):
    """Input validation"""
    pass

# In routes
try:
    venue = await service.create(req)
except ValidationError as e:
    raise HTTPException(status_code=400, detail=str(e))
except ScraperError as e:
    raise HTTPException(status_code=502, detail="Scraper failed")
```

**Frontend**: Type-safe error handling:

```typescript
export const apiCall = async <T,>(
  fn: () => Promise<T>,
  onError?: (err: Error) => void
): Promise<T | null> => {
  try {
    return await fn()
  } catch (err) {
    console.error(err)
    onError?.(err as Error)
    return null
  }
}
```

---

## Configuration & Environment

All configuration comes from `.env` via Pydantic settings (never hardcoded):

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    openai_api_key: str
    google_places_api_key: str
    scraper_delay_seconds: int = 2
    
    class Config:
        env_file = ".env"

settings = Settings()

# Usage: settings.database_url
```

---

**Last Updated**: 2026-04-20  
**For**: Story of Dubai  
**Enforced by**: Code review and Claude Code settings.json
