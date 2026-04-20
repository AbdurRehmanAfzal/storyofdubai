# Code Style Rules

## Python (Backend)
- **Formatter**: Black (line length 100)
- **Linter**: ruff
- **Type hints**: Required on all function signatures (Pydantic models count)
- **Async first**: Use `async def` for FastAPI endpoints
- **No abbreviations**: `user_id` not `uid`, `restaurant_rating` not `rat`
- **Docstrings**: Only on public APIs and complex functions (Google style)
- **Imports**: Organized as (stdlib, third-party, local) with blank lines between

## TypeScript/JavaScript (Frontend)
- **Framework**: Next.js 14 with TypeScript strict mode
- **Styling**: TailwindCSS + CSS modules (no inline styles)
- **Components**: Functional, named exports, one component per file
- **State**: React hooks (useState, useEffect), no class components
- **API calls**: Use `fetch` with proper error handling, wrap in `lib/` utilities
- **File naming**: kebab-case for files (button-group.tsx, not ButtonGroup.tsx)

## SQL & Database
- **Naming**: snake_case for tables/columns
- **Migrations**: Alembic, auto-generated when possible
- **Comments**: On tables with complex purpose, not on obvious columns
- **Constraints**: NOT NULL, UNIQUE, FOREIGN KEY on creation, not added later

## Git Commits
- **Format**: Conventional Commits (feat:, fix:, refactor:, docs:, test:, chore:)
- **Scope**: backend, frontend, docs, infra (e.g., `feat(backend): add user enrichment`)
- **Message**: Present tense, lowercase, max 50 chars for subject
- **Related task**: If from PROGRESS.md, reference task ID in body
