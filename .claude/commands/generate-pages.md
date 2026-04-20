# /generate-pages — Trigger Next.js Static Page Generation

When user types `/generate-pages [template_type]`, trigger AI enrichment and Next.js static page build for the specified template.

---

## Template Types

| Type | Purpose | Pages Generated |
|------|---------|-----------------|
| `venue-area` | Restaurants/hotels by area | area × category × venues |
| `properties` | Real estate listings | area × bedrooms × price ranges |
| `visa-guides` | Visa information by nationality | nationality × visa type |
| `buildings` | Building/developer showcase | developer × building |
| `companies` | Company registry | sector × company |
| `all` | All templates (full build) | 10,000+ pages |

---

## Step 1: Check Data Counts

Before generating, verify sufficient data exists in database:

```bash
cd backend
python -c "
from sqlalchemy import select, func
from app.database import SessionLocal
from app.models import Venue, Property, VisaGuide, Company

session = SessionLocal()

# Count venues by area
result = session.execute(
  select(Venue.area, func.count(Venue.id))
  .where(Venue.is_active == True)
  .group_by(Venue.area)
)
print('VENUES BY AREA:')
for area, count in result:
  print(f'  {area}: {count}')

# Count properties
prop_count = session.execute(
  select(func.count(Property.id))
  .where(Property.is_active == True)
).scalar()
print(f'\\nPROPERTIES: {prop_count}')

# Count visa guides
visa_count = session.execute(
  select(func.count(VisaGuide.id))
  .where(VisaGuide.is_active == True)
).scalar()
print(f'VISA GUIDES: {visa_count}')

# Count companies
company_count = session.execute(
  select(func.count(Company.id))
  .where(Company.is_active == True)
).scalar()
print(f'COMPANIES: {company_count}')

session.close()
"
```

**Output should show**:
- At least 50+ venues per area (for meaningful content)
- At least 100+ properties (for property pages)
- At least 10+ visa guides
- At least 50+ companies

---

## Step 2: AI Enrichment (Optional)

Generate AI summaries for any pages missing `ai_summary`:

```bash
cd backend
python -m app.ai_enrichment.run \
  --type [template_type] \
  --missing-only \
  --verbose
```

**Example**:
```bash
python -m app.ai_enrichment.run --type venue-area --missing-only --verbose
```

**Output**:
```
AI Enrichment: venue-area
Found 120 venues missing ai_summary
Generating summaries using GPT-4o-mini...
[████████████████░░░░] 80/120 (3m 45s elapsed, ~4m total)
```

**Cost estimate**: ~$0.02 per 100 summaries (at GPT-4o-mini rates)

---

## Step 3: Build Frontend

Trigger Next.js to generate all static pages:

```bash
cd frontend
npm run build 2>&1 | tee build.log
```

**This process**:
1. Calls `getStaticPaths()` → fetches all valid paths from API
2. Calls `getStaticProps()` for each path → fetches page data
3. Renders React → HTML files in `.next/`
4. Outputs progress and build times

**Expected output**:
```
> next build

■ Building application...
  ■ Compiling client
  ✓ Compiling server

  ✓ Generating static pages (1,847 pages)
  ✓ Creating preload map
  ✓ Generating pages map
  ✓ Collecting build traces
  ■ Finalizing page optimization
  
  Route                                           Size
  ├ λ /api/health                                2.5 kB
  ├ ○ /                                          15 kB
  ├ ○ /restaurants/[area]/[slug]                42 kB
  ├ ○ /properties/[area]/[slug]                 38 kB
  ...
  
Build: 847s
Exports: 25s
```

---

## Step 4: Verify Generated Pages

Count and verify pages were generated:

```bash
# Count all generated HTML pages
find frontend/.next -name "*.html" | wc -l

# Verify specific page paths
ls -la frontend/.next/server/pages/restaurants/dubai-marina/
ls -la frontend/.next/server/pages/properties/
```

**Expected**:
- Should see thousands of HTML files (10,000+ for full build)
- Each area should have separate directory
- Build should complete without errors

