# Claude Code Commands — Story of Dubai

Quick reference for custom slash commands that automate common development workflows.

---

## Available Commands

### `/review [file|all]`
**Purpose**: Perform full code review against all rules files  
**When to use**: Before committing, to catch style/architecture/security issues  
**Checks**: codestyle.md, architecture.md, api-conventions.md, security.md, testing.md  
**Output**: Review report with score and actionable fixes

**Example**:
```
/review app/services/venue_service.py
/review all
```

See: [review.md](review.md)

---

### `/fix-issue [description|#number]`
**Purpose**: Fix a GitHub issue with full plan → implementation → verification workflow  
**When to use**: When you have a specific bug or feature to implement  
**Workflow**: 
1. Understand issue
2. Locate affected code
3. Show fix plan (ask approval)
4. Implement changes
5. Run tests & review
6. Commit & push

**Example**:
```
/fix-issue Scoring algorithm doesn't handle null ratings
/fix-issue #42
```

See: [fix-issue.md](fix-issue.md)

---

### `/deploy [backend|frontend|all]`
**Purpose**: Full deployment to VPS with pre-deploy checklist and post-deploy verification  
**When to use**: When ready to push code to production  
**Includes**:
- Pre-deploy checklist (tests, secrets, git status)
- Step-by-step VPS deployment
- Database migration execution
- Health check verification
- Rollback procedure

**Example**:
```
/deploy backend
/deploy frontend
/deploy all
```

See: [deploy.md](deploy.md)

---

## Future Commands (To Add)

These commands should be created in future sessions:

- `/test [file|all]` — Run pytest with coverage, show gaps
- `/lint` — Run Black, isort, ESLint, mypy
- `/scrape [data-source]` — Trigger scraper locally (Google Places, Bayut, etc.)
- `/db` — Database utilities (migrate, seed, backup, restore)
- `/logs [service]` — Tail VPS logs (API, Celery, nginx)
- `/monitor` — Real-time health monitoring (API, DB, Redis, Celery)
- `/serve` — Start all local services (backend, frontend, Redis, Celery)

---

## How Commands Work

Each command file in this directory follows a standard structure:

1. **Trigger**: `/command-name` (user types this)
2. **Description**: What the command does
3. **Prerequisites**: What must be true before running
4. **Steps**: Detailed workflow
5. **Examples**: Common usage patterns
6. **Troubleshooting**: Common issues & fixes

Commands are designed to:
- ✅ Enforce project standards (rules in .claude/rules/)
- ✅ Prevent common mistakes (security checks, tests required)
- ✅ Automate repetitive tasks (code generation, testing, deployment)
- ✅ Provide clear output for decision-making

---

## Using Commands in This Session

To invoke a command, type in your prompt:
```
/review app/api/v1/venues.py
```

Claude Code will:
1. Read the corresponding `.claude/commands/[command].md` file
2. Execute the workflow described
3. Return results and next steps

---

**Last Updated**: 2026-04-20  
**For**: Story of Dubai  
**Total Commands**: 3 (review, fix-issue, deploy)
