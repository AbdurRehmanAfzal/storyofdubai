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

            # Random delay to mimic human reading time
            await asyncio.sleep(random.uniform(3, 5))

            # Try different selectors for property cards - use broader selectors
            listings = await page.query_selector_all('a[href*="/property/"]')

            if not listings:
                # Fallback: try other common selectors
                listings = await page.query_selector_all('[href*="/property/"]')

            if not listings:
                # Even broader fallback
                listings = await page.query_selector_all('a[href*="property"]')

            self.properties_found += len(listings)
            logger.info("bayut_listings_found", area=area_slug, count=len(listings))

            for idx, listing in enumerate(listings[:limit]):
                try:
                    parsed = await self.parse_listing(listing, area_slug)
                    if parsed:
                        results.append(parsed)
                        self.properties_parsed += 1

                    # Random scroll to simulate human browsing
                    if idx % 5 == 0:
                        await page.evaluate("window.scrollBy(0, 300)")
                        await asyncio.sleep(random.uniform(0.5, 1.5))

                except Exception as e:
                    logger.warning("bayut_parse_error", area=area_slug, index=idx, error=str(e))
                    self.errors.append(str(e))
                    continue

        except Exception as e:
            logger.error("bayut_area_error", area=area_slug, error=str(e))
            self.errors.append(str(e))

        return results

    async def parse_listing(self, listing, area_slug: str) -> dict | None:
        """Parse a single property listing from HTML link element."""
        try:
            # The listing is an <a> tag href pointing to /property/...
            href = await listing.get_attribute("href")
            if not href or "/property/" not in href:
                return None

            # Get all text content from the link
            full_text = (await listing.inner_text()).strip()
            if not full_text:
                return None

            # Try to extract title - first line usually
            lines = full_text.split("\n")
            title = lines[0].strip() if lines else None
            if not title:
                return None

            # Look for price in the text (usually contains "AED" or digits followed by pattern)
            price_match = re.search(r"(AED\s*)?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", full_text)
            if not price_match:
                return None

            price_text = price_match.group(2) if price_match else "0"
            price_aed = int(re.sub(r"[^\d]", "", price_text) or 0)
            if price_aed == 0 or price_aed < 1000:  # Unrealistic price
                return None

            # Look for bedroom info - usually a number followed by "b" or "BR" or "bed"
            bed_match = re.search(r"(\d+)\s*(?:b|br|bed)", full_text, re.IGNORECASE)
            bedrooms = int(bed_match.group(1)) if bed_match else 1

            # Look for bathroom info
            bath_match = re.search(r"(\d+)\s*(?:ba|bath)", full_text, re.IGNORECASE)
            bathrooms = int(bath_match.group(1)) if bath_match else 1

            # Look for sqft/area info
            size_match = re.search(r"([\d.]+)\s*(?:sqft|sq\.?ft|sqm|m2)", full_text, re.IGNORECASE)
            size_sqft = float(size_match.group(1)) if size_match else None

            # Build affiliate URL from href
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
            logger.warning("bayut_parse_listing_error", error=str(e), area=area_slug)
            return None

    async def scrape(
        self, areas: list[str] | None = None, limit_per_area: int = 40
    ) -> list[dict]:
        """Main scrape method — scrapes all areas and returns property data."""
        target_areas = areas or list(BAYUT_AREAS.keys())
        all_results = []

        async with async_playwright() as p:
            browser: Browser = await p.chromium.launch(
                headless=False,  # Headed mode - less suspicious to detection systems
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-breakpad",
                    "--disable-client-side-phishing-detection",
                    "--disable-component-extensions-with-background-pages",
                    "--disable-default-apps",
                    "--disable-extensions",
                    "--disable-sync",
                ],
            )

            context = await browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent=self.get_user_agent(),
                locale="en-US",
                timezone_id="Asia/Dubai",  # Match Bayut's region
            )

            page = await context.new_page()

            # Masking without stealth plugin (stealth plugin itself triggers detection)
            await context.add_init_script(
                """
                Object.defineProperty(navigator, 'webdriver', { get: () => false });
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
                Object.defineProperty(navigator, 'languages', { get: () => ['en-US'] });
                delete navigator.__proto__.webdriver;
            """
            )

            for area_slug in target_areas:
                logger.info("bayut_scraping_area", area=area_slug)
                results = await self.scrape_area(area_slug, page, limit_per_area)
                all_results.extend(results)
                self.requests_made += 1

                # Random delay to mimic human behavior
                delay = random.uniform(3.0, 6.0)
                logger.info("rate_limit_delay", seconds=delay)
                await asyncio.sleep(delay)

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
