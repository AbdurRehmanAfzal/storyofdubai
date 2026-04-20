import asyncio
import random
import time
from abc import ABC, abstractmethod
from typing import Any
import httpx
import structlog
from app.config import settings

logger = structlog.get_logger()

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
]


class BaseScraper(ABC):
    """Base scraper class that all specific scrapers inherit from.

    Provides:
    - Rate limiting with configurable delay + jitter
    - Automatic retries with exponential backoff
    - User-agent rotation to avoid detection
    - Request statistics tracking
    - Error logging and aggregation
    """

    MAX_RETRIES = settings.SCRAPER_MAX_RETRIES
    DELAY = settings.SCRAPER_DELAY_SECONDS
    JITTER = settings.SCRAPER_JITTER_SECONDS

    def __init__(self):
        self.session_start = time.time()
        self.requests_made = 0
        self.errors = []
        self._ua_index = 0

    def get_user_agent(self) -> str:
        """Get next user agent in rotation"""
        ua = USER_AGENTS[self._ua_index % len(USER_AGENTS)]
        self._ua_index += 1
        return ua

    async def rate_limit_delay(self):
        """Apply rate limit delay with random jitter"""
        delay = self.DELAY + random.uniform(0, self.JITTER)
        await asyncio.sleep(delay)

    async def fetch_with_retry(self, url: str, **kwargs) -> httpx.Response:
        """Fetch URL with automatic retries and exponential backoff.

        Args:
            url: URL to fetch
            **kwargs: Additional arguments passed to httpx.get()

        Returns:
            httpx.Response: Response from successful request

        Raises:
            httpx.HTTPError: If all retries exhausted
        """
        headers = kwargs.pop("headers", {})
        headers["User-Agent"] = self.get_user_agent()

        for attempt in range(self.MAX_RETRIES):
            try:
                await self.rate_limit_delay()
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(url, headers=headers, **kwargs)
                    response.raise_for_status()
                    self.requests_made += 1
                    return response
            except (httpx.TimeoutException, httpx.HTTPStatusError) as e:
                error_msg = str(e)
                self.errors.append(error_msg)
                logger.warning(
                    "scraper_retry",
                    url=url,
                    attempt=attempt + 1,
                    error=error_msg,
                )
                if attempt == self.MAX_RETRIES - 1:
                    raise
                # Exponential backoff: 1s, 2s, 4s
                await asyncio.sleep(2 ** attempt)

    @abstractmethod
    async def scrape(self, **kwargs) -> list[dict[str, Any]]:
        """Main scrape method implemented by subclasses.

        Returns:
            List of parsed data dictionaries
        """
        pass

    @abstractmethod
    def parse(self, raw_data: Any) -> dict[str, Any]:
        """Parse raw response data into structured format.

        Implemented by subclasses for specific data sources.

        Args:
            raw_data: Raw response data (JSON, HTML, etc)

        Returns:
            Parsed dictionary
        """
        pass

    def get_stats(self) -> dict:
        """Return scraper session statistics"""
        return {
            "requests_made": self.requests_made,
            "errors_count": len(self.errors),
            "duration_seconds": round(time.time() - self.session_start, 2),
        }
