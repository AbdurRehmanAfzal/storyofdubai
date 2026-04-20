# Security Rules

## API Security
- **Authentication**: JWT tokens required for all write endpoints
- **Token secret**: Stored in .env as SECRET_KEY, never hardcoded
- **HTTPS only**: All requests must use HTTPS in production
- **CORS**: Whitelist frontend domain only, no wildcard (*)
- **Rate limiting**: 1000 req/hour per IP globally

## Secrets Management
- **Never commit secrets**: .env in .gitignore, use .env.example as template
- **Environment-specific**: .env, .env.production, .env.staging
- **Rotate regularly**: API keys, database passwords every 90 days
- **Use .env.local for development**: Never push personal keys

## Database Security
- **Parameterized queries**: Always use ORM (SQLAlchemy), never f-strings in SQL
- **Connection pooling**: PostgreSQL with SSL connection string
- **Supabase RLS**: Enable Row Level Security for user-scoped data (future)
- **Backups**: Encrypted, stored separately from production

## Web Security Headers
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
```

## Scraper Security
- **Rate limiting**: Minimum 2 second delay between requests
- **User-Agent**: Rotate to avoid blocking (identified as StoryOfDubai/1.0)
- **Respect robots.txt**: Check before scraping
- **Session management**: Rotate IP monthly if using residential proxies
- **API keys in header**: Never in URL query parameters

## AI Enrichment Security
- **API keys**: Stored in .env, never logged
- **Prompt injection**: Never directly interpolate user input into prompts
- **Content filtering**: Flag and review suspicious AI outputs before publishing
- **Audit trail**: Log all AI enrichment calls (timestamp, tokens used, cost)

## Infrastructure Security
- **SSH**: Only key-based auth, no password login on VPS
- **Firewall**: Open only ports 22 (SSH), 80 (HTTP), 443 (HTTPS)
- **Sudo access**: Minimal (deploy user only, no password)
- **Security updates**: Weekly cron for apt update && apt upgrade

## Data Privacy
- **GDPR compliance**: Don't store personal data (emails, phone numbers of visitors)
- **Scraping consent**: Verify terms of service allow data collection
- **Data retention**: Delete backups after 7 days
- **User data**: Never sold or shared with third parties

## Incident Response
- **Breach detection**: Monitor logs for unusual activity
- **Response time**: 1 hour to investigate, 24 hours to notify if data exposed
- **Post-mortem**: Document what happened, why, and how to prevent it
- **Monitoring**: Sentry alerts for errors, Cloudflare DDoS protection enabled

## Secret Scanning
- **Pre-commit hook**: Detect secrets (API keys, passwords) before commit
- **Tool**: detect-secrets or gitleaks (optional but recommended)
- **GitHub secrets scanning**: Enabled on private repo

## Code Review Security Checklist
- [ ] No hardcoded passwords/keys
- [ ] Input validation on all API endpoints
- [ ] SQL injection prevented (ORM used)
- [ ] XSS prevention (Next.js escapes by default)
- [ ] CSRF tokens on state-changing endpoints (if applicable)
- [ ] Rate limiting configured
- [ ] Error messages don't leak sensitive info
