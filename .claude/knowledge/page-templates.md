# Page Template Knowledge

Complete specification of all page templates, data structures, and component library.

---

## Template 1: Venue Area Hub (`/[category]/[area]/`)

**File**: `frontend/pages/[category]/[area].tsx`  
**Data source**: `/api/v1/page-paths/[category]/[area]/?limit=20`  
**Example**: `/restaurants/dubai-marina/`

**Purpose**: Primary ranking page for each category × area combination. High commercial intent.

### Data Requirements

```typescript
interface VenueAreaHub {
  area: string              // "Dubai Marina"
  area_slug: string         // "dubai-marina"
  category: string          // "Restaurants"
  category_slug: string     // "restaurants"
  total_venues: number      // Total in this area+category
  venues: Venue[]           // Top 20 by composite_score
}

interface Venue {
  id: number
  name: string
  slug: string              // Unique per entity type
  rating: number            // 0-5
  review_count: number
  composite_score: number   // 0-100
  price_range: string       // "$", "$$", "$$$", "$$$$"
  cuisine_type: string      // For restaurants
  image_url: string
}
```

### Page Structure

```
H1: Best {Category} in {Area} Dubai
Subtitle: Top-rated {category} with ratings, reviews, and {CTA}

Quick Stats:
  - Total venues: {count}
  - Average rating: {avg}/5
  - Price range: {min}-{max}

Featured List (Top 5):
  1. Venue Name (4.8★, 1,240 reviews)
  2. Venue Name (4.7★, 890 reviews)
  ...

[Affiliate CTA Block]

Related Areas:
  - Link to nearby area hubs
  - 5 other areas in same emirate

Schema.org:
  - ItemList (venues)
  - BreadcrumbList
  - LocalBusiness (for featured venues)
```

### Meta Tags

```html
<title>Best {Category} in {Area}, Dubai | Story of Dubai</title>
<meta name="description" 
      content="Top-rated {category} in {area}. Ratings, reviews, price ranges, and {CTA}. Updated 2026." />
<link rel="canonical" href="https://storyofdubai.com/{category}/{area}/" />
```

### ISR Settings

```typescript
export async function getStaticProps({ params }) {
  return {
    props: { /* data */ },
    revalidate: 86400  // 24 hours
  }
}
```

---

## Template 2: Individual Venue (`/[category]/[area]/[venue-slug]/`)

**File**: `frontend/pages/[category]/[area]/[venue-slug].tsx`  
**Data source**: `/api/v1/venues/{slug}/`  
**Example**: `/restaurants/dubai-marina/nobu/`

**Purpose**: Individual listing page. Medium commercial intent, high CTR for branded searches.

### Data Requirements

```typescript
interface VenuePage {
  id: number
  name: string
  slug: string
  area: string
  area_slug: string
  category: string
  category_slug: string
  
  // Ratings & Reviews
  rating: number            // 0-5
  review_count: number
  composite_score: number   // 0-100
  score_breakdown: {
    rating_contribution: number
    recency_contribution: number
    review_count_contribution: number
  }
  
  // Business Details
  address: string
  phone: string
  website: string
  opening_hours: {
    monday: string          // "11:00 AM - 11:00 PM"
    // ... each day
  }
  
  // Category-specific (for restaurants)
  cuisine_type: string
  price_range: string
  dine_in: boolean
  delivery: boolean
  takeout: boolean
  
  // AI Enrichment
  ai_summary: string        // Unique 150-300 word intro
  highlights: string[]      // ["Michelin-starred", "Romantic ambiance"]
  
  // Images
  image_url: string         // Primary image
  images: string[]          // Gallery
  
  // Affiliate
  reservation_url: string   // Booking affiliate link
  
  // Related
  nearby_venues: Venue[]    // 3-5 similar venues in same area
}
```

### Page Structure

