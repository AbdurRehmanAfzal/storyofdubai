from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List
import secrets


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    APP_NAME: str = "Story of Dubai API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str = secrets.token_urlsafe(32)

    # Database
    DATABASE_URL: str
    DATABASE_URL_SYNC: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Redis TTLs (seconds)
    CACHE_TTL_RANKINGS: int = 3600        # 1 hour
    CACHE_TTL_VENUE: int = 86400          # 24 hours
    CACHE_TTL_PAGE_PATHS: int = 21600     # 6 hours
    CACHE_TTL_VISA: int = 604800          # 7 days

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://storyofdubai.com",
        "https://www.storyofdubai.com",
    ]

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_MAX_TOKENS: int = 400
    OPENAI_DAILY_BUDGET_USD: float = 2.0  # hard stop

    # Google Places
    GOOGLE_PLACES_API_KEY: str = ""
    GOOGLE_PLACES_DAILY_BUDGET_USD: float = 5.0  # hard stop

    # Scrapers
    SCRAPER_DELAY_SECONDS: float = 2.0
    SCRAPER_JITTER_SECONDS: float = 1.0
    SCRAPER_MAX_RETRIES: int = 3
    SCRAPER_API_KEY: str = ""  # ScraperAPI proxy

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = {"development", "testing", "production"}
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT == "testing"


settings = Settings()
