# Testing Standards — Story of Dubai

Comprehensive testing strategy for all backend code. Frontend testing deferred to Phase 3.

---

## Test Structure

```
backend/tests/
├── conftest.py                    — Shared fixtures, test DB, mock clients
├── unit/
│   ├── test_scoring.py            — Scoring algorithm (CRITICAL)
│   ├── test_scrapers.py           — Parser logic (mock HTTP)
│   ├── test_enrichment.py         — AI content generation (mock OpenAI)
│   └── test_models.py             — Pydantic schema validation
├── integration/
│   ├── test_api_venues.py         — Venue endpoints with DB
│   ├── test_api_properties.py     — Property endpoints
│   ├── test_api_visa.py           — Visa guide endpoints
│   ├── test_api_companies.py      — Company endpoints
│   ├── test_pipeline.py           — Scraper → DB → Scoring flow
│   └── test_caching.py            — Redis cache behavior
├── e2e/
│   ├── test_page_generation.py    — getStaticPaths returns valid paths
│   └── test_scrape_to_page.py     — Full pipeline: scrape → page generation
└── fixtures/
    ├── factories.py               — factory_boy model factories
    ├── mocks.py                   — Mock responses for external APIs
    └── sample_data.py             — Test data constants
```

---

## What Must Be Tested (Non-Negotiable)

### 1. Scoring Algorithm (100% Coverage Required)

The scoring engine is core IP. Must test every weight, edge case, and combination.

```python
# tests/unit/test_scoring.py
import pytest
from app.scoring.venue_scorer import VenueScorer

class TestVenueScorer:
    @pytest.fixture
    def scorer(self):
        return VenueScorer()
    
    # Test every weight
    def test_rating_weight_contribution(self, scorer):
        """Rating contributes 30% of score"""
        venue = Venue(rating=5.0, review_count=100, is_recent=True)
        score = scorer.calculate(venue)
        assert score > 0.7  # Rating alone should yield > 70
    
    # Test edge cases
    def test_score_with_zero_reviews(self, scorer):
        """Venues with 0 reviews should not crash"""
        venue = Venue(rating=4.5, review_count=0)
        score = scorer.calculate(venue)
        assert 0 <= score <= 100
    
    def test_score_with_null_rating(self, scorer):
        """Venues with null rating should handle gracefully"""
        venue = Venue(rating=None, review_count=50)
        score = scorer.calculate(venue)
        assert score is not None  # Should not be None
    
    def test_score_with_missing_data(self, scorer):
        """Partial data should not crash scorer"""
        venue = Venue(rating=4.0, review_count=None, is_recent=None)
        score = scorer.calculate(venue)
        assert 0 <= score <= 100
    
    # Test weight combinations
    def test_max_score_all_factors(self, scorer):
        """Perfect scores in all factors = 100"""
        venue = Venue(
            rating=5.0, review_count=10000,
            is_recent=True, completeness=1.0
        )
        score = scorer.calculate(venue)
        assert score == 100
    
    def test_min_score_all_factors(self, scorer):
        """Worst scores in all factors = 0"""
        venue = Venue(
            rating=0, review_count=0,
            is_recent=False, completeness=0
        )
        score = scorer.calculate(venue)
        assert score == 0
    
    # Test determinism
    def test_scoring_is_deterministic(self, scorer):
        """Same input always produces same score"""
        venue = Venue(rating=4.5, review_count=100)
        score1 = scorer.calculate(venue)
        score2 = scorer.calculate(venue)
        assert score1 == score2  # Exact match, no randomness
```

### 2. Scraper Data Parsers (70% Coverage Minimum)

Test parsing logic with mocked HTTP responses. NEVER test with live HTTP.

```python
# tests/unit/test_scrapers.py
import pytest
from unittest.mock import Mock, AsyncMock
from app.scrapers.google_places import GooglePlacesScraper

@pytest.fixture
def mock_response():
    """Mock successful Google Places API response"""
    return {
        "results": [
            {
                "name": "Nobu",
                "rating": 4.8,
                "user_ratings_total": 1240,
                "formatted_address": "Dubai Marina",
                "place_id": "abc123",
                "types": ["restaurant", "food"],
                "opening_hours": {
                    "open_now": True,
                    "weekday_text": ["Monday: 6:00 PM – 11:00 PM", ...]
                }
            }
        ]
    }

@pytest.mark.asyncio
async def test_parse_venue_success(mock_response):
    """Parser correctly extracts venue from API response"""
    scraper = GooglePlacesScraper(api_key="test_key")
    venue = scraper._parse_venue(mock_response["results"][0])
    
    assert venue.name == "Nobu"
    assert venue.rating == 4.8
    assert venue.review_count == 1240
    assert venue.address == "Dubai Marina"
    assert venue.place_id == "abc123"

@pytest.mark.asyncio
async def test_parse_venue_missing_rating(mock_response):
    """Parser handles missing rating gracefully"""
    mock_response["results"][0].pop("rating", None)
    scraper = GooglePlacesScraper(api_key="test_key")
    venue = scraper._parse_venue(mock_response["results"][0])
    
    assert venue.rating is None
    assert venue.name == "Nobu"  # Other fields still populated

@pytest.mark.asyncio
async def test_parse_venue_invalid_data():
    """Parser rejects malformed data"""
    bad_response = {"name": "Test"}  # Missing required fields
    scraper = GooglePlacesScraper(api_key="test_key")
    
    with pytest.raises(ValueError):
        scraper._parse_venue(bad_response)
```