```
Breadcrumb: Home > {Category} > {Area} > {Venue}

H1: {Name} — {Cuisine Type} in {Area}, Dubai

[Hero Image]

Score Badge: {Composite Score}/100
"Excellent - 4.8★ based on 1,240 reviews"

Quick Facts (2-column):
  Rating: 4.8/5 (1,240 reviews)
  Cuisine: Japanese, Fusion
  Area: Dubai Marina
  Price Range: $$$
  Phone: +971 4 777 6777
  Website: noburestaurants.com
  Hours: 6:00 PM - 11:00 PM

[Affiliate CTA: Book a Table]

AI-Generated Introduction (150-300 words)
"Dubai Marina is home to some of the city's finest dining establishments..."

Sections:
  - About This Restaurant
  - Location & Hours
  - Amenities (Dine-in, Delivery, Takeout)
  - Highlights
  - Nearby Restaurants (Internal Links)

[JSON-LD Schema]
```

### Meta Tags

```html
<title>{Name} | {Cuisine} in {Area}, Dubai | Story of Dubai</title>
<meta name="description" 
      content="{Name}: {cuisine} restaurant in {area}. {rating}★ ({review_count} reviews). {address}. Book online." />
<link rel="canonical" href="https://storyofdubai.com/{category}/{area}/{slug}/" />
```

---

## Template 3: Property Filter (`/apartments/[area]/[bedrooms]-bedroom/[price-bucket]/`)

**File**: `frontend/pages/apartments/[area]/[bedrooms]-bedroom/[price-bucket].tsx`  
**Data source**: `/api/v1/properties/?area={area}&bedrooms={bedrooms}&price_min={min}&price_max={max}`  
**Example**: `/apartments/downtown-dubai/2-bedroom/100k-200k/`

**Purpose**: High commercial intent. Best for property affiliate links (Bayut, PropertyFinder).

### Data Requirements

```typescript
interface PropertyFilterPage {
  area: string
  area_slug: string
  bedrooms: number
  price_bucket: string          // "under-50k", "50k-100k", etc.
  price_min_aed: number
  price_max_aed: number
  total_properties: number
  properties: Property[]         // Top 20 by composite_score
}

interface Property {
  id: number
  title: string
  slug: string
  bedrooms: number
  bathrooms: number
  area_sqft: number
  price_aed: number
  price_currency: string        // "AED"
  price_type: string            // "rent" or "sale"
  property_type: string         // "apartment", "villa", "townhouse"
  area: string
  address: string
  image_url: string
  composite_score: number
}
```

### Page Structure

```
H1: {Bedrooms}-Bedroom Apartments for Rent in {Area}, Dubai

Filter Summary:
  Area: {Area}
  Bedrooms: {Bedrooms}
  Price Range: AED {min}—{max}/year

Results: {total} apartments found, sorted by score

List (Top 20):
  1. {Title} - AED {price} | {sqft} sqft | {rating}★
  2. {Title} - AED {price} | {sqft} sqft | {rating}★
  ...

Affiliate CTA:
  "Find more on Bayut.com →"
  "View on PropertyFinder →"

Sections:
  - Price Analysis
  - Popular Buildings
  - Area Guide
```

### ISR Settings

```typescript
revalidate: 43200  // 12 hours (prices change faster)
```

---

## Template 4: Visa Guide (`/visa-guide/[nationality]/[visa-type]/`)

**File**: `frontend/pages/visa-guide/[nationality]/[visa-type].tsx`  
**Data source**: `/api/v1/visa-guides/{nationality}/{visa-type}/`  
**Example**: `/visa-guide/united-states/visit-visa/`

**Purpose**: Informational. Highest RPM for Google Ads (legal/finance category). Good for visa consultant affiliates.

### Data Requirements

```typescript
interface VisaGuidePage {
  nationality: string           // "United States"
  nationality_slug: string      // "united-states"
  visa_type: string             // "Visit Visa"
  visa_type_slug: string        // "visit-visa"
  
  // Key Info
  eligibility: boolean
  processing_time: string       // "7-14 days"
  validity: string              // "30 days"
  cost_aed: number
  
  // Details
  overview: string              // Full description
  requirements: string[]        // List of requirements
  documents: {
    name: string
    description: string
  }[]
  faq: {
    question: string
    answer: string
  }[]
  
  // AI Enrichment
  ai_summary: string           // HowTo-style guide
  
  // Affiliate
  apply_url: string            // Government portal or consultant link
}
```

