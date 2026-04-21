# Run Story of Dubai Locally — Complete Step-by-Step Guide

**Estimated Time**: 30-40 minutes total  
**Goal**: Get both frontend and backend running, see data flow in action

---

## System Check (2 minutes)

First, verify you have all required software:

```bash
# Check Node.js
node --version
# Expected: v20+

# Check npm
npm --version
# Expected: 10+

# Check Python
python3 --version
# Expected: 3.12+

# Check PostgreSQL
psql --version
# Expected: PostgreSQL 14+

# Check Redis
redis-cli --version
# Expected: redis-cli 7+
```

**If any are missing**: Stop here and install them before continuing.

---

## PART 1: PostgreSQL & Redis Setup (10 minutes)

### Option A: Using Docker (Recommended if you have Docker)

```bash
# Terminal 1: Start PostgreSQL
docker run --name storyofdubai-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d postgres:16-alpine

# Terminal 2: Start Redis
docker run --name storyofdubai-redis \
  -p 6379:6379 \
  -d redis:7-alpine

# Verify they're running
docker ps
# You should see two containers listed
```

### Option B: Using Local Installation

If you have PostgreSQL and Redis installed locally:

```bash
# Check PostgreSQL is running
psql -U postgres -c "SELECT 1"
# Expected: Should return "1"

# Check Redis is running
redis-cli ping
# Expected: PONG
```

---

## PART 2: Backend Setup (10 minutes)

### Step 1: Create Virtual Environment

```bash
cd backend

# Create venv (one-time only)
python3.12 -m venv venv

# Activate venv
source venv/bin/activate

# Verify activation (you should see (venv) in prompt)
which python
```

### Step 2: Install Dependencies

```bash
# Still in backend/ with venv activated
pip install -r requirements.txt

# This takes 2-3 minutes
# You should see "Successfully installed X packages"
```

### Step 3: Create/Update .env File

```bash
# Create .env in backend/ with these values:
cat > .env << 'EOF'
# App
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key-min-32-chars-change-in-production

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/storyofdubai
DATABASE_URL_SYNC=postgresql://postgres:postgres@localhost:5432/storyofdubai

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# APIs (leave empty for now)
OPENAI_API_KEY=
GOOGLE_PLACES_API_KEY=

# Pagination
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
EOF
```

### Step 4: Create Database

```bash
# Still in backend/ with venv activated

# Create database
psql -U postgres -c "CREATE DATABASE storyofdubai;"

# Run migrations
alembic upgrade head

# Verify (should return count of 0 for empty tables)
psql $DATABASE_URL -c "SELECT COUNT(*) FROM areas;"
```

### Step 5: Insert Sample Data (Optional but Recommended)

