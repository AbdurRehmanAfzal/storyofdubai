# Deployment & DevOps Guide

## Environments
| Environment | Backend | Frontend | Database | Cache | Domain |
|---|---|---|---|---|---|
| **Development** | localhost:8000 | localhost:3000 | Supabase free | Redis local | — |
| **Staging** | Hostinger VPS | Vercel preview | Supabase free | Redis on VPS | staging.storyofdubai.com |
| **Production** | Hostinger VPS | Vercel | Supabase paid / RDS | Redis on VPS | storyofdubai.com |

## Backend Deployment (FastAPI on Hostinger VPS)

### Prerequisites
- Hostinger VPS (Ubuntu 22.04, $5/month)
- SSH access configured (key in ~/.ssh/storyofdubai_rsa)
- Domain pointing to VPS IP (A record)

### Initial VPS Setup (First Time)
```bash
# SSH into VPS
ssh -i ~/.ssh/storyofdubai_rsa root@[VPS_IP]

# Update system
apt update && apt upgrade -y
apt install -y python3.12 python3.12-venv python3-pip
apt install -y postgresql postgresql-contrib redis-server nginx git

# Create deploy user
useradd -m -s /bin/bash deploy
usermod -aG sudo deploy
# Copy SSH key for deploy user

# Create app directory
mkdir -p /app/storyofdubai
chown -R deploy:deploy /app
```

### Deployment Process
```bash
# On local machine
git push origin main

# On VPS (via deploy user)
ssh -i ~/.ssh/storyofdubai_rsa deploy@[VPS_IP]

# Pull latest code
cd /app/storyofdubai
git pull origin main

# Install dependencies
python3.12 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Run migrations
cd backend
alembic upgrade head

# Restart services
sudo systemctl restart storyofdubai-api
sudo systemctl restart storyofdubai-celery
```

### Systemd Service Files

**File**: `/etc/systemd/system/storyofdubai-api.service`
```ini
[Unit]
Description=Story of Dubai FastAPI Backend
After=network.target

[Service]
User=deploy
WorkingDirectory=/app/storyofdubai
Environment="PATH=/app/storyofdubai/venv/bin"
ExecStart=/app/storyofdubai/venv/bin/uvicorn \
  backend.app.main:app \
  --host 127.0.0.1 \
  --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**File**: `/etc/systemd/system/storyofdubai-celery.service`
```ini
[Unit]
Description=Story of Dubai Celery Worker
After=network.target redis-server.service

[Service]
User=deploy
WorkingDirectory=/app/storyofdubai
Environment="PATH=/app/storyofdubai/venv/bin"
ExecStart=/app/storyofdubai/venv/bin/celery \
  -A backend.app.celery_app \
  worker \
  --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target
```

### Nginx Configuration
**File**: `/etc/nginx/sites-available/storyofdubai`
```nginx
upstream storyofdubai_api {
  server 127.0.0.1:8000;
}

server {
  listen 80;
  server_name api.storyofdubai.com;
  
  # Redirect HTTP to HTTPS
  return 301 https://$server_name$request_uri;
}

server {
  listen 443 ssl http2;
  server_name api.storyofdubai.com;
  
  # SSL certificates (Let's Encrypt via certbot)
  ssl_certificate /etc/letsencrypt/live/api.storyofdubai.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/api.storyofdubai.com/privkey.pem;
  ssl_protocols TLSv1.2 TLSv1.3;
  
  # Gzip compression
  gzip on;
  gzip_types text/plain application/json;
  
  # Proxy to FastAPI
  location / {
    proxy_pass http://storyofdubai_api;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # WebSocket support (if needed for real-time)
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
  }
  
  # Rate limiting
  limit_req_zone $binary_remote_addr zone=api:10m rate=100r/s;
  limit_req zone=api burst=200 nodelay;
}
```

### SSL Certificate Setup
```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate (for api.storyofdubai.com)
sudo certbot certonly --nginx -d api.storyofdubai.com

# Auto-renewal (cron)
sudo certbot renew --quiet (runs daily via systemd timer)
```

## Frontend Deployment (Next.js on Vercel)

### Initial Setup
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy (first time)
cd frontend
vercel --prod

# It will:
# 1. Authenticate with Vercel
# 2. Create project
# 3. Build and deploy
# 4. Create DNS records (if using Vercel DNS)
```