### Page Structure

```
H1: {Nationality} {Visa Type} for UAE — Requirements & Process

Quick Summary Box:
  Processing Time: 7-14 days
  Validity: 30 days
  Cost: AED 100
  Eligibility: ✓ Eligible for {nationality} nationals

Table of Contents
  1. Overview
  2. Eligibility
  3. Required Documents
  4. Application Process
  5. FAQs

Sections:

1. Overview
   {AI-generated 300-word intro about visa and process}

2. Eligibility
   - Who is eligible?
   - Who is NOT eligible?

3. Required Documents
   Checklist:
   ☐ Valid Passport
   ☐ Return Ticket
   ☐ Proof of Accommodation
   ☐ Bank Statement

4. Step-by-Step Application
   Step 1: ...
   Step 2: ...
   (Schema.org: HowToStep)

5. FAQs
   Q: How long does processing take?
   A: ...
   (Schema.org: FAQPage)

[CTA: Apply Now / Get Visa Consultant Help]
```

### Schema.org

```json
{
  "@type": "HowTo",
  "name": "{Nationality} {VisaType} for UAE",
  "step": [...]
}
```

### ISR Settings

```typescript
revalidate: 604800  // 7 days (rules change slowly)
```

---

## Template 5: Building Profile (`/buildings/[building-slug]/`)

**File**: `frontend/pages/buildings/[building-slug].tsx`  
**Data source**: `/api/v1/buildings/{slug}/`  
**Example**: `/buildings/burj-khalifa/`

### Page Structure

```
H1: {Building Name} — Dubai

Key Stats:
  Height: {height} meters
  Completed: {year}
  Developer: {developer}
  Location: {area}

Image Gallery

Overview

Notable Features

Nearby Amenities:
  - Restaurants
  - Shopping
  - Parks

Related Buildings

Related Properties (affiliate links)
```

---

## Component Library

### VenueCard
Shows venue with score badge, key stats, affiliate link
```typescript
<VenueCard 
  name="Nobu"
  rating={4.8}
  composite_score={92}
  area="Dubai Marina"
  image={url}
  href="/restaurants/dubai-marina/nobu/"
/>
```

### ScoreBadge
Displays 0-100 score with color coding
```typescript
<ScoreBadge score={92} />  // Green
<ScoreBadge score={65} />  // Yellow
<ScoreBadge score={40} />  // Red
```

### AffiliateCTA
Context-aware call-to-action
```typescript
<AffiliateCTA 
  type="restaurant"
  affiliate_link="..."
  cta_text="Book a Table"
/>
```

### BreadcrumbNav
Structured breadcrumb + schema.org
```typescript
<BreadcrumbNav items={[
  { label: "Home", href: "/" },
  { label: "Restaurants", href: "/restaurants/" },
  { label: "Dubai Marina", href: "/restaurants/dubai-marina/" },
  { label: "Nobu", href: "/restaurants/dubai-marina/nobu/" }
]} />
```

### RelatedPages
Auto-fetches and renders internal links
```typescript
<RelatedPages 
  entity_id={venue_id}
  entity_type="venue"
  limit={5}
/>
```

---

## Performance Targets

| Page Type | Build Time | Load Time | Lighthouse |
|-----------|-----------|-----------|-----------|
| Area Hub | 30-60s per 100 pages | <1s | >85 |
| Individual Venue | 10-20s per 100 pages | <800ms | >90 |
| Property Filter | 15-30s per 100 pages | <1s | >85 |
| Visa Guide | 5-10s per 50 pages | <600ms | >95 |

Total 10k page build: ~20-30 minutes on Vercel

### Data Structure
```typescript
interface RestaurantPage {
  id: number;
  name: string;
  area: string;
  address: string;
  phone: string;
  website: string;
  cuisine_type: string;
  rating: number;  // 0-5
  review_count: number;
  google_places_id: string;
  image_url: string;
  composite_score: number;
  ai_enrichment: {
    content: string;  // 200-word intro
    similarity_score: number;
  };
  highlights: string[];  // e.g., ["Romantic ambiance", "Michelin-starred"]
}
```

