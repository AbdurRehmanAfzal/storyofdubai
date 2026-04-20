# Security Rules — Story of Dubai

Critical security standards that must be followed on every commit. No exceptions.

---

## MANDATORY Security Checklist

Before committing code in these areas, verify ALL checkboxes:

**Areas requiring security review**:
- ✅ Authentication & authorization
- ✅ Database queries (SQL injection prevention)
- ✅ External API calls (secrets handling)
- ✅ Environment variables & config
- ✅ Scraper logic (robots.txt, rate limiting, data)
- ✅ File uploads (if any)
- ✅ Logging (no secrets in logs)

**Checklist**:
```python
# Before committing:
[ ] No hardcoded credentials anywhere (DATABASE_URL, API_KEY, etc.)
[ ] All inputs validated with Pydantic
[ ] No bare except: clauses
[ ] No logging of request bodies (may contain secrets)
[ ] No logging of API keys even in debug mode
[ ] All DB queries use SQLAlchemy parameterized queries
[ ] External API calls wrapped in try/except with proper error handling
[ ] CORS settings match environment (no wildcard in production)
[ ] No stack traces returned to API clients (logged server-side only)
[ ] VCS ignores .env, CLAUDE.local.md, .env.local (via .gitignore)
```

---

## Environment Variable Rules

### The Golden Rule: ZERO Hardcoded Credentials

```python
# ❌ BAD: Hardcoded (NEVER DO THIS)
DATABASE_URL = "postgresql://user:password@localhost:5432/db"
OPENAI_API_KEY = "sk-abc123def456"

# ✅ GOOD: From environment
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    openai_api_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()  # Reads from .env on startup
```

### Config Pattern (pydantic-settings)

```python
# app/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str  # Must be set (required)
    database_pool_size: int = 10
    
    # APIs
    openai_api_key: str
    google_places_api_key: str
    
    # Security
    secret_key: str  # Min 32 chars
    jwt_expiration_seconds: int = 604800  # 7 days
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def __init__(self, **data):
        super().__init__(**data)
        
        # Validate at startup
        if len(self.secret_key) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        if not self.database_url.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("DATABASE_URL must start with postgresql://")

settings = Settings()  # Validates on app startup
```

### .env Structure

```bash
# .env (never committed, in .gitignore)
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/storyofdubai_dev
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-...
GOOGLE_PLACES_API_KEY=AIza...
SECRET_KEY=your-secret-key-min-32-chars-change-in-production
ENVIRONMENT=development
DEBUG=true
```

### VPS Credentials

On VPS, credentials stored in `/etc/storyofdubai/.env`:

```bash
# /etc/storyofdubai/.env (on VPS)
# Owned by root, permissions 600 (read-only by app)
DATABASE_URL=postgresql+asyncpg://app_user:STRONG_PASSWORD@localhost:5432/storyofdubai
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-... (production key)
SECRET_KEY=VERY_LONG_SECRET_KEY_MIN_32_CHARS
ENVIRONMENT=production
DEBUG=false
```

Loaded by systemd service:

```ini
# /etc/systemd/system/storyofdubai-api.service
[Service]
EnvironmentFile=/etc/storyofdubai/.env
ExecStart=/app/storyofdubai/venv/bin/uvicorn app.main:app
```

---

## Scraper Security Rules

### Rate Limiting (MANDATORY)

```python
# ❌ BAD: No delay
for url in urls:
    response = await fetch(url)  # Hammers server

# ✅ GOOD: Rate limiting with jitter
import asyncio
import random

class BaseScraper:
    delay_seconds: int = 2
    jitter_range: tuple = (0, 1)  # Random 0-1 seconds
    
    async def scrape(self):
        for url in urls:
            await self._rate_limit()
            response = await fetch(url)
    
    async def _rate_limit(self):
        """Enforce delay with jitter"""
        delay = self.delay_seconds + random.uniform(*self.jitter_range)
        await asyncio.sleep(delay)
```

### User-Agent Rotation

```python
# ❌ BAD: Same user agent (likely to be blocked)
headers = {"User-Agent": "Mozilla/5.0"}

# ✅ GOOD: Rotate from list
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    # ... more agents
]

import random

headers = {"User-Agent": random.choice(USER_AGENTS)}
```

### Respect robots.txt

