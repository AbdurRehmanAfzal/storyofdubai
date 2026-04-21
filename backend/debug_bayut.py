#!/usr/bin/env python3
"""Debug script to see actual page content."""
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
import json


async def debug_bayut():
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
        print(f"Navigating to {url}...")
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)

        await asyncio.sleep(5)

        # Get page title and check if it's captcha
        title = await page.title()
        print(f"Page Title: {title}")

        # Get all text
        body_text = await page.locator("body").inner_text()
        print(f"\nBody Text (first 2000 chars):\n{body_text[:2000]}")

        # Check for property links
        links = await page.query_selector_all("a")
        print(f"\nTotal <a> elements: {len(links)}")

        # Find links with /property/ in href
        property_links = []
        for link in links[:100]:  # Check first 100
            href = await link.get_attribute("href")
            if href and "/property/" in href:
                property_links.append(href)

        print(f"Links with '/property/': {len(property_links)}")
        if property_links:
            print("Sample property links:")
            for link in property_links[:3]:
                print(f"  {link}")

        # Try to get HTML of first few links
        if property_links:
            print("\nAnalyzing first property link:")
            first_link = await page.locator(f'a[href="{property_links[0]}"]').first
            html = await first_link.inner_html()
            text = await first_link.inner_text()
            print(f"HTML (500 chars): {html[:500]}")
            print(f"TEXT: {text}")

        # Try to take a screenshot
        print("\nTaking screenshot...")
        await page.screenshot(path="/tmp/bayut_debug.png")
        print("Screenshot saved to /tmp/bayut_debug.png")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_bayut())
