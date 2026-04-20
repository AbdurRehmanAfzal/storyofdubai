# SEO Strategy Knowledge — CRITICAL, DO NOT BREAK

This document defines the SEO strategy that **all architectural, content, and deployment decisions must serve**. Changes to any strategy here require documented approval.

---

## The Core SEO Principle

**storyofdubai.com wins search rankings by having the most comprehensive, data-fresh, structured content about Dubai across 10,000+ specific long-tail queries.**

Every architectural decision exists to serve this goal:
- ✅ Data freshness (scrapers run daily, ISR updates pages every 24h)
- ✅ Uniqueness (GPT-4o-mini generates unique intro per page)
- ✅ Structure (schema.org on every page, proper heading hierarchy)
- ✅ Internal linking (dense graph passes PageRank to deep pages)
- ✅ Crawlability (dynamic sitemap, mobile-optimized, fast)

---

## URL Architecture (IMMUTABLE Once Indexed)

**⚠️ WARNING**: Changing URL patterns after Google indexes pages **destroys ranking**. These patterns are LOCKED.

### Naming Rules

```
✅ GOOD
  /restaurants/dubai-marina/
  /apartments/downtown-dubai/2-bedroom/
  /visa-guide/united-states/visit-visa/
  /buildings/burj-khalifa/

❌ BAD
  /restaurants/Dubai Marina/ (capital letters)
  /restaurants?area=dubai-marina (query params in SEO URLs)
  /restaurants/dubai_marina (underscores)
  /restaurants/dubai-marina/1234/ (trailing IDs)
```

### Locked URL Patterns (Production URLs)

These are the **canonical URL structures** that all code must follow:

```
/[category]/[area]/
  ↳ Venue area hub (e.g., /restaurants/dubai-marina/)
  ↳ Data: top 20 venues in area+category, ordered by composite_score
  ↳ ISR: 86400 (24 hours)
  ↳ Meta: "Best {category} in {area} Dubai"

/[category]/[area]/[venue-slug]/
  ↳ Individual venue page (e.g., /restaurants/dubai-marina/nobu/)
  ↳ Data: single venue + nearby venues list
  ↳ ISR: 86400 (24 hours)
  ↳ Meta: "{name} - {category} in {area}"

/apartments/[area]/[bedrooms]-bedroom/[price-bucket]/
  ↳ Property filter page (e.g., /apartments/downtown/2-bedroom/100k-200k/)
  ↳ Price buckets: under-50k, 50k-100k, 100k-200k, 200k-plus (AED/year rent)
  ↳ ISR: 43200 (12 hours — prices change faster)
  ↳ Meta: "[area] 2-bedroom apartments {price_range}"

/buildings/[building-slug]/
  ↳ Building profile (e.g., /buildings/burj-khalifa/)
  ↳ Data: building details, location, nearby venues
  ↳ ISR: 604800 (7 days)

/developers/[developer-slug]/
  ↳ Developer profile (e.g., /developers/emaar/)
  ↳ Data: developer info, buildings, properties
  ↳ ISR: 604800 (7 days)

/visa-guide/[nationality]/[visa-type]/
  ↳ Visa information (e.g., /visa-guide/united-states/visit-visa/)
  ↳ Data: visa requirements, costs, timeline
  ↳ ISR: 604800 (7 days)

/freezone/[freezone-slug]/
  ↳ Freezone profile (e.g., /freezone/dubai-silicon-oasis/)
  ↳ Data: freezone info, companies, costs
  ↳ ISR: 604800 (7 days)

/freezone/[slug-a]-vs-[slug-b]/
  ↳ Freezone comparison (e.g., /freezone/dso-vs-jafza/)
  ↳ Data: side-by-side comparison table
  ↳ ISR: 604800 (7 days)

/sitemap.xml
  ↳ Dynamic sitemap (auto-generated from DB)
  ↳ Includes all is_active=true pages
  ↳ Priority: 1.0 (home), 0.8 (hubs), 0.6 (details)

/robots.txt
  ↳ Allow all, Disallow: /admin/, /api/
```

### Slug Generation Rules

Slugs are **permanent identifiers**. They must be:

1. **Lowercase**: "Nobu Dubai Marina" → "nobu-dubai-marina"
2. **Hyphens only**: "Al-Baraha" → "al-baraha" (NOT "al_baraha")
3. **ASCII only**: "مطعم النيل" → transliterated, never Arabic
4. **Unique per entity type**: Multiple restaurants can't have same slug
5. **Stable**: Never change once published

**Never add/remove words from slug after publication.**

---

## Page Quality Requirements (Google Helpful Content Compliance)

Every generated page MUST meet these minimum quality standards:

### Content Uniqueness
- [ ] **Unique H1** — Never duplicate H1 across any two pages (including different areas/categories)
- [ ] **Unique meta description** — Auto-generated from data (rating + area + category), not template-repeated
- [ ] **Unique introductory paragraph** — GPT-4o-mini generated, stored in DB's `ai_summary` field
  - Min 150 words, max 300 words
  - Must include entity name + location + category naturally
  - Must include call-to-action (affiliate link, reservation, etc.)

### Data Integrity
- [ ] **Real data only** — Minimum 5 actual venue/property listings per area page
  - Pages with < 5 real listings: DO NOT PUBLISH (set status=draft)
  - Better to have fewer pages with quality than thousands of thin pages
- [ ] **Current data** — Last updated date visible on page
  - Timestamp from database `updated_at` field
  - Show: "Last updated: 2 hours ago" or exact date

### Technical Requirements
- [ ] **Schema.org JSON-LD** — Appropriate type for page
- [ ] **Structured headings** — H1 → H2 → H3, proper hierarchy
- [ ] **Internal links** — At least 3 contextual links to related pages
- [ ] **Mobile optimized** — Responsive design, fast (Lighthouse > 85)
- [ ] **Breadcrumb navigation** — Visible + schema.org markup

---

## Schema.org Types by Page Type

Implement the **correct schema type** for each page. Google uses this for rich snippets and SERP features.

### Venue Area Hub → ItemList + BreadcrumbList
### Individual Venue → LocalBusiness + Review aggregate
### Property Listing → RealEstateListing + BreadcrumbList
### Visa Guide → HowTo + BreadcrumbList
### Building Profile → LandmarksOrHistoricalBuildings
### Freezone/Developer → Organization

---

## Internal Linking Strategy (PageRank Flow)

**Goal**: Create a dense internal link graph that passes PageRank from high-authority pages (area hubs) to deep pages (individual venues).

### Linking Rules

**From area hub** (`/restaurants/dubai-marina/`):
- Link to top 5 venues in that area
- Link to 5 other nearby area hubs (Dubai Hills, Downtown, Marina, etc.)
- Link to 3 cross-category pages (hotels in Dubai Marina, attractions, etc.)
- Total: 10-15 outbound links

**From individual venue** (`/restaurants/dubai-marina/nobu/`):
- Link back to area hub (reciprocal)
- Link to 3 nearby venues of same category
- Link to 2 cross-category pages
- Total: 5-8 outbound links

**From visa guide**: Link to freezone/relocation guides, area hubs

**From building profile**: Link to developer, area hub, nearby properties

---

## Sitemap Rules

### Structure
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="https://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://storyofdubai.com/</loc>
    <priority>1.0</priority>
    <changefreq>weekly</changefreq>
  </url>
  
  <url>
    <loc>https://storyofdubai.com/restaurants/dubai-marina/</loc>
    <priority>0.8</priority>
    <changefreq>daily</changefreq>
  </url>
  
  <url>
    <loc>https://storyofdubai.com/restaurants/dubai-marina/nobu/</loc>
    <priority>0.6</priority>
    <changefreq>daily</changefreq>
  </url>