---

## Step 5: Verify Sitemap

Check dynamic sitemap generation:

```bash
# Start dev server (or use production server)
cd frontend
npm run dev &
sleep 5

# Verify sitemap
curl -s http://localhost:3000/sitemap.xml | head -30
curl -s http://localhost:3000/sitemap.xml | grep -c "<url>"
```

**Expected output**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://storyofdubai.com/</loc>
    <lastmod>2026-04-20T14:30:00Z</lastmod>
  </url>
  <url>
    <loc>https://storyofdubai.com/restaurants/dubai-marina/nobu</loc>
    ...
```

Count of `<url>` tags = total indexed pages.

---

## Step 6: Test Page Loading

Verify a few generated pages load correctly:

```bash
# Test a venue page
curl -s http://localhost:3000/restaurants/dubai-marina/nobu | grep -o "<title>.*</title>"

# Test a property page
curl -s http://localhost:3000/properties/downtown-dubai/ | grep -o "<h1>.*</h1>"

# Check for schema.org markup
curl -s http://localhost:3000/restaurants/dubai-marina/nobu | grep "schema.org"
```

**Expected**:
- Page has proper title
- Page has content headers
- Page includes JSON-LD schema markup

---

## Step 7: Report Results

Show final summary:

```
### Page Generation Report: [template_type]

**Data Summary**:
- Total venues: 1,247
- Total properties: 3,892
- Total visa guides: 186
- Total companies: 5,431

**AI Enrichment**:
- Pages enriched: 847
- Cost: ~$0.16
- Time: 12m 34s

**Build Results**:
- Pages generated: 10,432
- Build time: 847 seconds (14m 7s)
- Largest page: 145 kB
- Smallest page: 12 kB

**Sitemap**:
- Total URLs: 10,432
- Compressed size: 2.3 MB

**Verification**:
✓ Sample pages load correctly
✓ Schema.org markup present
✓ No build errors or warnings
✓ All expected paths generated

**Next Step**: Deploy to Vercel with /deploy frontend
```

---

## Step 8: Commit Build Artifacts (Optional)

If using static export (not ISR), commit generated files:

```bash
git add frontend/.next/
git commit -m "build: regenerate static pages (1,247 venues, 3,892 properties)"
```

Note: With ISR (Incremental Static Regeneration), don't commit `.next/` — Vercel handles builds.

---

## Troubleshooting

### Build hangs on `getStaticPaths()`
- Check API is running: `curl http://localhost:8000/api/v1/health`
- Check database has data: `SELECT COUNT(*) FROM venues;`
- Increase timeout: edit `next.config.js` → `staticPageGenerationTimeout: 3600`

### Out of memory during build
- Reduce batch size: edit `next.config.js`
- Build each template separately instead of `all`
- Increase server RAM or use ISR instead

### Pages missing `ai_summary`
- Run AI enrichment first: `/generate-pages [type]` includes this step
- Or run manually: `python -m app.ai_enrichment.run --type [type]`

### Sitemap empty or wrong
- Check API endpoint returns paths: `curl http://localhost:8000/api/v1/page-paths/venues/`
- Verify sitemap generation code in `pages/sitemap.xml.ts`

### Schema.org markup missing
- Check page template includes `<Head>` with schema
- Verify `app/utils/schema.ts` generates valid JSON-LD

---

## Best Practices

✅ **DO**:
- Run after any scraper completes (fresh data)
- Run after changing page template/styling
- Verify sitemap after generation (for SEO)
- Test a few pages to ensure correctness
- Deploy to Vercel immediately after building

❌ **DON'T**:
- Generate without sufficient data (sparse pages rank poorly)
- Skip AI enrichment (pages need unique content)
- Generate unnecessarily (build takes 15+ minutes)
- Commit `.next/` to git (Vercel builds on deploy)

---

**Last Updated**: 2026-04-20  
**For**: Story of Dubai Page Generation  
**Enforced by**: next.config.js, getStaticPaths/getStaticProps