```python
# ✅ GOOD: Check robots.txt before scraping new site
import aiohttp
from urllib.robotparser import RobotFileParser

class BaseScraper:
    async def can_scrape(self, domain: str) -> bool:
        """Check if domain allows scraping"""
        try:
            rp = RobotFileParser()
            rp.set_url(f"https://{domain}/robots.txt")
            rp.read()
            return rp.can_fetch("*", f"https://{domain}/")
        except Exception as e:
            logger.warning(f"Could not read robots.txt for {domain}: {e}")
            return False  # When in doubt, don't scrape
    
    async def scrape(self):
        if not await self.can_scrape(domain):
            logger.info(f"Skipping {domain}: robots.txt forbids scraping")
            return
        
        # Safe to scrape
```

### Data Privacy Rules

```python
# ❌ BAD: Storing scraped personal data
class Review(Base):
    __tablename__ = "reviews"
    
    user_email = Column(String)  # NEVER store personal data
    user_phone = Column(String)  # NEVER store personal data

# ✅ GOOD: Only store public business data
class Review(Base):
    __tablename__ = "reviews"
    
    # OK: Public information about the business
    venue_name = Column(String)
    rating = Column(Float)
    review_text = Column(Text)
    
    # NEVER: User personal data
    # user_email, user_phone, user_address, etc.
```

### Proxy Rotation (For High-Volume Scraping)

```python
# For scraping sites that aggressively block:
class ProxiedScraper(BaseScraper):
    def __init__(self, proxy_service="brightdata"):
        self.proxy_service = proxy_service
        # Example: BrightData rotating proxy
        self.proxy = "http://customer-user:password@proxy.provider.com:port"
    
    async def _fetch(self, url: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                proxy=self.proxy,
                timeout=30
            ) as response:
                return await response.text()
```

---

## API Security Rules

### Authentication (Bearer Token / JWT)

```python
# ❌ BAD: No authentication on admin endpoints
@router.post("/scraper/run")
def run_scraper():
    # Anyone can trigger scrapers!
    pass

# ✅ GOOD: Require Bearer token
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthCredentials

security = HTTPBearer()

@router.post("/scraper/run")
async def run_scraper(credentials: HTTPAuthCredentials = Depends(security)):
    user = await verify_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Safe to run scraper
```

### JWT Configuration

```python
# app/security.py
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException

def create_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,  # From .env, min 32 chars
        algorithm="HS256"
    )
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Input Validation (Pydantic)

```python
# ❌ BAD: No validation
@router.get("/venues")
async def get_venues(area: str, limit: int):
    # Anyone can send: limit=-1, limit=999999, area="<script>"
    return await db.query(f"SELECT * FROM venues WHERE area='{area}'")  # SQL injection!

# ✅ GOOD: Validate with Pydantic
from pydantic import BaseModel, Field

class VenueFilter(BaseModel):
    area: str = Field(..., min_length=1, max_length=100)
    limit: int = Field(default=20, ge=1, le=100)  # Min 1, max 100

@router.get("/venues", response_model=ApiResponse)
async def get_venues(
    filters: VenueFilter = Depends(),
    session: AsyncSession = Depends(get_session)
):
    # Pydantic validates: area is string 1-100 chars, limit is 1-100
    stmt = select(Venue).where(Venue.area == filters.area).limit(filters.limit)
    return await session.execute(stmt)
```

### CORS Configuration

```python
# ❌ BAD: Allow all origins (security risk)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # NEVER in production!
)

# ✅ GOOD: Whitelist specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://storyofdubai.com",
        "https://www.storyofdubai.com",
        "http://localhost:3000",  # Dev only
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    allow_credentials=True,
)
```

---

## Database Security

### Parameterized Queries (Always Use SQLAlchemy)

```python
# ❌ BAD: String interpolation (SQL injection!)
result = await session.execute(
    f"SELECT * FROM venues WHERE slug = '{user_input}'"
)

# ✅ GOOD: Parameterized (SQLAlchemy handles escaping)
stmt = select(Venue).where(Venue.slug == user_input)
result = await session.execute(stmt)

# SQLAlchemy never builds raw SQL strings
```

### Connection String Security

```python
# ❌ BAD: Hardcoded in code
DATABASE_URL = "postgresql://user:password@localhost:5432/db"

# ✅ GOOD: From environment
DATABASE_URL = os.getenv("DATABASE_URL")
# Raises error if not set
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in environment")
```

### Database User Permissions

On VPS, create limited DB user:

```sql
-- Create app user (not postgres superuser)
CREATE USER app_user WITH PASSWORD 'STRONG_PASSWORD';

