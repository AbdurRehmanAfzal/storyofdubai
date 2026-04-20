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
✓ Prompt 3 (Partial): Claude Code Settings & Permissions

## NEXT TASK
→ **Prompt 3 (Continued)**: Database Schema & API Scaffolding
  - Create Alembic migrations for core tables (pages, restaurants, properties, etc.)
  - Scaffold FastAPI endpoints for `/api/v1/`
  - Set up SQLAlchemy models and Pydantic schemas
  - Create health check endpoint

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
- Prompt 1: Created complete project structure, CLAUDE.md brain, all documentation
- Prompt 2: Set up SSH (GitHub configured), pushed code to repository
- Added comprehensive CLAUDE.local.md for local development (NOT committed)
- Updated .env.example with detailed environment variables and comments
- Created reusable SSH setup folder (~/.claude/ssh-setup/) for future projects
- Prompt 3 (Partial): Created .claude/settings.json (permissions for Claude Code)
  - Allow: git, python, pip, npm, pytest, alembic, celery, uvicorn, read/write
  - Deny: destructive commands (rm -rf, DROP TABLE, SSH from repo)
  - settings.local.json: SSH allowed only on local machine for VPS deployment
