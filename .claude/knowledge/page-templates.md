# Page Templates & Content Structure

## Template 1: Restaurant Page
**File**: `frontend/pages/restaurants/[area]/[name].tsx`  
**Data**: Fetched from `/api/v1/restaurants/{id}`  
**URL Example**: `/restaurants/dubai-marina/nobu/`

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