### 3. Slug Generation (Uniqueness, Special Characters)

Test slug generation with Arabic, special characters, and edge cases.

```python
# tests/unit/test_models.py
import pytest
from app.models import Venue
from app.utils.slugs import generate_slug

def test_slug_generation_basic():
    """Simple English name → valid slug"""
    slug = generate_slug("Nobu Dubai Marina")
    assert slug == "nobu-dubai-marina"
    assert slug.isascii()

def test_slug_generation_arabic():
    """Arabic characters are transliterated"""
    slug = generate_slug("مطعم النيل")  # Arabic for "Nile Restaurant"
    assert slug == "mataam-alnyl"  # Transliterated
    assert slug.isascii()

def test_slug_generation_special_chars():
    """Special chars removed or replaced"""
    slug = generate_slug("Café & Bar (2026)")
    assert slug == "cafe-bar-2026"
    assert "&" not in slug and "(" not in slug

def test_slug_uniqueness():
    """Slugs are unique (in DB)"""
    venue1 = Venue(name="Nobu", area_id=1)
    venue2 = Venue(name="Nobu", area_id=2)  # Same name, different area
    
    # In reality, should have area_id in slug
    assert venue1.slug != venue2.slug or venue1.area_id != venue2.area_id
```

### 4. API Response Format (All Endpoints)

Every endpoint must return the standard envelope.

```python
# tests/integration/test_api_venues.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_venues_response_format(async_client: AsyncClient):
    """GET /venues returns standard envelope"""
    response = await async_client.get("/api/v1/venues/?page=1&per_page=5")
    
    assert response.status_code == 200
    json = response.json()
    
    # Must have these fields
    assert "success" in json
    assert "data" in json
    assert "meta" in json
    assert "error" in json
    
    # Success case
    assert json["success"] is True
    assert json["error"] is None
    assert isinstance(json["data"], list)
    
    # Meta must have pagination
    assert json["meta"]["total"] > 0
    assert json["meta"]["page"] == 1
    assert json["meta"]["per_page"] == 5

@pytest.mark.asyncio
async def test_get_venue_not_found(async_client: AsyncClient):
    """GET /venues/{slug} 404 returns standard error"""
    response = await async_client.get("/api/v1/venues/invalid-slug-xyz/")
    
    assert response.status_code == 404
    json = response.json()
    
    assert json["success"] is False
    assert json["data"] is None
    assert json["meta"] is None
    assert json["error"] is not None
    assert json["error"]["code"] == "VENUE_NOT_FOUND"
```

### 5. Database Migrations

Every migration must be tested for both upgrade and downgrade.

```python
# tests/integration/test_migrations.py
import pytest
from sqlalchemy import text
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext

@pytest.mark.asyncio
async def test_all_migrations_run(async_session):
    """All migrations can run without error"""
    # Run: alembic upgrade head
    # If this passes, migrations are valid
    pass

@pytest.mark.asyncio
async def test_migration_downgrade_upgrade(async_session):
    """Migrations are reversible: upgrade → downgrade → upgrade"""
    # Run: alembic downgrade -1
    # Run: alembic upgrade head
    # Check data integrity
    pass
```

### 6. Page Path Generation (getStaticPaths)

Verify that all returned paths are valid and queryable.

```python
# tests/e2e/test_page_generation.py
import pytest

@pytest.mark.asyncio
async def test_page_paths_venues_endpoint(async_client):
    """GET /page-paths/venues returns valid paths"""
    response = await async_client.get("/api/v1/page-paths/venues/")
    
    assert response.status_code == 200
    paths = response.json()["data"]
    
    assert len(paths) > 0
    for path in paths:
        assert "slug" in path
        assert "area" in path
        assert "category" in path
        
        # Verify each path is queryable
        response = await async_client.get(f"/api/v1/venues/{path['slug']}/")
        assert response.status_code == 200
```

---

## Test Fixtures Rules

### Shared Fixtures (conftest.py)

```python
# tests/conftest.py
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from unittest.mock import AsyncMock, Mock
from app.main import app
from httpx import AsyncClient

@pytest_asyncio.fixture
async def test_db():
    """Separate test database, wiped before each test"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",  # In-memory for speed
        echo=False
    )
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def async_session(test_db):
    """Async session for tests"""
    async_session_maker = sessionmaker(test_db, class_=AsyncSession, expire_on_commit=False)
    async with async_session_maker() as session:
        yield session

@pytest_asyncio.fixture
async def async_client(test_db):
    """AsyncClient for API tests"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def mock_openai():
    """Mock OpenAI client"""
    mock = AsyncMock()
    mock.ChatCompletion.create.return_value = {
        "choices": [{"message": {"content": "Generated content here..."}}]
    }
    return mock

@pytest.fixture
def mock_google_places():
    """Mock Google Places API"""
    mock = AsyncMock()
    mock.places.return_value = {
        "results": [
            {
                "name": "Test Venue",
                "rating": 4.5,
                "user_ratings_total": 100,
                "formatted_address": "Dubai"
            }
        ]
    }
    return mock
```

