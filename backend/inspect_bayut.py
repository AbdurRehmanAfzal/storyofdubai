#!/usr/bin/env python3
"""Quick script to inspect Bayut.com HTML structure."""
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth


async def inspect_bayut():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            locale="en-US",
            timezone_id="Asia/Dubai",
        )
        # Apply stealth
        stealth_instance = Stealth()
        await stealth_instance.apply_stealth_async(context)

        page = await context.new_page()

        url = "https://www.bayut.com/to-rent/apartments/dubai-marina/"
        print(f"Fetching {url}...")
        await page.goto(url, wait_until="networkidle", timeout=30000)

        # Wait for content to load
        await asyncio.sleep(5)

        # Get page content
        content = await page.content()

        # Print first 5000 chars to see structure
        print("\n" + "=" * 80)
        print("PAGE HTML STRUCTURE (first 10000 chars)")
        print("=" * 80)
        print(content[:10000])

        print("\n" + "=" * 80)
        print("SEARCHING FOR LISTING INDICATORS")
        print("=" * 80)

        # Try to find property cards by various selectors
        selectors_to_try = [
            "a[href*='/property/']",
            "article",
            "[class*='card']",
            "[class*='property']",
            "[class*='listing']",
            "[role='link']",
            "[data-testid*='property']",
            "[class*='result']",
            "[class*='ProductCard']",
            "[class*='EPC']",
        ]

        for selector in selectors_to_try:
            try:
                elements = await page.query_selector_all(selector)
                print(f"  {selector}: Found {len(elements)} elements")
                if len(elements) > 0 and len(elements) <= 3:
                    for idx, elem in enumerate(elements[:1]):
                        html = await elem.inner_html()
                        print(f"    Element {idx} HTML (1000 chars): {html[:1000]}...")
                        # Try to get text content
                        text = await elem.inner_text()
                        print(f"    Element {idx} TEXT (500 chars): {text[:500]}...")
            except Exception as e:
                print(f"  {selector}: Error - {e}")

        print("\n" + "=" * 80)
        print("PAGE TITLE AND BODY")
        print("=" * 80)
        title = await page.title()
        body_text = await page.locator("body").inner_text()
        print(f"Title: {title}")
        print(f"Body text (first 1000 chars): {body_text[:1000]}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(inspect_bayut())
