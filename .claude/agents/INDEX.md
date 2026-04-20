# Claude Code Agents — Story of Dubai

Specialized agents that automate code review, security auditing, and domain-specific tasks.

---

## Available Agents

### Code Reviewer Agent
**File**: [code-reviewer.md](code-reviewer.md)  
**Spawned when**: User runs `/review`, or code changes affect backend/frontend  
**Specialization**: Architecture patterns, code quality, SEO impact (critical for programmatic SEO platform), performance, testing

**Review checklist covers**:
- Architecture (thin routes, fat services, Pydantic schemas, proper async)
- Code quality (type hints, error handling, logging, formatting)
- **SEO impact** (URL structure, getStaticPaths, meta tags, schema.org markup) ← unique to this project
- Performance (database indexes, N+1 queries, Redis caching, pagination)
- Security basics (hardcoded credentials, raw SQL, rate limiting)
- Testing (unit tests, integration tests, coverage)

**Output**: Verdict (PASS/NEEDS WORK/FAIL), categorized findings, line references, score out of 10

---

### Security Auditor Agent
**File**: [security-auditor.md](security-auditor.md)  
**Spawned when**: User runs `/security-audit`, or code changes affect scrapers/auth/API  
**Specialization**: Vulnerabilities specific to web scraping platforms

**Threat model covers**:
- Tier 1 (Critical): API key exposure, scraper DDoS, SQL injection, VPS compromise
- Tier 2 (High): Unauthorized scraper access, data exfiltration, dependency CVEs, weak CORS
- Tier 3 (Medium): Personal data scraping, IDOR, excessive error details

**Audit checks**:
1. Secret detection (hardcoded API keys, tokens, DB credentials)
2. Scraper safety (rate limiting, user-agent rotation, retry logic, robots.txt)
3. Input validation (Pydantic models, parameterized queries, pagination limits)
4. API authentication (protected endpoints, CORS configuration)
5. Data privacy (no personal data, no IDOR)
6. Infrastructure (VPS firewall, SSH config, dependency vulnerabilities)

**Output**: Security Audit Report with CVSS scores, categorized by severity (Critical/High/Medium/Low)

---

## Decision Tree: When to Spawn

```
Code change detected
├─ Touches backend/app/models/ → Code Reviewer
├─ Touches backend/app/services/ → Code Reviewer
├─ Touches backend/app/api/ → Code Reviewer + Security Auditor (if auth/input validation)
├─ Touches backend/app/scrapers/ → Code Reviewer + Security Auditor (rate limiting, secrets)
├─ Touches frontend/pages/ → Code Reviewer (SEO impact!)
├─ Touches frontend/components/ → Code Reviewer
├─ Touches app/config.py or .env handling → Security Auditor only
├─ Touches authentication → Security Auditor only
└─ Other infrastructure changes → Security Auditor

User runs /review → Code Reviewer
User runs /security-audit → Security Auditor
Before production deployment → Both agents (full review + full audit)
```

---

## Communication Between Agents

**Code Reviewer** → **Security Auditor**: "Found potential SQL injection, please verify"
- Code Reviewer flags the issue, Security Auditor provides deep analysis and historical context

**Security Auditor** → **Code Reviewer**: "Rate limiting missing in new scraper, blocks code review"
- Security Auditor blocks, Code Reviewer requires fix before approval

**Both agents** → User: "Code FAIL" or "Security FAIL" = cannot proceed
- Changes required, no exception

---

## Future Agents (To Add)

- **Performance Auditor**: Database query analysis, caching strategy, build time optimization
- **SEO Auditor**: Meta tags, schema.org, sitemap validity, canonical URLs, robots.txt
- **Infrastructure Agent**: VPS deployment, database management, monitoring, cost optimization
- **Testing Agent**: Test coverage gaps, mutation testing, test reliability
- **Documentation Agent**: Auto-update PROGRESS.md, detect missing docstrings, verify examples

---

## How Agents Are Used in This Session

1. **User requests code review**: `/review app/services/venue.py`
   - Code Reviewer Agent spawned
   - Returns structured review with verdict and line references

2. **User requests security audit**: `/security-audit`
   - Security Auditor Agent spawned
   - Returns threat assessment, issue categorization, remediation steps

3. **Code feature added by Claude Code**:
   - Code Reviewer + Security Auditor both spawned automatically
   - Both must approve before code is committed

4. **Before deployment**:
   - Both agents run full audit
   - Any Critical findings block deployment
   - High findings require documented mitigation

---

**Last Updated**: 2026-04-20  
**For**: Story of Dubai  
**Total Agents**: 2 (Code Reviewer, Security Auditor)