```bash
# Still in backend/ with venv activated
# Create a script to seed sample data

python << 'EOF'
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal, async_engine, Base
from app.models import Area, Category, Venue
from datetime import datetime

async def seed_data():
    # Create tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with AsyncSessionLocal() as session:
        # Create areas
        areas = [
            Area(name="Dubai Marina", slug="dubai-marina"),
            Area(name="Downtown Dubai", slug="downtown-dubai"),
            Area(name="Business Bay", slug="business-bay"),
            Area(name="Jumeirah Village Circle", slug="jumeirah-village-circle"),
        ]
        
        for area in areas:
            session.add(area)
        
        await session.flush()
        
        # Create category
        category = Category(name="Restaurants", slug="restaurants")
        session.add(category)
        
        await session.flush()
        
        # Create sample venues
        venues = [
            Venue(
                name="Nobu Dubai Marina",
                slug="nobu-dubai-marina",
                area_id=areas[0].id,
                category_id=category.id,
                google_rating=4.8,
                review_count=1240,
                price_tier=3,
                composite_score=91.25,
                phone="+971 4 777 6777",
                address="Al Marjan Island, Dubai Marina, Dubai",
                website="https://www.noburestaurants.com",
                is_active=True,
                last_scraped_at=datetime.utcnow().isoformat(),
            ),
            Venue(
                name="Zuma Dubai Marina",
                slug="zuma-dubai-marina",
                area_id=areas[0].id,
                category_id=category.id,
                google_rating=4.7,
                review_count=890,
                price_tier=3,
                composite_score=85.50,
                phone="+971 4 425 5560",
                address="Gate Village 6, DIFC, Dubai",
                website="https://www.zumarestaurant.com",
                is_active=True,
                last_scraped_at=datetime.utcnow().isoformat(),
            ),
            Venue(
                name="Pai Thai Downtown",
                slug="pai-thai-downtown",
                area_id=areas[1].id,
                category_id=category.id,
                google_rating=4.5,
                review_count=560,
                price_tier=2,
                composite_score=78.75,
                phone="+971 4 424 0999",
                address="Souk Al Bahar, Old Town, Downtown Dubai",
                website="https://www.paithai.ae",
                is_active=True,
                last_scraped_at=datetime.utcnow().isoformat(),
            ),
        ]
        
        for venue in venues:
            session.add(venue)
        
        await session.commit()
        print("✅ Sample data inserted!")
        print(f"   - {len(areas)} areas")
        print(f"   - {len(venues)} venues")

asyncio.run(seed_data())
EOF
```

---

## PART 3: Start Backend API (5 minutes)

```bash
# Terminal 3: Backend API
cd backend
source venv/bin/activate

# Start FastAPI server
uvicorn app.main:app --reload --port 8000

# You should see:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete

# The server auto-reloads when you change code
```

**Verify API is running**:
```bash
# Open new terminal (Terminal 4)
curl http://localhost:8000/api/v1/health

# Expected response:
# {"success":true,"data":null,"meta":null,"error":null,"status":"healthy",...}
```

---

## PART 4: Frontend Setup (5 minutes)

### Terminal 5: Frontend Setup

```bash
# From project root
cd frontend

# Install dependencies (one-time, ~30 seconds)
npm install

# You should see "added X packages"
```

### Setup Frontend Environment

```bash
# Create .env.local in frontend/
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SITE_URL=http://localhost:3000
EOF

# Verify it's created
cat .env.local
```

---

## PART 5: Start Frontend Dev Server (3 minutes)

```bash
# Still in frontend/ (Terminal 5)
# Kill if npm install is still running

npm run dev

# You should see:
# ▲ Next.js 14.x
# - Local:        http://localhost
:3000
# - Environments: .env.local
# 
# ✓ Ready in Xs
```

---

## PART 6: See It All Working (5 minutes)

### 1. Test API Endpoints

Open a new terminal and run these:

```bash
# Terminal 6

# Get all areas
curl http://localhost:8000/api/v1/areas/ | jq

# Get all categories
curl http://localhost:8000/api/v1/categories/ | jq

# Get all venues
curl http://localhost:8000/api/v1/venues/ | jq

# Get single venue by slug
curl http://localhost:8000/api/v1/venues/nobu-dubai-marina/ | jq

# Get venues in Dubai Marina area
curl "http://localhost:8000/api/v1/venues/?area=dubai-marina" | jq
```

**Expected Response Format**:
```json
{
  "success": true,
  "data": [
    {
      "id": "...",
      "name": "Nobu Dubai Marina",
      "slug": "nobu-dubai-marina",
      "google_rating": 4.8,
      "review_count": 1240,
      "composite_score": 91.25,
      ...
    }
  ],
  "meta": {
    "total": 3,
    "page": 1,
    "per_page": 20,
    "has_next": false
  },
  "error": null
}
```

### 2. View Frontend Pages

Open your browser:

```
http://localhost:3000/
```

**You should see**:
- ✅ Homepage with "The Story of Dubai" title
- ✅ 6 category cards (Restaurants, Hotels, Attractions, etc.)
- ✅ 10 top areas listed
- ✅ Stats showing "10,000+ Pages indexed", "Daily updates", "40+ areas covered"

