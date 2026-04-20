# Testing Rules

## Backend (Python)
- **Framework**: pytest + pytest-asyncio
- **Coverage**: Minimum 70% for core logic (scrapers, scoring, enrichment)
- **Mocking**: Use unittest.mock for external APIs (Google Places, OpenAI)
- **Database**: Use in-memory SQLite for unit tests, PostgreSQL for integration tests
- **Fixtures**: In `backend/tests/conftest.py` (database, client, API keys)
- **Organization**: `backend/tests/` mirrors `app/` structure

## Test File Structure
```
backend/tests/
├── conftest.py                    # Shared fixtures
├── test_api/
│   └── test_restaurants.py        # GET, POST, PUT, DELETE
├── test_scrapers/
│   └── test_google_places.py      # Scraper logic
├── test_models/
│   └── test_schema_validation.py  # Pydantic validation
└── test_pipeline/
    └── test_scoring.py            # Scoring algorithm
```

## Test Naming & Structure
```python
# ❌ Bad
def test_it():
    pass

# ✅ Good
def test_get_restaurants_returns_200_when_valid_page():
    response = client.get("/api/v1/restaurants?page=1")
    assert response.status_code == 200

def test_get_restaurants_returns_400_when_page_less_than_1():
    response = client.get("/api/v1/restaurants?page=0")
    assert response.status_code == 400
```

## Frontend (TypeScript)
- **Framework**: Jest + React Testing Library
- **Coverage**: 60% minimum for components
- **Unit tests**: Pure functions (utils), component logic
- **No E2E tests**: Testing Library for user interaction, not Cypress/Playwright
- **Mocking**: Mock API calls in tests, not real backend

## Integration Tests
- **When**: Critical paths only (user flow: list → view → affiliate click)
- **Tool**: pytest with real PostgreSQL test database
- **Setup**: Docker Compose with postgres:16-alpine
- **Cleanup**: Each test runs in a transaction that rolls back

## CI/CD Testing
- **Hook**: `pre-commit` hook validates Python with `black --check` and `ruff check`
- **GitHub Actions**: Run tests on every PR
- **Pass criteria**: All tests pass, coverage >= minimum

## Running Tests Locally
```bash
# Backend
cd backend
pytest -v --cov=app
pytest backend/tests/test_api/ -k "restaurants"  # Specific test

# Frontend
cd frontend
npm test -- --coverage
npm test -- --watch
```

## Debugging Tests
```python
# Add print debugging
import pytest
def test_something():
    result = do_something()
    print(f"DEBUG: {result}")  # Visible with -s flag
    assert result == expected

# Run with output
pytest -s test_file.py
```

## Performance Tests
- **Endpoint response time**: Target < 200ms for GET (no enrichment)
- **Page generation**: 10k pages in < 2 hours
- **Scraper throughput**: 100 entities/minute (with 2s rate limit)
