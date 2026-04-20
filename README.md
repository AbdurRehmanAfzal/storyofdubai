# Story of Dubai — Programmatic SEO Platform

Auto-generate 10,000+ SEO pages about Dubai businesses, properties, visas, and experiences. Monetized via Google AdSense and affiliate commissions.

## Project Status
**Phase**: 0 - Initial Setup  
**Start Date**: 2026-04-20  
**Owner**: Abdur Rehman Afzal

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20 LTS
- PostgreSQL 16
- Redis 7
- Git

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example ../.env
# Edit .env with your credentials
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` (frontend) and `http://localhost:8000/api/v1/docs` (API docs).

## Architecture

```
storyofdubai/
├── backend/        # FastAPI + SQLAlchemy + Celery
├── frontend/       # Next.js 14 + static generation
├── infrastructure/ # Docker, nginx, deployment scripts
├── .claude/        # Claude Code configuration & knowledge base
└── docs/           # Architecture & deployment guides
```

## Key Features
- **Automated Scraping**: Playwright + httpx for dynamic & static sites
- **Data Scoring**: Composite scoring engine for relevance ranking
- **AI Enrichment**: GPT-4o-mini generates unique page intros
- **Static Generation**: Next.js getStaticPaths for 10k+ SEO-optimized pages
- **ISR**: Incremental Static Regeneration (daily refresh)
- **Monetization**: AdSense + affiliate links (Viator, Booking.com, Bayut)

## Data Categories
- **Restaurants & Cafes**: ~1,200 pages
- **Hotels & Accommodation**: ~800 pages
- **Properties**: ~2,400 pages
- **Visa & Immigration**: ~600 pages
- **Companies & Startups**: ~3,000 pages
- **Experiences & Tours**: ~900 pages

## Development Workflow
1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and test locally
3. Update PROGRESS.md with status
4. Commit with descriptive message
5. Push and create a pull request

## Environment
- **Development Database**: Supabase free tier
- **Development Cache**: Redis (localhost:6379)
- **Staging/Production**: Hostinger VPS
- **Frontend Hosting**: Vercel

## Documentation
- **CLAUDE.md** — Project brain & business rules (required reading)
- **PROGRESS.md** — Session state tracker
- **docs/** — Architecture, API, deployment guides

## Key Business Rules
⚠️ **CRITICAL — Never violate these:**
- Never delete scraped data (mark is_active=False instead)
- Never scrape without 2+ second rate limiting
- Never hardcode API keys
- Never break URL structure (destroys SEO)
- Always include JSON-LD schema.org markup
- Scoring output must be deterministic

## Getting Help
- Read `CLAUDE.md` for the complete project brain
- Run `claude /help` for Claude Code commands
- Check `docs/` for architecture guides

## License
Private project — not open source