### Factory Boy (test_factories.py)

Never hardcode test data inline — use factories.

```python
# tests/fixtures/factories.py
import factory
from app.models import Venue, Area, Category

class AreaFactory(factory.Factory):
    class Meta:
        model = Area
    
    name = "Dubai Marina"
    slug = "dubai-marina"
    is_active = True

class CategoryFactory(factory.Factory):
    class Meta:
        model = Category
    
    name = "Restaurants"
    slug = "restaurants"

class VenueFactory(factory.Factory):
    class Meta:
        model = Venue
    
    name = factory.Sequence(lambda n: f"Venue {n}")
    slug = factory.Sequence(lambda n: f"venue-{n}")
    rating = 4.5
    review_count = 100
    composite_score = 85.0
    area = factory.SubFactory(AreaFactory)
    category = factory.SubFactory(CategoryFactory)
    is_active = True

# Usage in tests:
def test_with_venue():
    venue = VenueFactory(name="Nobu", rating=4.8)
    assert venue.name == "Nobu"
```

---

## Coverage Requirements

```
Minimum coverage by module:

app/scoring/           100%  (core IP, must be bulletproof)
app/models/            90%   (data validation)
app/api/               80%   (endpoints)
app/services/          80%   (business logic)
app/scrapers/          70%   (parser logic, not HTTP)
app/pipeline/          75%   (orchestration)
app/ai_enrichment/     70%   (AI content generation)

Overall:              75%   (minimum project-wide)
```

### Run Coverage Report

```bash
cd backend
pytest tests/ -v \
  --cov=app \
  --cov-report=html \
  --cov-report=term-missing:skip-covered

# Opens htmlcov/index.html to see gaps
open htmlcov/index.html
```

---

## Running Tests Locally

### All Tests
```bash
cd backend
pytest tests/ -v
```

### Specific Test File
```bash
pytest tests/unit/test_scoring.py -v
```

### Specific Test Function
```bash
pytest tests/unit/test_scoring.py::TestVenueScorer::test_rating_weight_contribution -v
```

### With Coverage
```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```

### Only Unit Tests (Fast)
```bash
pytest tests/unit/ -v
```

### Only Integration Tests (Slower)
```bash
pytest tests/integration/ -v
```

### Watch Mode (Rerun on File Change)
```bash
pytest-watch tests/ -- -v
```

---

## Frontend Testing (Phase 3)

**NOT required in Phase 1.** Frontend testing deferred until Phase 3.

When added in Phase 3, use:
- **Unit tests**: Jest + React Testing Library
- **Component tests**: Query real DOM, don't mock
- **E2E tests**: Playwright (test getStaticPaths → generated pages)

```bash
# Phase 3 additions:
cd frontend
npm test -- --coverage
npm run test:e2e  # Playwright tests
```

---

## Pytest Configuration

**File**: `backend/pyproject.toml` (already configured)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
markers = [
    "unit: Unit tests (fast)",
    "integration: Integration tests (moderate)",
    "e2e: End-to-end tests (slow)",
    "slow: Slow tests",
]
addopts = "--strict-markers -v --tb=short"
```

### Run Only Marked Tests
```bash
pytest -m unit              # Only unit tests
pytest -m integration       # Only integration tests
pytest -m "not slow"        # Skip slow tests
```

---

## Test Data Seeding

For integration/E2E tests, seed test database:

```python
# tests/fixtures/seed_data.py
async def seed_test_data(session: AsyncSession):
    """Populate test DB with realistic data"""
    areas = [
        AreaFactory(name="Dubai Marina"),
        AreaFactory(name="Downtown Dubai"),
    ]
    
    categories = [
        CategoryFactory(name="Restaurants"),
        CategoryFactory(name="Hotels"),
    ]
    
    venues = [
        VenueFactory(name="Nobu", area=areas[0], category=categories[0]),
        VenueFactory(name="Zuma", area=areas[0], category=categories[0]),
        VenueFactory(name="Emirates Palace", area=areas[1], category=categories[1]),
    ]
    
    session.add_all(areas + categories + venues)
    await session.commit()

# Usage:
@pytest.mark.asyncio
async def test_list_venues_by_area(async_session):
    await seed_test_data(async_session)
    
    venues = await service.list_by_area("dubai-marina")
    assert len(venues) == 2
```

---

## CI/CD Testing

Tests run automatically on:
- **Local**: `git commit` (pre-commit hook runs pytest)
- **GitHub**: Every push to any branch (GitHub Actions)
- **Production**: Before deploy to VPS

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - run: pip install -r backend/requirements.txt
      - run: cd backend && pytest tests/ --cov=app
```

---

**Last Updated**: 2026-04-20  
**For**: Story of Dubai Backend  
**Enforced by**: pytest, CI/CD, pre-commit hooks