-- Grant only needed permissions
GRANT CONNECT ON DATABASE storyofdubai TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO app_user;

-- NO DELETE or DROP permissions
REVOKE DELETE, DROP ON ALL TABLES IN SCHEMA public FROM app_user;
```

---

## Logging Security

### NEVER Log Secrets

```python
# ❌ BAD: Logs expose secrets
logger.info(f"Connecting to database: {DATABASE_URL}")
logger.info(f"API Key: {OPENAI_API_KEY}")
logger.debug(f"Request body: {request.body}")  # May contain passwords

# ✅ GOOD: Log safely
logger.info("Database connection established")
logger.info(f"API Key: {OPENAI_API_KEY[:10]}...")  # Only first 10 chars
logger.debug(f"Request to {request.url}")  # URL, not body
```

### Error Handling (No Stack Traces to Clients)

```python
# ❌ BAD: Stack trace sent to API client
@router.get("/venues")
async def get_venues():
    try:
        return await service.list_venues()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # Stack trace!

# ✅ GOOD: Log stack trace, return generic error
@router.get("/venues")
async def get_venues():
    try:
        return await service.list_venues()
    except Exception as e:
        logger.error(f"Error listing venues: {e}", exc_info=True)  # Full trace in logs
        raise HTTPException(status_code=500, detail="Internal error")  # Generic to client
```

### Audit Logging

```python
# Log important actions for security audit trail
logger.info(
    f"Admin action: user_id={user.id} action=create_venue venue={venue.name}"
)
```

---

## VPS Security

### SSH Configuration

```bash
# On VPS: Disable password auth, allow key-based only
# /etc/ssh/sshd_config
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes

sudo systemctl restart ssh
```

### Firewall Rules

```bash
# UFW (Ubuntu)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### Automatic Security Updates

```bash
# Install unattended-upgrades
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

# /etc/apt/apt.conf.d/50unattended-upgrades
Unattended-Upgrade::Allowed-Origins {
    "\${distro_id}:\${distro_codename}-security";
};
```

### Fail2Ban (Prevent Brute Force)

```bash
# Install fail2ban
sudo apt install fail2ban

# /etc/fail2ban/jail.local
[sshd]
enabled = true
maxretry = 3
findtime = 600
bantime = 3600
```

---

## What Claude MUST NEVER Do

These are absolute rules:

```python
# ❌ NEVER: Log full request bodies
logger.debug(f"Request: {request.body}")  # May contain passwords

# ❌ NEVER: Log API keys even in debug
logger.debug(f"OpenAI key: {OPENAI_API_KEY}")

# ❌ NEVER: Return stack traces to clients
raise HTTPException(status_code=500, detail=str(exception))

# ❌ NEVER: Hardcode secrets
DATABASE_URL = "postgresql://user:password@..."

# ❌ NEVER: Commit .env files
git commit -m "fix: add credentials" .env  # BLOCKED by .gitignore

# ❌ NEVER: Use bare except without logging
try:
    result = do_something()
except:  # Swallows all exceptions, no logging!
    pass

# ❌ NEVER: Trust user input without validation
user_input = request.query_params.get("area")
stmt = f"SELECT * FROM venues WHERE area = '{user_input}'"  # SQL injection!

# ❌ NEVER: Use wildcard CORS
allow_origins=["*"]  # Security risk
```

---

## Security Review Checklist (Pre-Commit)

Before committing, verify:

- [ ] No hardcoded credentials (DATABASE_URL, API_KEY, SECRET_KEY)
- [ ] All secrets come from environment variables
- [ ] All user inputs validated with Pydantic
- [ ] All database queries use SQLAlchemy parameterized queries
- [ ] No logging of request bodies or API keys
- [ ] Error messages don't leak sensitive info
- [ ] Admin endpoints require authentication (Bearer token)
- [ ] CORS origins whitelisted (no wildcard in production)
- [ ] All external API calls wrapped in try/except
- [ ] Scraper rate limiting present
- [ ] User agent rotation in scrapers
- [ ] robots.txt check in scrapers
- [ ] .env and CLAUDE.local.md in .gitignore
- [ ] No stack traces returned to API clients

---

**Last Updated**: 2026-04-20  
**For**: Story of Dubai  
**Enforced by**: Code review, pre-commit hooks, automated scanning
