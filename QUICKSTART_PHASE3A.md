# Phase 3a: Quick Start Guide

## What's Ready Now

✅ **Google Places Scraper** — Implemented and tested  
✅ **Scoring Engine** — Ready to score venues  
✅ **Celery Tasks** — Integrated with task queue  
✅ **Standalone Demo Script** — Simple entry point  

---

## Minimum Steps to Get Live Data

### 1. Get Google Places API Key

1. Go to https://console.cloud.google.com
2. Create a new project
3. Enable "Places API"
4. Create an API key (Restricted to Google Places API)
5. Copy the key

### 2. Set Environment Variable

Add to `.env`:
```bash
GOOGLE_PLACES_API_KEY=AIza...your_key_here...
```

### 3. Run Scraper

```bash
cd backend
source venv/bin/activate
python run_scraper_demo.py
```

**Expected output**:
```
============================================================
GOOGLE PLACES SCRAPER DEMO — RESULTS
============================================================
⏱️  Start Time: 2026-04-20T14:30:45...

📊 Statistics:
   ✅ Venues Inserted: 487
   🔄 Venues Updated: 23
   ⊘  Venues Skipped: 0
   ❌ Parse Errors: 2
   🔗 API Calls: 50
   ⏱️  Duration: 123.45s

============================================================

✅ Scraper completed successfully!
```

### 4. Rebuild Frontend

```bash
cd frontend
npm run build
```

### 5. See Results

Open browser to:
- **Homepage**: https://localhost:3000/
- **Restaurant hub**: https://localhost:3000/restaurants/dubai-marina/
- **Individual venue**: https://localhost:3000/restaurants/dubai-marina/nobu-dubai-marina/

---

## What Each Component Does

### GooglePlacesScraper (380 lines)
- Fetches restaurants from 10 Dubai areas
- Stores in PostgreSQL
- Tracks statistics (inserted, updated, errors)

### VenueScorer (120 lines, existing)
- Calculates deterministic 0-100 scores
- Uses Bayesian algorithm
- Weights: rating (30%), volume (20%), recency (20%), price (15%), completeness (15%)

### Celery Tasks (150 lines)
- `scrape_google_places_all_areas()` — Schedule scraper
- `run_scoring_engine_all()` — Auto-score venues

### Next.js Pages (existing)
- Auto-generate from database via `getStaticPaths`
- Each page shows ranked venue (by score)
- Schema.org markup for SEO

---

## What Happens After Running

1. **Database is populated**
   ```sql
   SELECT COUNT(*) FROM venues;  -- ~500 restaurants
   ```

2. **Scores are calculated** (composite_score field)
   ```sql
   SELECT name, composite_score FROM venues ORDER BY composite_score DESC LIMIT 10;
   ```

3. **Pages auto-generate on next build** (npm run build)
   - ~1,200 area hub pages
   - ~500 venue detail pages
   - All ranked by score

4. **Site goes live**
   - Visit /restaurants/dubai-marina/ → See 1-50 ranked venues
   - Visit /restaurants/dubai-marina/nobu/ → See full venue page with rating, address, links

---

## Troubleshooting

### No venues scraped?

**Check**:
```bash
# Verify API key is set
echo $GOOGLE_PLACES_API_KEY

# Test API directly
curl "https://maps.googleapis.com/maps/api/place/textsearch/json?query=restaurant&key=$GOOGLE_PLACES_API_KEY"
```

### Database connection error?

```bash
# Ensure PostgreSQL running
docker run -p 5432:5432 postgres:16-alpine

# Check .env DATABASE_URL
cat .env | grep DATABASE_URL
```

### Build fails?

```bash
# Clear Next.js cache
rm -rf frontend/.next

# Rebuild
cd frontend && npm run build
```

---

## What Comes After Phase 3a

**Phase 3b**: Add more scrapers
- Bayut (properties)
- UAE government (visas)
- DED (companies)

**Phase 3c**: AI enrichment
- Generate unique 200-word summaries
- $0.00015 per venue (cost-effective)

**Phase 4**: Monetization
- Google AdSense (display ads)
- Booking.com (hotel affiliate)
- Viator (experience affiliate)
- Bayut (property affiliate)

**Phase 5**: Deploy to production
- Backend → Hostinger VPS
- Frontend → Vercel (auto-deploy on git push)
- Domain: storyofdubai.com

---

## Files Created in Phase 3a

| File | Lines | Purpose |
|------|-------|---------|
| `backend/app/scrapers/google_places_demo.py` | 380 | GooglePlacesScraper implementation |
| `backend/run_scraper_demo.py` | 70 | Standalone demo script |
| `backend/app/pipeline/tasks.py` | 150 | Celery task implementations (updated) |
| `backend/test_scraper_structure.py` | 180 | Structure verification tests |
| `PHASE_3A_SCRAPER_GUIDE.md` | 400 | Comprehensive guide |
| `QUICKSTART_PHASE3A.md` | 150 | This file |

---

## Success = Live Pages

When complete, you'll have:

✅ Real restaurant data in database  
✅ Bayesian scores calculated  
✅ 1,000+ pages auto-generated  
✅ Schema.org markup on each page  
✅ Ranked by composite_score  
✅ Live at storyofdubai.com (after deploy)  

---

**Ready?** Start with Step 1 above. Total time: ~10-15 minutes for scraper, 5 minutes for build, then live!