</urlset>
```

### Priority Rules
- **Homepage**: 1.0, weekly
- **Area hubs**: 0.8, daily
- **Individual pages**: 0.6, daily
- **Visa guides**: 0.5, weekly
- **Building profiles**: 0.5, monthly

### Generation
- Auto-generated by FastAPI endpoint
- Includes only is_active=true pages
- Submitted to Google Search Console

---

## Content Pillar Strategy
Generate pages across these categories to dominate Dubai searches:

### Pillar 1: "Best [Cuisine] Restaurants in Dubai"
- **Pages**: ~1,200 (12 cuisines × 100 areas/neighborhoods)
- **Keywords**: "best Italian restaurants in Dubai Marina", "fine dining in Downtown Dubai"
- **Content**: Rating, reviews, cuisine type, location, reservation link
- **Affiliate**: TheFork (reservation commission), Booking.com (hotel referral)

### Pillar 2: "Dubai [Property Type] for Sale/Rent"
- **Pages**: ~2,400 (apartments, villas, studios × 30 areas × 3 price brackets)
- **Keywords**: "1BR apartment for rent in Downtown Dubai", "luxury villa Marina"
- **Content**: Price, size, amenities, rental yield, agent contact
- **Affiliate**: Bayut, PropertyFinder ($50-200 per lead)

### Pillar 3: "[Nationality] Visa to UAE — Requirements & Process"
- **Pages**: ~600 (50+ nationalities × visa types)
- **Keywords**: "Indian visa to UAE", "US citizen work visa Dubai"
- **Content**: Requirements, documents, processing time, eligibility
- **Affiliate**: PRO service links, visa consultants

### Pillar 4: "Companies & Startups in [Sector] Dubai"
- **Pages**: ~3,000 (20 sectors × 150 companies)
- **Keywords**: "fintech startups in Dubai", "logistics companies UAE"
- **Content**: Company overview, investment, hiring status
- **Affiliate**: B2B networks, recruitment platforms

### Pillar 5: "Top [Activity] in Dubai — 50 Must-Do Experiences"
- **Pages**: ~900 (category lists + individual experience pages)
- **Keywords**: "best adventures in Dubai", "free things to do Dubai"
- **Content**: Description, location, opening hours, tour operator
- **Affiliate**: Viator (8%), GetYourGuide, Klook

## SEO Fundamentals (On-Page)

### Page Structure
```html
<head>
  <title>Best {Cuisine} Restaurants in {Area}, Dubai | Story of Dubai</title>
  <meta name="description" content="Top-rated {cuisine} restaurants in {area}. Reviews, ratings, locations, and online reservations. Updated 2026.">
  
  <!-- JSON-LD Schema (MUST HAVE ON EVERY PAGE) -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "name": "{Restaurant Name}",
    "description": "{AI-generated 200-word intro}",
    "url": "{full_url}",
    "image": "{photo_url}",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "{address}",
      "addressLocality": "Dubai",
      "addressRegion": "Dubai",
      "postalCode": "{zip}",
      "addressCountry": "AE"
    },
    "telephone": "{phone}",
    "aggregateRating": {
      "@type": "AggregateRating",
      "ratingValue": "{rating}",
      "ratingCount": "{review_count}"
    }
  }
  </script>
</head>
<body>
  <h1>{Restaurant Name} — {Cuisine} in {Area}, Dubai</h1>
  <p class="intro">{AI-generated intro (200 words)}</p>
  
  <!-- Key facts -->
  <div class="facts">
    <p><strong>Rating:</strong> {rating}/5 ({review_count} reviews)</p>
    <p><strong>Location:</strong> {area}, Dubai</p>
    <p><strong>Cuisine:</strong> {cuisine}</p>
    <p><strong>Phone:</strong> {phone}</p>
  </div>
  
  <!-- CTA -->
  <a href="{reservation_link}" class="cta">Book a Table</a>
  <a href="{affiliate_link}" class="affiliate">View on Booking.com</a>
</body>
```

### Keyword Placement
- **H1 Tag**: Include primary keyword (e.g., "Best Italian Restaurants in Dubai Marina")
- **Meta Title**: 50-60 chars, include keyword
- **Meta Description**: 155-160 chars, persuasive
- **Body**: Keyword density 1-2% (not stuffing)
- **Internal links**: Link to related restaurants, areas, cuisines

### Content Quality
- **Length**: 500+ words (intro + facts + reviews + images)
- **Freshness**: Update last_update timestamp monthly
- **Uniqueness**: AI generates unique intros (cosine similarity check)
- **Readability**: Short paragraphs, bullet points, clear hierarchy

## Technical SEO

### Site Architecture
```
storyofdubai.com/
├── /restaurants/                      # Category landing pages
│   ├── /restaurants/dubai-marina/     # Area + category
│   └── /restaurants/italian/          # Cuisine pages
├── /apartments/                       # Property category
│   ├── /apartments/dubai-marina/1br/
│   └── /apartments/dubai-marina/2br/
├── /visa-guide/                       # Visa information
│   └── /visa-guide/indian/work-visa/
├── /companies/                        # Company directory
│   └── /companies/fintech/            # Sector pages
└── /experiences/                      # Tours & activities
    └── /experiences/desert-safari/
