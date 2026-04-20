# /review — Full Code Review Command

When user types `/review [file or "all"]`, perform this complete review:

## Step 1: Read context
- Read CLAUDE.md and the file(s) to review
- If "all", review all files changed in the last commit: `git diff HEAD~1 --name-only`

## Step 2: Check against all rules files
- **codestyle.md** — Flag any violations (formatting, naming, imports, type hints)
- **architecture.md** — Flag structural issues (routes vs services, ORM patterns, dependency injection)
- **api-conventions.md** — Flag if API file (response envelope, pagination, status codes, authentication)
- **security.md** — ALWAYS check this (hardcoded credentials, input validation, SQL injection, secrets in logs)
- **testing.md** — Are tests present for new logic? Coverage targets met?

## Step 3: Output review report

```
### Review Report: [filename]

**Critical Issues** (must fix before commit):
- [Issue 1]: [explanation]
- [Issue 2]: [explanation]

**Warnings** (should fix):
- [Warning 1]: [explanation]
- [Warning 2]: [explanation]

**Suggestions** (optional improvements):
- [Suggestion 1]: [explanation]

**Security Flags**:
- [Any security concerns found]

**Missing Tests**:
- [What needs to be tested]

**Overall Score**: X/10
```

## Step 4: Ask for action

Ask: "Do you want me to fix all Critical issues now?"

If yes, proceed to fix them automatically and re-run /review.

---

## Example Usage

```
/review app/services/venue_service.py
/review all
/review backend/app/api/v1/venues.py
```

---

**Last Updated**: 2026-04-20