### Environment Variables in Vercel
Go to **Project Settings → Environment Variables**
```
NEXT_PUBLIC_API_URL=https://api.storyofdubai.com/api/v1
```

### Vercel Deployment Configuration
**File**: `vercel.json` (optional, in root)
```json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/.next",
  "framework": "nextjs",
  "env": {
    "NEXT_PUBLIC_API_URL": "@next_public_api_url"
  }
}
```

### Continuous Deployment
- **Trigger**: Every push to `main` branch
- **Status**: Check Vercel dashboard or GitHub status
- **Rollback**: Click "Promote to Production" on previous deployment

## Database Deployment

### Supabase Free Tier (Initial)
1. Sign up at https://supabase.com
2. Create project (Region: Europe, 3-5 second latency from Dubai)
3. Get connection string: `postgresql://postgres:password@db.xxx.supabase.co:5432/postgres`
4. Store in `.env` and `CLAUDE.local.md`
5. Run migrations: `alembic upgrade head`

### Migration to Self-Hosted PostgreSQL
**When**: Usage exceeds Supabase limits (10GB storage, 500 connections)

```bash
# 1. Dump Supabase database
pg_dump -h db.supabase.co -U postgres -d postgres > dump.sql

# 2. Import to VPS PostgreSQL
psql -h localhost -U postgres < dump.sql

# 3. Update DATABASE_URL in .env on VPS
# DATABASE_URL=postgresql://user:password@localhost:5432/storyofdubai

# 4. Restart FastAPI
sudo systemctl restart storyofdubai-api
```

### Database Backup Strategy
```bash
# Daily backup script
#!/bin/bash
# /app/scripts/backup-db.sh
BACKUP_DIR=/backups/postgresql
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

pg_dump -h localhost -U postgres storyofdubai > \
  $BACKUP_DIR/storyofdubai_$TIMESTAMP.sql

# Keep only last 7 days
find $BACKUP_DIR -mtime +7 -delete

# Install cron job
# 0 2 * * * /app/scripts/backup-db.sh
```

## Monitoring & Logging

### Application Monitoring
- **Tool**: Sentry (free tier)
- **Setup**: Add `sentry-sdk` to backend requirements
- **Config**: Set `SENTRY_DSN` in `.env`
- **Alerts**: Get Slack notifications on critical errors

### Log Aggregation
- **Tool**: Cloudflare Logpush (free with Cloudflare)
- **Alternative**: ELK Stack (if needed)

### Performance Monitoring
- **Google PageSpeed Insights**: Track Core Web Vitals
- **Cloudflare Analytics**: Monitor CDN cache hit ratio
- **Vercel Analytics**: Track page performance

## DNS Configuration
```
storyofdubai.com
├── A record: [Cloudflare IP]
├── CNAME: www → storyofdubai.com
└── CNAME: api → api.storyofdubai.com (Hostinger VPS)

Cloudflare (as CDN + WAF)
├── Origin: api.storyofdubai.com (Hostinger VPS)
├── Cache: 1 hour for static assets
└── SSL: Full (Cloudflare → Origin)
```

## Rollback Procedure
If deployment breaks production:

1. **Immediate** (within 5 minutes)
   - Frontend: Vercel dashboard → Click previous deployment → "Promote to Production"
   - Backend: `git revert [bad commit]` → `git push` → SSH into VPS → `git pull` → `systemctl restart storyofdubai-api`

2. **Database** (if schema broke)
   - Run rollback migration: `alembic downgrade -1`
   - Or restore from backup (if data loss)

## Cost Tracking
| Service | Cost/Month | Notes |
|---------|-----------|-------|
| Hostinger VPS | $5 | Backend + Redis + PostgreSQL |
| Supabase (free) | $0 | 10GB storage, 500 connections |
| Vercel (free) | $0 | Unlimited builds, 100GB bandwidth |
| Cloudflare (free) | $0 | CDN, WAF, DDoS protection |
| Google AdSense | — | Revenue share |
| **TOTAL** | **$5/month** | Pre-revenue |

## Monitoring Checklist
- [ ] Error rates < 0.1% (from Sentry)
- [ ] API response time < 200ms (from Cloudflare Analytics)
- [ ] Core Web Vitals all green (from PageSpeed Insights)
- [ ] Database connections < 50 (from PostgreSQL logs)
- [ ] Disk space > 20% free (from VPS monitoring)
- [ ] SSL certificate valid > 30 days (from Certbot)
