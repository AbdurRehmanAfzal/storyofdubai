# /scraper-run — Run a Scraper Manually

When user types `/scraper-run [scraper_name] [options]`, execute a scraper with full workflow and results reporting.

---

## Available Scrapers

| Scraper | Purpose | Usage |
|---------|---------|-------|
| `google-places` | Venues from Google Places API | `/scraper-run google-places --area dubai-marina --limit 50` |
| `bayut` | Property listings from Bayut.com | `/scraper-run bayut --area downtown --bedrooms 2` |
| `visa-portal` | UAE visa information | `/scraper-run visa-portal --country us` |
| `companies` | Company data from DED portal | `/scraper-run companies --sector fintech --limit 100` |

---

## Step 1: Verify Prerequisites

Before running any scraper, verify:

```bash
# Check environment variables are set
echo "DATABASE_URL: ${DATABASE_URL:?missing}"
echo "OPENAI_API_KEY: ${OPENAI_API_KEY:?missing}"
echo "GOOGLE_PLACES_API_KEY: ${GOOGLE_PLACES_API_KEY:?missing}"

# Check database connection
cd backend && python -c "from app.database import SessionLocal; SessionLocal().execute('SELECT 1')"

# Check Redis (for caching)
redis-cli ping  # Should return PONG
```

---

## Step 2: Dry-Run Mode

Run scraper in dry-run mode FIRST (show what would be collected, without saving):

```bash
cd backend
python -m app.scrapers.[scraper_name] \
  --dry-run \
  --area [area] \
  --limit [limit]
```

**Example**:
```bash
python -m app.scrapers.google_places --dry-run --area dubai-marina --limit 50
```

**Output**:
```
Dry-run: Google Places Scraper
Area: dubai-marina
Limit: 50
Found 48 venues (46 new, 2 updates)
Sample records:
  1. Nobu (rating: 4.8, reviews: 1240)
  2. Zuma (rating: 4.7, reviews: 890)
  ...
Estimated time: 3 minutes (48 records × 2s delay + parsing)
```

---

## Step 3: Ask for Confirmation

Show results and ask:

```
Dry run found 48 venues to collect.
This will take ~3 minutes (with 2s rate limiting).
Proceed with actual scrape? (yes/no)
```

Only continue if user confirms.

---

## Step 4: Run Actual Scraper

If confirmed, run the scraper:

```bash
cd backend
python -m app.scrapers.[scraper_name] \
  --area [area] \
  --limit [limit] \
  --verbose  # Show progress
```

**Example**:
```bash
python -m app.scrapers.google_places --area dubai-marina --limit 50 --verbose
```

**Monitor output for**:
- Rate limiting delays (should see 2-3s pauses between requests)
- Error messages (rate limit hit, API errors, parse failures)
- Progress: `[10/48] Processing Nobu...`

---

## Step 5: Calculate Scoring

After scraper completes, run scoring engine on new/updated data:

```bash
cd backend
python -m app.scoring.run --area [area] --recalculate
```

**Example**:
```bash
python -m app.scoring.run --area dubai-marina --recalculate
```

This will:
- Calculate composite scores for all new venues
- Update any changed scores in database
- Invalidate cache (force refresh on next page generation)

---

## Step 6: Show Results

Report final results:

```
### Scrape Results: google-places (dubai-marina)

**Records Processed**: 48
- New records: 46
- Updated records: 2
- Errors: 0

**Timing**: 2m 45s (including 2s delays)
**API calls**: 48
**Database writes**: 48

**New venues added**:
  - Nobu (rating: 4.8, score: 92)
  - Zuma (rating: 4.7, score: 85)
  - ... (46 total)

**Action**: Scoring calculated, cache invalidated
**Next**: Run /generate-pages venue-area to build static pages
```

---

## Step 7: Update PROGRESS.md

Add to PROGRESS.md:

```markdown
## Session Notes (Current)
- Ran google-places scraper for dubai-marina (48 new venues)
- Calculated composite scores
- Ready for page generation
```

---

## Troubleshooting

### Scraper hangs
- Check Redis is running: `redis-cli ping`
- Check API rate limits: API may be blocking requests
- Increase delay: `--delay 5` (adds 5s between requests)

### Rate limit errors
- Reduce `--limit`: Try `--limit 20` instead of 50
- Increase `--delay`: Try `--delay 3` for 3s delays
- Check API quota in API dashboard (Google Places, etc.)

### Database connection fails
- Verify DATABASE_URL: `echo $DATABASE_URL`
- Check database is running: `psql $DATABASE_URL -c "SELECT 1"`
- Run migrations: `alembic upgrade head`

### Parser errors
- Check sample HTML/API response: `curl [api_url]`
- Verify scraper parsing logic (may need adjustment if site changed)
- Run with `--verbose` to see exact error

---

## Best Practices

✅ **DO**:
- Run `/security-audit` before running scrapers (check rate limiting, error handling)
- Run in dry-run mode first (never scrape blindly)
- Monitor logs while scraping (watch for rate limits, errors)
- Run scoring immediately after scraping (calculate fresh scores)
- Commit PROGRESS.md after scraping (track what was collected)

❌ **DON'T**:
- Run multiple scrapers simultaneously (hammers APIs)
- Skip dry-run mode (may collect duplicate data)
- Ignore rate limit errors (site may block IP)
- Run without checking credentials are set
- Leave scraper running unattended for hours

---

**Last Updated**: 2026-04-20  
**Enforced by**: .claude/rules/security.md (rate limiting, robots.txt, user-agent)
