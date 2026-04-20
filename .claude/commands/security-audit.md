# /security-audit — Full Security Audit

When user types `/security-audit`, perform a comprehensive security scan of the entire codebase against the security rules in `.claude/rules/security.md`.

---

## Scan 1: Hardcoded Secrets

Search for any hardcoded API keys, passwords, tokens, or credentials:

```bash
grep -r "api_key\|password\|secret\|token" backend/app --include="*.py" | grep -v ".env\|config.py\|test"
```

**Flag any matches** that are:
- Hardcoded strings (not from environment variables)
- Not in comments or test fixtures
- Not variable names (e.g., `openai_api_key` parameter is OK, `openai_api_key = "sk-..."` is NOT)

---

## Scan 2: SQL Injection Risk

Find any raw string formatting in database queries (should use SQLAlchemy parameterized queries only):

```bash
grep -r "f\"SELECT\|f\"INSERT\|f\"UPDATE\|format.*SELECT\|\.query(" backend/app --include="*.py"
```

**Every match must be verified**:
- ❌ BAD: `f"SELECT * FROM venues WHERE slug = '{user_input}'"`
- ❌ BAD: `"SELECT ... {}".format(user_input)`
- ✅ GOOD: `select(Venue).where(Venue.slug == user_input)`

---

## Scan 3: Scraper Rate Limiting

Check every scraper file in `backend/app/scrapers/`:
- [ ] Has `asyncio.sleep()` or `time.sleep()` call (enforces rate limiting)
- [ ] Sets `User-Agent` header (rotates or uses realistic agent)
- [ ] Has error handling with retry logic (try/except blocks)
- [ ] Logs scrape job results (ScrapeJob record created)
- [ ] Respects `robots.txt` (if applicable)

**Flag any scraper missing these**:
```bash
for file in backend/app/scrapers/*.py; do
  echo "=== $(basename $file) ==="
  grep -E "sleep|User-Agent|except|ScrapeJob|robots" "$file" || echo "⚠️ Missing checks"
done
```

---

## Scan 4: API Security

Check every route in `backend/app/api/`:

**For admin/protected routes**:
- [ ] Has `Depends(get_current_user)` or similar auth dependency
- [ ] Returns 401 if not authenticated
- [ ] No hardcoded credentials in route handler

**For all routes**:
- [ ] Inputs validated with Pydantic (has `response_model`)
- [ ] No direct exception messages returned to client (returns generic "Internal error" for 500s)
- [ ] Error details logged with `logger.error(..., exc_info=True)`

**Grep for violations**:
```bash
grep -r "def.*POST\|def.*PUT\|def.*DELETE" backend/app/api --include="*.py" -A 3 | grep -v "Depends\|response_model"
```

---

## Scan 5: Environment Variables & Secrets

**Check `.env` file is properly ignored**:
```bash
git check-ignore .env CLAUDE.local.md .env.local
# Should output: .env, CLAUDE.local.md, .env.local (all ignored)
```

**Check no secrets in last commit**:
```bash
git log -p HEAD~5..HEAD | grep -E "password|api_key|secret_key|DATABASE_URL.*=" | head -5
# Should output: nothing
```

**Check configuration loads from environment**:
```bash
grep -r "Settings\|BaseSettings" backend/app --include="*.py" | grep "class Settings"
```

---

## Scan 6: Dependencies

Check for known vulnerabilities in dependencies:

**Backend**:
```bash
cd backend
pip-audit 2>/dev/null || pip install pip-audit && pip-audit
```

**Frontend**:
```bash
cd frontend
npm audit
```

Flag any:
- Critical vulnerabilities
- High vulnerabilities with available fixes
- Outdated dependency versions

---

## Scan 7: Logging Security

Check no secrets are logged:

```bash
grep -r "logger\|print" backend/app --include="*.py" | grep -E "password|api_key|DATABASE_URL|OPENAI_KEY|secret"
```

**Flag any matches** that log:
- Full request bodies (may contain passwords)
- API keys or tokens
- Database credentials
- Secret keys

---

## Output: Security Report

Format:

```
### Security Audit Report
**Date**: [timestamp]
**Scope**: Full codebase (backend + frontend)

### Critical Issues (fix immediately)
- [Issue 1]: [File], [Line]: [Description]
- [Issue 2]: ...

### High Issues (fix before next deploy)
- [Issue 1]: ...

### Medium Issues (should fix)
- [Issue 1]: ...

### Low / Informational (nice to have)
- [Issue 1]: ...

### Passed Checks
- [x] No hardcoded secrets found
- [x] All database queries use SQLAlchemy
- [x] All scrapers have rate limiting
- [x] All admin routes require auth
- [x] All inputs validated with Pydantic
- [x] .env properly ignored
- [x] No secrets in logs
- [x] Dependencies scanned (0 critical vulnerabilities)

### Overall Score: X/10 (10 = perfect)
```

---

## When to Run

Run `/security-audit`:
- Before every production deployment
- After adding any new scraper
- After adding new API endpoint
- After updating dependencies
- Periodically (monthly recommended)

---

**Last Updated**: 2026-04-20  
**Enforced by**: .claude/rules/security.md