Click on "Restaurants" category → Should show:
```
http://localhost:3000/restaurants/
```

But you might see a 404 because we haven't generated the static pages yet. Let's do that:

### 3. Build and Serve Static Pages

```bash
# Terminal 7: Build frontend
cd frontend

# Build all static pages (1-2 minutes)
npm run build

# You should see:
# ▲ Next.js 14.x
# ✓ Compiled successfully
# ✓ Linting and checking validity of types
# ✓ Collecting page data (takes ~1min)
# ✓ Generating static pages (takes ~1min)
# 
# Route (pages)                              Size     First Load JS
# ├ ○ /                                      2.51 kB        84.9 kB
# ├ ● /[category]/[area]                     3.64 kB        86.1 kB
# ├ ● /[category]/[area]/[venue]             3.19 kB        85.6 kB
# └ ...
```

### 4. View Built Pages

```bash
# After build completes, start production server
npm start

# You should see:
# > next@14.x start
# ▲ Next.js 14.x (Server)
# - Local: http://localhost:3000
```

Now visit:
```
http://localhost:3000/restaurants/dubai-marina/
```

**You should see**:
- ✅ Area page with "Restaurants in Dubai Marina" heading
- ✅ List of 3 restaurants (Nobu, Zuma, Pai Thai)
- ✅ Each with rating, review count, score badge
- ✅ "Rank 1", "Rank 2", "Rank 3" indicators
- ✅ Schema.org markup in page source

Click on first restaurant:
```
http://localhost:3000/restaurants/dubai-marina/nobu-dubai-marina/
```

**You should see**:
- ✅ Venue name "Nobu Dubai Marina"
- ✅ Rating: 4.8⭐ (1,240 reviews)
- ✅ Score badge: "Exceptional" (green, 91.25/100)
- ✅ Address, phone, website
- ✅ "Reserve at TheFork" affiliate button
- ✅ Breadcrumb navigation
- ✅ Schema.org LocalBusiness markup

---

## PART 7: Run Celery Worker (Optional, for scheduled tasks)

If you want to test Celery tasks:

```bash
# Terminal 8: Celery Worker
cd backend
source venv/bin/activate

# Start worker
celery -A app.celery_app worker --loglevel=info

# You should see:
# ---------- celery@hostname ----------
# [Tasks]
#   - app.pipeline.tasks.run_ai_enrichment_pending
#   - app.pipeline.tasks.run_scoring_engine_all
#   - app.pipeline.tasks.scrape_google_places_all_areas
#   - ...
# ---------- [Workers: 1 (online)]
```

---

## Complete Terminal Layout Reference

Here's what your terminal tabs should look like:

```
Terminal 1: PostgreSQL (Docker)
  docker run postgres:16-alpine

Terminal 2: Redis (Docker)
  docker run redis:7-alpine

Terminal 3: FastAPI Backend
  cd backend && uvicorn app.main:app --reload

Terminal 4: API Testing
  (for curl commands)

Terminal 5: Frontend Dev
  cd frontend && npm run dev
  (During development - hot reload enabled)

Terminal 6: Additional Testing
  (for more curl commands)

Terminal 7: Frontend Build & Production
  cd frontend && npm run build && npm start
  (After build - production server)

Terminal 8: Celery Worker (Optional)
  cd backend && celery -A app.celery_app worker --loglevel=info
```

---

## URL Reference

Once everything is running:

| URL | Purpose | Status |
|-----|---------|--------|
| http://localhost:8000/api/v1/health | API health check | ✅ Always works |
| http://localhost:8000/api/v1/areas/ | All areas (JSON) | ✅ Works |
| http://localhost:8000/api/v1/venues/ | All venues (JSON) | ✅ Works |
| http://localhost:3000/ | Homepage | ✅ Works |
| http://localhost:3000/restaurants/ | Restaurants list | ⚠️ Need build |
| http://localhost:3000/restaurants/dubai-marina/ | Area page | ⚠️ Need build |
| http://localhost:3000/restaurants/dubai-marina/nobu/ | Venue page | ⚠️ Need build |

