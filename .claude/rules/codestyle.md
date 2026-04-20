# Code Style Rules — Story of Dubai

Claude Code must follow these rules on every file it creates or edits.

---

## Python Rules

### Formatting
- **Formatter**: Black (line length: 88 characters)
- **Import sorting**: isort (profile: black)
- **Type hints**: Required on all function signatures
- **String formatting**: f-strings only (no .format() or %)

### Naming Conventions
- **Files**: snake_case (venue_scraper.py, not VenueScraper.py)
- **Classes**: PascalCase (class VenueScorer:)
- **Functions/variables**: snake_case (def score_venue():)
- **Constants**: UPPER_SNAKE_CASE (MAX_RETRIES = 3)
- **FastAPI routers**: noun_plural (venues, properties, areas)

### Imports Order (isort enforced)
```python
# 1. Standard library
import asyncio
import json
from datetime import datetime

# 2. Third-party packages
import sqlalchemy as sa
from pydantic import BaseModel

# 3. Local application imports
from app.models import Restaurant
from app.services import VenueService
```

Each group separated by blank line.

### FastAPI Specific

```python
# ✅ GOOD
@router.get("/venues/{venue_id}", response_model=VenueResponse)
async def get_venue(venue_id: int, session: AsyncSession = Depends(get_session)):
    venue = await service.get_venue(venue_id, session)
    return venue

# ❌ BAD
@router.get("/venues/{venue_id}")
def get_venue(venue_id):  # sync, no type hints, no response_model
    venue = Restaurant.query.filter(id=venue_id).first()  # direct query
    return venue
```

**Rules**:
- Always use `async def` for route handlers
- Use Pydantic v2 models for all request/response schemas
- Router files live in `app/api/v1/[resource].py`
- Always include `response_model` on route decorators
- Tag all routes for automatic API docs grouping:

```python
@router.get("/venues", tags=["venues"], response_model=List[VenueResponse])
async def list_venues(...):
    pass
```

### SQLAlchemy Specific

```python
# ✅ GOOD (async + select + joinedload)
async def get_venue_with_details(session: AsyncSession, venue_id: int):
    stmt = select(Restaurant).where(Restaurant.id == venue_id)
    stmt = stmt.options(joinedload(Restaurant.area))
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

# ❌ BAD (sync, bare query, lazy loading)
def get_venue(venue_id):
    venue = Restaurant.query.filter_by(id=venue_id).first()
    area = venue.area  # Lazy load! N+1 problem
    return venue
```

**Rules**:
- Always use `async` session: `AsyncSession` everywhere
- Always use `select()` not `query()`
- Always add `__tablename__` and proper indexes
- Foreign keys always have explicit `ondelete` behavior:

```python
class Review(Base):
    __tablename__ = "reviews"
    venue_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"))
```

- Never use lazy loading — always specify `joinedload` or `selectinload`

### Error Handling

```python
# ✅ GOOD
try:
    result = await scrape_venue(url)
except HttpStatusError as e:
    logger.error(f"Scrape failed for {url}: {e}", exc_info=True)
    raise HTTPException(status_code=502, detail="External API error")
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="Internal error")

# ❌ BAD
try:
    result = scrape_venue(url)
except:  # Bare except!
    return {"error": "failed"}  # No logging, wrong status
```

**Rules**:
- Never use bare `except:`
- Always catch specific exceptions
- Log errors with: `logger.error(f"...", exc_info=True)`
- Return proper HTTP status codes from FastAPI (never 200 for errors)

---

## TypeScript / Next.js Rules

### Formatting
- **Formatter**: Prettier (single quotes, no semicolons, 2-space indent)
- **Linter**: ESLint with `next/core-web-vitals`

### Naming Conventions
- **Components**: PascalCase (VenueCard.tsx)
- **Pages**: kebab-case files, PascalCase exports (pages/venue-details.tsx → export default VenueDetails)
- **Hooks**: camelCase with "use" prefix (useVenueData.ts)
- **Utils**: camelCase (formatScore.ts, parseAddress.ts)
- **Constants**: UPPER_SNAKE_CASE (ITEMS_PER_PAGE = 50)

### Next.js Specific