### Layout
```
┌─────────────────────────────────────┐
│ Breadcrumb: Home > Restaurants > Marina > Nobu
│
│ H1: Nobu — Japanese Fine Dining in Dubai Marina
│
│ [Hero Image]
│
│ Quick Facts (Sidebar):
│ Rating: 4.8/5 (1,240 reviews)
│ Cuisine: Japanese, Fusion
│ Area: Dubai Marina
│ Price: $$$
│
│ Introduction (AI-generated, 200 words)
│
│ [Booking Widget / Affiliate Link]
│
│ Key Sections:
│ - About
│ - Location & Hours
│ - Reservations
│ - Reviews Highlights
│ - Similar Restaurants
│
│ [JSON-LD Schema]
└─────────────────────────────────────┘
```

### Component Structure
```typescript
// pages/restaurants/[area]/[name].tsx
export default function RestaurantPage({ restaurant }) {
  return (
    <>
      <Breadcrumb items={[...]} />
      <RestaurantHero image={restaurant.image_url} />
      <div className="container mx-auto">
        <h1>{restaurant.name} — {restaurant.cuisine_type} in {restaurant.area}</h1>
        <QuickFacts restaurant={restaurant} />
        <AIIntro content={restaurant.ai_enrichment.content} />
        <BookingWidget affiliateLink={restaurant.booking_link} />
        <AboutSection restaurant={restaurant} />
        <LocationSection restaurant={restaurant} />
        <ReviewsSection reviews={restaurant.reviews} />
        <RelatedRestaurants area={restaurant.area} />
      </div>
      <JsonLdSchema entity={restaurant} />
    </>
  );
}
```

## Template 2: Property Page
**File**: `frontend/pages/apartments/[area]/[bedroom]/[property].tsx`  
**Data**: Fetched from `/api/v1/properties/{id}`  
**URL Example**: `/apartments/dubai-marina/2-bedroom/marina-sky-tower/`

### Data Structure
```typescript
interface PropertyPage {
  id: number;
  title: string;
  property_type: string;  // 'apartment', 'villa', 'townhouse'
  bedrooms: number;
  bathrooms: number;
  area_sqft: number;
  price_aed: number;
  price_usd: number;
  price_type: string;  // 'sale' or 'rent'
  area: string;
  address: string;
  amenities: string[];  // ['Pool', 'Gym', 'Parking']
  description: string;
  agent_name: string;
  agent_phone: string;
  photos: string[];
  composite_score: number;
  rental_yield_pct: number;  // If DLD data available
}
```

### Layout
```
┌─────────────────────────────────────┐
│ Breadcrumb: Home > Apartments > Marina > 2BR
│
│ H1: 2-Bedroom Apartment in Marina Sky Tower
│
│ [Photo Gallery - Main + thumbnails]
│
│ Quick Info (Sidebar):
│ AED 2.5M / $680k
│ 2 Bed | 2 Bath | 1,200 sqft
│
│ AI Introduction (200 words)
│
│ [Contact Agent Button]
│
│ Key Sections:
│ - Overview
│ - Amenities
│ - Location Map
│ - Price History / Rental Yield
│ - Similar Properties
│ - Neighborhood Guide
│
│ [JSON-LD Schema]
└─────────────────────────────────────┘
```

## Template 3: Visa Guide Page
**File**: `frontend/pages/visa-guide/[nationality]/[visa-type].tsx`  
**Data**: Fetched from `/api/v1/visa-guides/{id}`  
**URL Example**: `/visa-guide/indian-nationals/dubai-work-visa/`

### Data Structure
```typescript
interface VisaGuidePage {
  id: number;
  nationality: string;
  visa_type: string;  // 'work', 'visit', 'residence', 'student'
  title: string;
  requirements: string[];
  documents_needed: string[];
  processing_time: string;  // e.g., "7-14 days"
  validity_period: string;
  renewal_process: string;
  cost_aed: number;
  is_eligible: boolean;
  additional_notes: string;
  last_updated: Date;
}
```

