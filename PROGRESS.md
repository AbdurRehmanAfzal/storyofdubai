# PROGRESS.md — Session State Tracker

**Last Updated**: 2026-04-20  
**Current Phase**: Phase 0 — Project Setup  

## Completed Tasks (Prompt 1 & 2)
- [x] Project folder structure created (27 directories)
- [x] CLAUDE.md written (5.6KB project brain)
- [x] Git initialized and configured
- [x] CLAUDE.local.md created with local machine config
- [x] .gitignore created (verified CLAUDE.local.md is excluded)
- [x] .env.example created with comprehensive documentation
- [x] README.md created
- [x] SSH setup folder created (~/.claude/ssh-setup/)
- [x] SSH key generated and added to GitHub
- [x] Code pushed to GitHub repository
- [x] All documentation committed

## IN PROGRESS
✓ Prompt 2 Complete: Local Config & Environment Setup
✓ Prompt 3 Complete: Code Style & Architecture Rules Documented
✓ Prompt 4 (Current): Command Documentation & Workflow Automation

## COMPLETED (Prompt 4)
- [x] Created .claude/commands/review.md (code review automation)
- [x] Created .claude/commands/fix-issue.md (issue fix workflow)
- [x] Created .claude/commands/deploy.md (VPS deployment procedure)
- [x] Created .claude/commands/INDEX.md (command reference)

## NEXT TASK
→ **Phase 1 Sprint 1**: Database Schema & API Scaffolding
  - Create Alembic migrations for core tables (venues, properties, visa_guides, companies, areas, categories, scrape_jobs, ai_enrichments)
  - Set up SQLAlchemy models with proper indexes and constraints
  - Create Pydantic schemas for request/response validation
  - Scaffold FastAPI endpoints for `/api/v1/`
  - Implement standard response envelope and error handling
  - Create health check endpoint
  - Write integration tests for all endpoints

## Blockers
None

## Key Decisions Made
- Using FastAPI (not Django) for lighter backend footprint
- Pages Router (not App Router) for Next.js for reliable getStaticPaths at 10k+ pages
- GPT-4o-mini (not GPT-4) for cost efficiency at scale
- Hostinger VPS ($5/mo) over AWS for cost efficiency
- SSH authentication (permanent, no tokens/passwords)
- Ed25519 SSH keys (modern, secure, smaller than RSA)
- Supabase free tier initially, migrate to self-hosted PostgreSQL at scale

## Architecture Decisions Log
| Date | Decision | Reason |
|------|----------|--------|
| 2026-04-20 | Pages Router over App Router | SSG at 10k+ pages more reliable in Pages Router |
| 2026-04-20 | Supabase free tier initially | Zero cost while building, migrate to self-hosted later |
| 2026-04-20 | GPT-4o-mini for enrichment | Good quality at $0.00015/1k input tokens, scales cost-effectively |
| 2026-04-20 | SSH over HTTPS tokens | Permanent, no expiration, industry standard |
| 2026-04-20 | Hostinger VPS | $5/mo cost, sufficient for 100k+ pages + traffic |

## Session Notes
- **Prompt 1**: Created complete project structure, CLAUDE.md brain, all documentation
- **Prompt 2**: Set up SSH (GitHub configured), pushed code to repository
  - Created comprehensive CLAUDE.local.md for local development
  - Updated .env.example with detailed environment variables
  - Created reusable SSH setup folder (~/.claude/ssh-setup/)
- **Prompt 3 (Partial)** — Rules Documentation:
  - Created .claude/rules/codestyle.md (Python/TypeScript conventions, git)
  - Created .claude/rules/architecture.md (Backend/Frontend patterns)
  - Updated backend/pyproject.toml (Black, isort, pytest config)
  - Created .claude/settings.json (Claude Code permissions)
  - Created .claude/settings.local.json (local SSH permissions)
  - Created .claude/rules/api-conventions.md (REST API standards, endpoints)
  - Updated .claude/rules/database.md (Alembic, indexes, naming)
  - Created .claude/rules/testing.md (pytest, fixtures, coverage 75% minimum)
  - Updated .claude/rules/security.md (secrets, auth, scraper rules)
  - **Total rules documentation: 2,400+ lines across 6 files**
