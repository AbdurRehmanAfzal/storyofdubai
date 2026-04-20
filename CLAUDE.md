# CLAUDE.md — Story of Dubai: Master Project Brain

## CRITICAL: Read this file completely at the start of every session

## Project Overview
**Product**: Dubai Programmatic SEO + Data Intelligence Platform  
**Domain**: storyofdubai.com  
**Goal**: Auto-generate 10,000+ SEO pages about Dubai (restaurants, properties, visas, companies, buildings) monetized via display ads (AdSense/Mediavine) and affiliate commissions (Viator, Booking.com, property portals)  
**Revenue model**: Fully passive — scraper → database → auto-generated pages → ads/affiliates  
**Owner**: Abdur Rehman Afzal, solo developer, Pakistan  
**Stage**: Initial build (Month 1)

## Architecture in One Paragraph
Python FastAPI backend serves data from PostgreSQL via REST API. Celery + Redis workers run scheduled scrapers (Playwright + httpx) that collect Dubai venues, properties, visa info, and company data. A scoring engine writes composite scores to the database. GPT-4o-mini enrichment generates unique 200-word page introductions per page and stores them in the database. Next.js frontend uses getStaticPaths + getStaticProps to build 10,000+ static pages from the database at build time. ISR (revalidate: 86400) auto-refreshes pages daily without full rebuilds. Cloudflare sits in front of everything for CDN and caching. VPS on Hostinger ($5/mo) hosts the FastAPI backend and Celery workers.

## Tech Stack (exact versions)
- Python 3.12
- FastAPI 0.115+
- SQLAlchemy 2.0 (async) + Alembic for migrations
- PostgreSQL 16
- Redis 7
- Celery 5.4
- Playwright 1.45+ (scraping JS-heavy sites)
- httpx 0.27 (scraping static sites)
- OpenAI Python SDK 1.40+ (GPT-4o-mini for enrichment)
- Next.js 14 (App Router + Pages Router hybrid — Pages Router for static generation)
- TypeScript 5
- TailwindCSS 3
- Node.js 20 LTS

## Key Business Rules Claude Must Never Violate
1. **NEVER delete scraped data** — only mark as is_active=False
2. **NEVER run scrapers without rate limiting** — min 2 second delay between requests
3. **NEVER hardcode API keys** — always use environment variables
4. **NEVER generate duplicate page content** — always check cosine similarity before saving AI content
5. **NEVER break the URL structure** once pages are indexed — changing slugs destroys SEO
6. **ALWAYS include schema.org JSON-LD** on every generated page
7. **ALWAYS update PROGRESS.md** when completing a major task
8. **The scoring engine output (composite_score) must be deterministic** — same inputs always produce same score

## Data Categories (what we scrape and what pages they generate)

| Data Source | What We Collect | Pages Generated | URL Pattern |
|---|---|---|---|
| Google Places API | Restaurants, hotels, attractions | ~1,200 per category | /[category]/[area]/ |
| Bayut.com | Property listings | ~2,400 | /apartments/[area]/[beds]/[price]/ |
| DLD (Dubai Land Dept) | Transaction data, rental yields | ~800 | /buildings/[name]/ |
| UAE govt portals | Visa types, requirements | ~600 | /visa-guide/[nationality]/[type]/ |
| DED / Freezone portals | Company/startup data | ~3,000 | /companies/[sector]/[name]/ |
| Viator / GetYourGuide | Experiences, tours | ~900 | /experiences/[category]/[area]/ |

## Environment Variables (see .env.example for all)
REQUIRED before any backend command:
- `DATABASE_URL` — PostgreSQL connection string
- `REDIS_URL` — Redis connection string
- `OPENAI_API_KEY` — for GPT-4o-mini enrichment
- `GOOGLE_PLACES_API_KEY` — for Places API
- `SECRET_KEY` — FastAPI JWT secret

## Current Sprint / What's In Progress
→ See PROGRESS.md for current task status

## How to Resume After Session Break
1. Read PROGRESS.md first — it tells you exactly where we stopped
2. Read this file (CLAUDE.md) fully
3. Run: `cd storyofdubai && git log --oneline -10` (see last commits)
4. Run: `git status` (see any uncommitted work)
5. Continue from PROGRESS.md "NEXT TASK" section

## Monetization Logic
- **Display ads**: Google AdSense (apply immediately) → Mediavine at 50k sessions/month
- **Affiliate links** are injected per page type:
  * Restaurant pages → TheFork/Zomato reservation links
  * Hotel pages → Booking.com affiliate (25-30% commission)
  * Experience pages → Viator affiliate (8% commission, avg order $120)
  * Property pages → Bayut/PropertyFinder referral ($50-200 per lead)
  * Visa pages → PRO service affiliate links

## Deployment Targets
- **Backend** (FastAPI + Celery): Hostinger VPS Ubuntu 22.04 (IP stored in CLAUDE.local.md)
- **Frontend** (Next.js): Vercel free tier
- **Database**: Supabase free tier (PostgreSQL) initially, migrate to VPS PostgreSQL at scale
- **Cache**: Redis on same VPS as backend
- **CDN**: Cloudflare free tier (always in front)

## Repository
- **GitHub**: https://github.com/abdurrehmanafzal/storyofdubai (create this)
- **Main branch**: main
- **Policy**: Never commit to main directly — always use feature branches
- **Branch naming**: feature/scraper-google-places, fix/scoring-algorithm, etc.

## Key File Locations
- **Project brain**: CLAUDE.md (this file) + CLAUDE.local.md (secrets, not in git)
- **Session state**: PROGRESS.md (updated at every major milestone)
- **Architecture rules**: .claude/rules/*.md
- **Custom commands**: .claude/commands/*.md
- **Domain knowledge**: .claude/knowledge/*.md

## Phase Roadmap
1. **Phase 0** (NOW): Project setup, DB schema, API scaffolding
2. **Phase 1**: Build scrapers (Google Places, static sites)
3. **Phase 2**: Scoring engine + data enrichment pipeline
4. **Phase 3**: Next.js frontend + static page generation
5. **Phase 4**: Monetization integration (AdSense, affiliate links)
6. **Phase 5**: Deploy to production (Hostinger + Vercel)