### Layout
```
┌─────────────────────────────────────┐
│ H1: Dubai Work Visa for Indian Nationals
│
│ Quick Summary Box:
│ Processing Time: 7-14 days
│ Validity: 3 years
│ Cost: AED 500
│ Eligibility: Yes for Indian nationals
│
│ Table of Contents
│ 1. Overview
│ 2. Eligibility
│ 3. Required Documents
│ 4. Application Process
│ 5. FAQs
│
│ Sections:
│ - Detailed Overview
│ - Step-by-Step Application
│ - Document Checklist
│ - Common FAQs
│ - How to Apply (CTA)
│
│ [JSON-LD Breadcrumb + FAQ Schema]
└─────────────────────────────────────┘
```

## Template 4: Company Directory Page
**File**: `frontend/pages/companies/[sector]/[company].tsx`  
**Data**: Fetched from `/api/v1/companies/{id}`  
**URL Example**: `/companies/fintech/flywire/`

### Data Structure
```typescript
interface CompanyPage {
  id: number;
  name: string;
  sector: string;
  sub_sector: string;
  description: string;
  founded_year: number;
  headquarters: string;
  website: string;
  phone: string;
  employees: number;
  funding_aed: number;
  funding_stage: string;  // 'seed', 'series-a', 'public'
  linkedin_url: string;
  recent_news: string[];
}
```

## Template 5: Experience/Activity Page
**File**: `frontend/pages/experiences/[category]/[experience].tsx`  
**Data**: Fetched from `/api/v1/experiences/{id}`  
**URL Example**: `/experiences/desert-safari/dune-bashing-with-dinner/`

### Data Structure
```typescript
interface ExperiencePage {
  id: number;
  title: string;
  category: string;  // 'adventure', 'cultural', 'shopping', 'family'
  description: string;
  price_usd: number;
  duration_hours: number;
  includes: string[];
  age_restriction: string;
  difficulty_level: string;
  rating: number;
  review_count: number;
  operator: string;  // Viator, GetYourGuide, etc.
  booking_url: string;  // Affiliate link
}
```

## Shared Components
All templates use these:

### JsonLdSchema Component
```typescript
// components/JsonLdSchema.tsx
export default function JsonLdSchema({ entity, type }) {
  const schema = {
    '@context': 'https://schema.org',
    '@type': type === 'restaurant' ? 'LocalBusiness' : 'Thing',
    name: entity.name,
    description: entity.ai_enrichment?.content || entity.description,
    url: entity.url,
    image: entity.image_url,
    // ... more fields per entity type
  };
  
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
  );
}
```

### RelatedItems Component
```typescript
// components/RelatedItems.tsx
export default function RelatedItems({ items, type }) {
  return (
    <section className="py-8">
      <h2>Related {type}</h2>
      <div className="grid grid-cols-3 gap-4">
        {items.map(item => (
          <Card key={item.id} item={item} type={type} />
        ))}
      </div>
    </section>
  );
}
```

### BookingWidget Component
```typescript
// components/BookingWidget.tsx
export default function BookingWidget({ affiliate_link, cta_text }) {
  return (
    <div className="bg-blue-100 p-6 rounded-lg">
      <a 
        href={affiliate_link}
        target="_blank"
        rel="noopener noreferrer"
        className="btn-primary"
      >
        {cta_text}
      </a>
    </div>
  );
}
```

## Static Generation Performance

### getStaticProps Pattern
```typescript
export async function getStaticProps({ params }) {
  const entity = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/${params.type}/${params.id}`
  );
  
  return {
    props: { entity },
    revalidate: 86400  // Revalidate daily
  };
}
```

### Expected Performance
- **Build time**: ~2-3 hours for 10,000 pages on Vercel
- **Page load**: < 1 second (static HTML)
- **ISR revalidation**: 30-60 seconds per page
- **CDN cache**: 24 hours (Cloudflare)