```typescript
// ✅ GOOD: getStaticProps with revalidate
export async function getStaticProps({ params }) {
  const venue = await fetch(`/api/v1/venues/${params.id}`)
  return {
    props: { venue },
    revalidate: 86400  // 24 hours ISR
  }
}

export async function getStaticPaths() {
  const venues = await fetch('/api/v1/venues?limit=10000')
  return {
    paths: venues.map(v => ({ params: { id: v.id.toString() } })),
    fallback: 'blocking'
  }
}

// ❌ BAD: Client-side fetch on SEO page
export default function VenueDetails() {
  const [venue, setVenue] = useState(null)
  useEffect(() => {
    fetch(`/api/v1/venues/${id}`).then(v => setVenue(v))  // Too late for SEO!
  }, [id])
  return <div>{venue?.name}</div>
}
```

**Rules**:
- Use Pages Router (not App Router) for all data-fetching pages
- Always use `getStaticProps` + `getStaticPaths` for generated pages
- Always set `revalidate: 86400` (24 hours) on `getStaticProps`
- Never fetch data client-side for SEO-critical content
- Always include `<Head>` with title, description, canonical on every page:

```typescript
import Head from 'next/head'

export default function VenuePage({ venue }) {
  return (
    <>
      <Head>
        <title>{venue.name} — Story of Dubai</title>
        <meta name="description" content={venue.description} />
        <link rel="canonical" href={`https://storyofdubai.com/venues/${venue.slug}`} />
      </Head>
      <VenueCard venue={venue} />
    </>
  )
}
```

### TypeScript

```typescript
// ✅ GOOD: Typed interfaces
interface Venue {
  id: number
  name: string
  rating: number
  area: Area
}

const venue: Venue = { ... }

// ❌ BAD: any types
const venue: any = { ... }
const venues: any[] = [...]
```

**Rules**:
- No `any` types — use proper interfaces
- Define API response types in `lib/types.ts`
- Use `interface` over `type` for objects:

```typescript
// lib/types.ts
export interface Venue {
  id: number
  name: string
  rating: number
}

export interface ApiResponse<T> {
  status: 'success' | 'error'
  data: T
}
```

---

## Git Commit Message Format

### Conventional Commits

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature (new scraper, endpoint, page)
- `fix`: Bug fix (scoring edge case, typo)
- `refactor`: Code restructuring (extract service, rename)
- `docs`: Documentation (CLAUDE.md, README)
- `test`: Test additions
- `chore`: Maintenance (deps, config)

**Examples**:
```
feat(backend): add google places scraper

Implement scraper for restaurants using Google Places API.
Rate limiting: 2s delay. Stores results in venues table.
Runs via celery task: scrape_google_places (daily at 2 AM)

Closes #123

feat(frontend): add venue detail page

Pages Router with getStaticProps/getStaticPaths.
Includes schema.org JSON-LD markup.
ISR: 24h revalidation.

fix(scoring): fix area score normalization edge case

Area scores now properly capped at 1.0.
Added test case for edge case.

docs: update CLAUDE.md with new endpoints
```

### Never Commit These Files
- `.env` — contains secrets
- `CLAUDE.local.md` — local machine config
- `.claude/settings.local.json` — local overrides
- `__pycache__/` — Python cache
- `node_modules/` — dependencies
- `.next/` — Next.js build
- `venv/` — virtual environment

### Always Update PROGRESS.md
Every major feature commit should include PROGRESS.md update:

```markdown
## Completed Tasks
- [x] Feature: Add Google Places scraper
- [x] Tests: Add scraper unit tests
- [x] Docs: Update CLAUDE.md

## NEXT TASK
→ Feature: Add Bayut.com property scraper
```

---

## Code Review Checklist

Before committing, verify:

- [ ] Black formatted: `black app/`
- [ ] isort organized: `isort app/`
- [ ] ESLint passes: `npm run lint`
- [ ] Type hints on all functions
- [ ] No bare `except:` or `any` types
- [ ] Tests pass: `pytest -v`
- [ ] FastAPI routes have `response_model`
- [ ] Next.js pages have `getStaticProps/getStaticPaths`
- [ ] PROGRESS.md updated
- [ ] No secrets in code or commit message

---

**Last Updated**: 2026-04-20  
**For**: Story of Dubai project  
**Enforced by**: Claude Code on every file edit