```

### URL Structure
- **Pattern**: /{entity_type}/{area_or_category}/{specific_entity}/
- **Slug generation**: Lowercase, kebab-case, max 75 chars
- **Examples**:
  - `/restaurants/dubai-marina/nobu/`
  - `/apartments/jbr/1-bedroom-apartment-for-rent/`
  - `/visa-guide/indian-nationals/dubai-work-visa/`

### Canonical Tags
```html
<link rel="canonical" href="https://storyofdubai.com/restaurants/dubai-marina/nobu/">
```

### Sitemap & Robots
```
# robots.txt
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
Sitemap: https://storyofdubai.com/sitemap.xml
```

**Sitemap generation** (Next.js):
```typescript
// pages/sitemap.xml.ts
export default function Sitemap() {
  return Pages.map(page => ({
    url: `https://storyofdubai.com${page.slug}`,
    changefreq: 'daily',
    priority: 0.8,
    lastmod: page.updated_at
  }));
}
```

### Mobile & Core Web Vitals
- **Mobile-first**: Next.js responsive design (TailwindCSS)
- **LCP** (Largest Contentful Paint): < 2.5s (Cloudflare CDN helps)
- **FID** (First Input Delay): < 100ms (static pages fast)
- **CLS** (Cumulative Layout Shift): < 0.1 (no late script injection)

## Link Building Strategy

### Internal Linking
- **Linking strategy**: 
  - Category pages → Related subcategories
  - Restaurant page → Other restaurants in same area
  - Visa page → Other visa types for same nationality
  - Company page → Companies in same sector

### External Links
- **Guest posting**: Dubai lifestyle blogs (1 link/month)
- **Directories**: Local business directories (free listing + link)
- **Social signals**: Encourage sharing on Facebook/LinkedIn
- **Partnerships**: Viator, Booking.com, PropertyFinder (logo + link)

## Content Updates Strategy
- **Monthly**: Refresh ratings/review counts (via scrapers)
- **Quarterly**: Update visa requirements (manual review)
- **Annually**: Full content audit (check if entities still exist)

## Monitoring SEO Performance

### Google Search Console
- **Submit sitemap**: Verify ownership
- **Monitor indexation**: Check coverage (should be 100% of pages)
- **Track keywords**: Target keywords (e.g., "best restaurants Dubai")
- **Fix issues**: Mobile usability, structured data errors

### Analytics Metrics
- **Traffic**: Sessions, users, session duration
- **Conversions**: Affiliate clicks, reservation links
- **Engagement**: Bounce rate (target < 40%), pages/session > 1.5
- **Rankings**: Track top 20 keywords (check Search Console)

### Monthly SEO Audit
```sql
-- Low-performing pages
SELECT slug, composite_score, page_views
FROM pages
WHERE page_views > 0 AND page_views < 10
ORDER BY updated_at DESC
LIMIT 20;

-- High-opportunity (high score, low traffic)
SELECT slug, composite_score, page_views
FROM pages
WHERE composite_score > 0.8 AND page_views < 50
ORDER BY composite_score DESC;
```

## Launch Checklist
- [ ] All pages include schema.org JSON-LD
- [ ] Canonical tags set correctly
- [ ] Mobile responsive design verified
- [ ] Core Web Vitals < thresholds (Google PageSpeed Insights)
- [ ] Sitemap generated and submitted to GSC
- [ ] robots.txt allows Googlebot
- [ ] 404 page created
- [ ] Internal links established
- [ ] Meta descriptions unique and persuasive
- [ ] Images optimized (WebP, lazy-loading)
