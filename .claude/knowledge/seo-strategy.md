# SEO Strategy & Page Optimization

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
