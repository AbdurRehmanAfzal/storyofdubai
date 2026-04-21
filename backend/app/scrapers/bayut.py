import asyncio
import random
import re
import time
from typing import Any
from playwright.async_api import async_playwright, Page, Browser
from app.scrapers.base import BaseScraper
from app.config import settings
import structlog

logger = structlog.get_logger()

BAYUT_AREAS = {
    "dubai-marina": "dubai-marina",
    "downtown-dubai": "downtown-dubai",
    "business-bay": "business-bay",
    "jumeirah-village-circle": "jumeirah-village-circle",
    "palm-jumeirah": "palm-jumeirah",
    "dubai-hills-estate": "dubai-hills-estate",
    "jumeirah": "jumeirah",
    "al-barsha": "al-barsha",
    "deira": "deira",
    "bur-dubai": "bur-dubai",
}

PRICE_BUCKETS = [
    (0, 50000, "under-50k"),
    (50000, 100000, "50k-100k"),
    (100000, 200000, "100k-200k"),
    (200000, float("inf"), "200k-plus"),
]


class BayutScraper(BaseScraper):
    """
    Scrapes rental property listings from Bayut.com.
    Uses Playwright for JS rendering.
    Rate limit: 1 request per 3 seconds (stricter than base).
    """

    DELAY = 3.0
    JITTER = 1.5

    def __init__(self):
        super().__init__()
        self.properties_found = 0
        self.properties_parsed = 0

    def get_price_bucket(self, price_aed: int) -> str:
        """Determine price bucket from AED amount."""
        for low, high, label in PRICE_BUCKETS:
            if low <= price_aed < high:
                return label
        return "200k-plus"

    def slugify(self, text: str) -> str:
        """Convert text to URL-safe slug."""
        text = text.lower().strip()
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[\s_]+", "-", text)
        text = re.sub(r"-+", "-", text)
        return text[:100]

    async def scrape_area(self, area_slug: str, page: Page, limit: int = 40) -> list[dict]:
        """Scrape all properties in a single area."""
        url = f"https://www.bayut.com/to-rent/apartments/{area_slug}/"
        results = []

        try:
            logger.info("bayut_fetching_area", area=area_slug, url=url)
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_selector('[class*="listing"]', timeout=10000)
            await asyncio.sleep(random.uniform(2, 4))

            # Try different selectors for property cards
            listings = await page.query_selector_all('article[class*="property"]')
            if not listings:
                listings = await page.query_selector_all('[data-testid="property-card"]')
            if not listings:
                listings = await page.query_selector_all('[class*="card"]')

            self.properties_found += len(listings)
            logger.info("bayut_listings_found", area=area_slug, count=len(listings))

            for idx, listing in enumerate(listings[:limit]):
                try:
                    parsed = await self.parse_listing(listing, area_slug)
                    if parsed:
                        results.append(parsed)
                        self.properties_parsed += 1
                except Exception as e:
                    logger.warning("bayut_parse_error", area=area_slug, index=idx, error=str(e))
                    self.errors.append(str(e))
                    continue

        except Exception as e:
            logger.error("bayut_area_error", area=area_slug, error=str(e))
            self.errors.append(str(e))

        return results

    async def parse_listing(self, listing, area_slug: str) -> dict | None:
        """Parse a single property listing from HTML element."""
        try:
            # Title
            title_el = await listing.query_selector("h2, [class*='title']")
            title = (await title_el.inner_text()).strip() if title_el else None
            if not title:
                return None

            # Price
            price_el = await listing.query_selector("[class*='price']")
            price_text = (await price_el.inner_text()).strip() if price_el else "0"
            price_aed = int(re.sub(r"[^\d]", "", price_text) or 0)
            if price_aed == 0:
                return None

            # Bedrooms
            bed_el = await listing.query_selector("[aria-label*='bed'], [class*='bed']")
            bed_text = (await bed_el.inner_text()).strip() if bed_el else "1"
            bedrooms = int(re.sub(r"[^\d]", "", bed_text) or 1)

            # Bathrooms
            bath_el = await listing.query_selector("[aria-label*='bath'], [class*='bath']")
            bath_text = (await bath_el.inner_text()).strip() if bath_el else "1"
            bathrooms = int(re.sub(r"[^\d]", "", bath_text) or 1)

            # Size
            size_el = await listing.query_selector("[aria-label*='sqft'], [class*='area']")
            size_text = (await size_el.inner_text()).strip() if size_el else ""
            size_sqft = float(re.sub(r"[^\d.]", "", size_text) or 0) or None

            # Link (for affiliate URL)
            link_el = await listing.query_selector("a[href*='/property/']")
            href = await link_el.get_attribute("href") if link_el else ""
            affiliate_url = (
                f"https://www.bayut.com{href}" if href and href.startswith("/") else href
            )

            slug = self.slugify(f"{title}-{area_slug}-{bedrooms}br")

            return {
                "title": title,
                "slug": slug,
                "area_slug": area_slug,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "size_sqft": size_sqft,
                "price_aed": price_aed,
                "price_bucket": self.get_price_bucket(price_aed),
                "property_type": "apartment",
                "affiliate_url": affiliate_url or "",
            }
        except Exception as e:
            logger.warning("bayut_parse_listing_error", error=str(e))
            return None

    async def scrape(
        self, areas: list[str] | None = None, limit_per_area: int = 40
    ) -> list[dict]:
        """Main scrape method — scrapes all areas and returns property data."""
        target_areas = areas or list(BAYUT_AREAS.keys())
        all_results = []

        async with async_playwright() as p:
            browser: Browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                ],
            )

            context = await browser.new_context(
                viewport={"width": 1440, "height": 900},
                user_agent=self.get_user_agent(),
                locale="en-US",
            )

            # Mask automation signals
            await context.add_init_script(
                """
                Object.defineProperty(navigator, 'webdriver', { get: () => false });
            """
            )

            page = await context.new_page()

            for area_slug in target_areas:
                logger.info("bayut_scraping_area", area=area_slug)
                results = await self.scrape_area(area_slug, page, limit_per_area)
                all_results.extend(results)
                self.requests_made += 1
                await self.rate_limit_delay()

            await browser.close()

        logger.info(
            "bayut_complete",
            total=len(all_results),
            properties_found=self.properties_found,
            properties_parsed=self.properties_parsed,
            stats=self.get_stats(),
        )
        return all_results

    def parse(self, raw_data: Any) -> dict:
        """Parse method (not used for Bayut, parsing done during scrape)."""
        return raw_data