⚠️ = Requires `npm run build` first

---

## Common Issues & Fixes

### "Port 8000 already in use"
```bash
# Kill the process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --port 8001
```

### "Database connection refused"
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Or restart it
docker restart storyofdubai-postgres
```

### "Redis connection refused"
```bash
# Check Redis is running
docker ps | grep redis

# Or restart it
docker restart storyofdubai-redis
```

### "npm command not found"
```bash
# Check Node.js installed
node --version

# If not, install from nodejs.org
# Then try again
npm --version
```

### "Python venv not activating"
```bash
# Make sure you're in backend/ directory
cd backend

# Try explicit activation
source venv/bin/activate

# Verify (should show (venv) in prompt)
echo $VIRTUAL_ENV
```

### "API returns 404 for venues"
```bash
# Verify sample data was inserted
psql $DATABASE_URL -c "SELECT COUNT(*) FROM venues;"

# Should return 3 (from seed data)
# If 0, run the seed data script again
```

### "Frontend shows blank page"
```bash
# Check that API is running on port 8000
curl http://localhost:8000/api/v1/health

# Check that .env.local exists
cat frontend/.env.local

# Should show API_URL=http://localhost:8000
```

---

## Development Workflow

Once everything is running:

### To Edit Backend Code
1. Files in `backend/app/` auto-reload (uvicorn --reload)
2. Changes apply immediately (no restart needed)
3. Check http://localhost:8000/api/v1/health to verify

### To Edit Frontend Code
1. Files in `frontend/` auto-reload (next dev)
2. Changes apply immediately in browser
3. Browser hot-reloads automatically

### To View Database Changes
```bash
# Check current data
psql $DATABASE_URL -c "SELECT name, composite_score FROM venues ORDER BY composite_score DESC;"
```

---

## Success Checklist

When complete, you should see:

- [ ] ✅ FastAPI running on http://localhost:8000
- [ ] ✅ API health endpoint returns JSON
- [ ] ✅ Venues in database (psql shows 3 rows)
- [ ] ✅ Homepage loads at http://localhost:3000
- [ ] ✅ Category page shows after npm run build
- [ ] ✅ Venue detail page shows restaurant info
- [ ] ✅ Rating badges colored correctly (green for high score)
- [ ] ✅ Schema.org markup in page source (view-source:)

---

## Next Steps After Getting It Running

1. **Test the scraper** (Phase 3a)
   ```bash
   # In backend/ with venv activated
   python run_scraper_demo.py
   # (Requires GOOGLE_PLACES_API_KEY)
   ```

2. **Add more sample data**
   - Edit the seed script above to add more venues
   - Rebuild frontend to see new pages

3. **Test with Celery**
   ```bash
   # Terminal 8: Start Celery worker
   celery -A app.celery_app worker --loglevel=info
   
   # Terminal 4: Trigger task
   python -c "from app.pipeline.tasks import run_scoring_engine_all; print(run_scoring_engine_all())"
   ```

4. **Explore the code**
   - `backend/app/models/` — Database models
   - `backend/app/api/v1/` — API endpoints
   - `frontend/pages/` — Website pages
   - `frontend/components/` — Reusable components

---

## Time Breakdown

- PostgreSQL + Redis: 2 minutes
- Backend setup: 10 minutes
- Frontend setup: 5 minutes
- Start servers: 3 minutes
- Build and view: 5 minutes
- **Total: ~25 minutes**

---

**You're now running the complete Story of Dubai project locally!** 🎉

API endpoint working ✅  
Frontend rendering ✅  
Database connected ✅  
Ready for Phase 3b ✅
