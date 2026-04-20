# Session Recovery Guide

**Use this when resuming work after a break.**

## Quick Recovery Checklist (5 minutes)

1. **Read these files in order**:
   - CLAUDE.md (project brain)
   - PROGRESS.md (last session state)
   - This file (recovery guide)

2. **Check git status**:
   ```bash
   cd /home/abdurrehmanafzal/Documents/storyofdubai
   git log --oneline -10     # Last 10 commits
   git status                # Any uncommitted changes
   git branch                # Current branch
   ```

3. **Check database connectivity**:
   ```bash
   # If backend is running, test API
   curl http://localhost:8000/api/v1/health
   
   # Or test database directly
   psql $DATABASE_URL -c "SELECT 1"
   ```

4. **Continue from PROGRESS.md**:
   - Read "NEXT TASK" section
   - Check "BLOCKERS" for any issues
   - Resume implementation

## Common Recovery Scenarios

### Scenario A: Session Ended Mid-Implementation
**Sign**: PROGRESS.md shows task as "IN PROGRESS"

```bash
# 1. Understand what was being worked on
grep -A 5 "IN PROGRESS" PROGRESS.md

# 2. Check git to see uncommitted changes
git status
git diff backend/  # See what changed

# 3. Decide: commit or discard?
# Option 1: Commit the partial work
git add -A
git commit -m "WIP: [task description]"

# Option 2: Discard and start fresh
git checkout -- .

# 4. Continue from next task
```

### Scenario B: Backend/Frontend Won't Start
**Sign**: Dependencies changed or config missing

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# If still fails, check logs:
tail -100 backend/logs/app.log

# Frontend
cd frontend
npm install  # Refresh node_modules
npm run dev

# If still fails, check:
cat frontend/package-lock.json | head -20  # Verify integrity
```

### Scenario C: Database Connection Error
**Sign**: "psycopg2.OperationalError: cannot connect"

```bash
# 1. Check if running Supabase or self-hosted
cat .env | grep DATABASE_URL

# 2. Verify credentials
# For Supabase: Log in to supabase.com, get connection string
# For local: psql -U postgres -c "\l"

# 3. Test connection
psql $DATABASE_URL -c "SELECT version();"

# 4. If migration needed
cd backend
alembic upgrade head

# 5. Restart backend
python -m uvicorn app.main:app --reload
```

### Scenario D: Redis Won't Connect
**Sign**: Celery tasks failing with "ConnectionError"

```bash
# Check if Redis running
redis-cli ping  # Should return "PONG"

# If not running, start it
redis-server

# Or on VPS (systemd)
sudo systemctl start redis-server
sudo systemctl status redis-server

# Test Celery
celery -A app.celery_app inspect active  # List active tasks
```

### Scenario E: Git Merge Conflicts
**Sign**: `git status` shows "both modified" or "both added"

```bash
# See conflicting files
git status

# Open each file and resolve (<<<, ===, >>>)
vim backend/app/models.py  # Fix conflicts

# Mark resolved
git add backend/app/models.py

# Commit
git commit -m "resolve: merge conflicts"

# Or abort if unsure
git merge --abort
```

## Recovery Decision Tree

```
┌─ Start recovery
│
├─ Read PROGRESS.md
│  ├─ Task IN_PROGRESS? → Scenario A (commit or discard)
│  ├─ Task pending?     → Continue from next task
│  └─ Task completed?   → Read "NEXT TASK" section
│
├─ git status shows conflicts?
│  └─ Yes → Scenario E (resolve conflicts)
│
├─ Start backend/frontend?
│  ├─ Fails to start? → Scenario B (reinstall dependencies)
│  └─ Runs OK?        → Continue
│
├─ Can connect to database?
│  ├─ No → Scenario C (check DB connection)
│  └─ Yes → Continue
│
├─ Can connect to Redis?
│  ├─ No → Scenario D (start Redis)
│  └─ Yes → Continue
│
└─ All systems running? → Resume from PROGRESS.md "NEXT TASK"
```

## Important Files Checklist
- [ ] CLAUDE.md exists (project brain)
- [ ] .env exists (never committed)
- [ ] CLAUDE.local.md exists (local secrets)
- [ ] PROGRESS.md updated (last session state)
- [ ] backend/requirements.txt up to date
- [ ] frontend/package.json up to date
- [ ] Git history clean (no merge conflicts)

## Variables to Remember
- **VPS IP**: Stored in CLAUDE.local.md (Hostinger)
- **Database URL**: Stored in .env (Supabase or self-hosted)
- **API Keys**: Stored in .env (OpenAI, Google Places, etc.)
- **Frontend API URL**: http://localhost:3000 (dev), https://api.storyofdubai.com (prod)

## Quick Command Reference
```bash
# Navigate to project
cd /home/abdurrehmanafzal/Documents/storyofdubai

# Check latest commits
git log --oneline -5

# See uncommitted changes
git diff

# Start backend (if not running)
cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload

# Start frontend (if not running)
cd frontend && npm install && npm run dev

# Run tests
cd backend && pytest -v

# Check database
psql $DATABASE_URL -c "SELECT COUNT(*) FROM restaurants;"

# Check Redis
redis-cli ping

# View logs
journalctl -u storyofdubai-api -f  # On VPS
tail -f backend/logs/app.log       # Locally
```

## Session Notes Template
After each session, update PROGRESS.md with:
- **Completed**: What you finished
- **In Progress**: What you started but didn't finish
- **Next Task**: What to do next session
- **Blockers**: Any issues that need solving
- **Key Decisions**: Any architectural decisions made

Example:
```markdown
## Session 2026-04-21
### Completed
- [x] Set up project structure
- [x] Created CLAUDE.md
- [x] Initialized git

### In Progress
- [ ] Creating database schema
  - Completed: pages, restaurants tables
  - Todo: ai_enrichments, scoring_results

### Next Task
→ Write Alembic migrations for all core tables

### Blockers
None

### Key Decisions
- Using Alembic for migrations (not raw SQL)
- Soft deletes only (is_active flag)
```

## Recovery Success = All Three Green
- ✅ Git clean (no uncommitted changes, no conflicts)
- ✅ Backend running (`curl http://localhost:8000/api/v1/health` → 200)
- ✅ Frontend running (`http://localhost:3000` loads)
- ✅ Database connected (`psql $DATABASE_URL -c "SELECT 1"` → returns 1)

Once all green, you're ready to continue. Open PROGRESS.md, read "NEXT TASK", and resume implementation.
