# /deploy — Deploy to VPS Command

When user types `/deploy [backend|frontend|all]`, execute full deployment workflow.

---

## Pre-Deploy Checklist (Run Every Time, No Exceptions)

Before ANY deployment, verify:

```
[ ] git status is clean: no uncommitted changes
[ ] All tests pass: cd backend && pytest tests/ -v
[ ] No secrets in last commit: git log -p HEAD~1..HEAD | grep -i "password\|api_key\|secret"
[ ] .env and CLAUDE.local.md not in commit: git show --name-only HEAD
[ ] PROGRESS.md updated with deployment note
[ ] VPS credentials available in CLAUDE.local.md
```

---

## Deploy Backend to VPS

### Prerequisites
- VPS IP and SSH credentials in CLAUDE.local.md
- SSH key configured: `~/.ssh/storyofdubai_rsa` or use default `~/.ssh/id_ed25519`
- Backend tests passing locally

### Deployment Steps

**1. Push code to GitHub (triggers CI/CD)**
```bash
git push origin main
```
Wait for GitHub Actions to pass (check Actions tab).

**2. SSH into VPS**
```bash
ssh -i ~/.ssh/storyofdubai_rsa deploy@[VPS_IP]
# Or if using default: ssh deploy@[VPS_IP]
```

**3. On VPS: Pull latest code**
```bash
cd /app/storyofdubai
git pull origin main
```

**4. On VPS: Run database migrations**
```bash
source venv/bin/activate
alembic upgrade head
# Check: alembic current
```

**5. On VPS: Install/update dependencies (if changed)**
```bash
pip install -r backend/requirements.txt
```

**6. On VPS: Restart API service**
```bash
sudo systemctl restart storyofdubai-api
# Check status: sudo systemctl status storyofdubai-api
```

**7. On VPS: Restart Celery worker (if scraper code changed)**
```bash
sudo systemctl restart storyofdubai-celery
# Check: sudo systemctl status storyofdubai-celery
```

**8. On VPS: Check logs**
```bash
tail -50 /var/log/storyofdubai/app.log
tail -50 /var/log/storyofdubai/celery.log
```

**9. Verify health endpoint**
```bash
curl https://api.storyofdubai.com/api/v1/health/
# Should return: {"status": "healthy", "database": "connected", ...}
```

### Post-Deploy (VPS)
- [ ] API responding: curl returns 200 with health status
- [ ] Database connected: check logs for connection errors
- [ ] Redis connected: check Celery can connect
- [ ] No recent errors in logs

---

## Deploy Frontend to Vercel

### Prerequisites
- Vercel CLI installed: `npm install -g vercel`
- Vercel project linked: `.vercel/project.json` exists
- Frontend builds locally: `npm run build`

### Deployment Steps

**1. Verify build works locally**
```bash
cd frontend
npm run build
npm run start  # Test production build
```

**2. Push to main branch (auto-deploys if configured)**
```bash
git push origin main
```

**3. Or manually deploy**
```bash
cd frontend
vercel --prod
```

**4. Check deployment**
- Visit: https://storyofdubai.vercel.app (or production domain)
- Check Vercel dashboard for build logs
- Verify page loads and API calls work

### Post-Deploy (Vercel)
- [ ] Homepage loads: https://storyofdubai.com
- [ ] Sample page loads: /restaurants/dubai-marina/nobu
- [ ] API calls working: check browser DevTools Network tab
- [ ] No build errors in Vercel dashboard

---

## Deploy Both (Backend + Frontend)

Run in this order:

```bash
# 1. Deploy backend first (it must be running for frontend to fetch data)
/deploy backend

# 2. Wait 5 minutes for VPS to stabilize

# 3. Deploy frontend
/deploy frontend

# 4. Test integration
curl https://storyofdubai.com/api/v1/health/
curl https://storyofdubai.com/restaurants/dubai-marina/
```

---

## Rollback Procedure (If Deployment Fails)

### Rollback Backend
```bash
ssh deploy@[VPS_IP]
cd /app/storyofdubai
git revert HEAD  # Reverts last commit
alembic downgrade -1  # Rollback last migration (if DB changed)
git push origin main
ssh deploy@[VPS_IP]
cd /app/storyofdubai && git pull origin main
alembic upgrade head
sudo systemctl restart storyofdubai-api
```

### Rollback Frontend
```bash
cd frontend
git revert HEAD
git push origin main
# Vercel auto-redeploys
# Or manually: vercel --prod --confirm
```

---

## Emergency Contacts

If deployment fails critically:

1. **Check VPS Status**: `ssh deploy@[VPS_IP] "systemctl status storyofdubai-api"`
2. **Check Logs**: `ssh deploy@[VPS_IP] "tail -100 /var/log/storyofdubai/app.log"`
3. **Database Down?**: `ssh deploy@[VPS_IP] "psql $DATABASE_URL -c 'SELECT 1'"`
4. **Redis Down?**: `ssh deploy@[VPS_IP] "redis-cli ping"`

---

## Monitoring Post-Deploy

After each deployment, monitor for 15 minutes:

```bash
# Terminal 1: Watch API logs
ssh deploy@[VPS_IP] "tail -f /var/log/storyofdubai/app.log"

# Terminal 2: Watch Celery logs
ssh deploy@[VPS_IP] "tail -f /var/log/storyofdubai/celery.log"

# Terminal 3: Monitor health (every 10 seconds)
while true; do
  curl -s https://api.storyofdubai.com/api/v1/health/ | jq .
  sleep 10
done
```

Look for:
- [ ] No error stack traces
- [ ] Database/Redis status "connected"
- [ ] Response times < 500ms
- [ ] No 500 or 502 errors

---

## Deployment Frequency & Strategy

**Backend**: Deploy after every feature/fix (Green = all tests pass)
**Frontend**: Deploy after contentious changes; usually auto-deploys via Vercel
**Database**: Migrations deployed with backend (run before restart)
**Secrets**: Never commit; always in VPS `/etc/storyofdubai/.env`

---

**Last Updated**: 2026-04-20  
**For**: Story of Dubai Deployments  
**Enforced by**: Pre-deploy checklist, automated CI/CD, health checks
