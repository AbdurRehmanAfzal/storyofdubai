#!/usr/bin/env python3
"""Standalone Bayut property scraper runner.

Usage:
    python run_bayut_scraper.py

Environment:
    Requires .env file with DATABASE_URL (PostgreSQL)
"""
import asyncio
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.insert(0, "/home/abdurrehmanafzal/Documents/storyofdubai/backend")

from app.config import settings
from app.scrapers.bayut import BayutScraper
from app.scrapers.db_writer import save_properties
from app.models import *  # noqa — ensures all models are registered


async def main():
    print("=" * 70)
    print("BAYUT PROPERTY SCRAPER")
    print("=" * 70)
    print("\nTarget: Dubai rental apartments across 10 areas")
    print("Source: Bayut.com (JavaScript-rendered listings)")
    print("Rate limit: 3s + jitter between area requests")
    print("Listings per area: 30 properties max\n")

    scraper = BayutScraper()

    try:
        print("Starting scraper...\n")
        properties = await scraper.scrape(limit_per_area=30)

        print("\n" + "=" * 70)
        print("SCRAPER RESULTS")
        print("=" * 70)
        print(f"Total properties parsed: {len(properties)}")
        print(f"Properties found on page: {scraper.properties_found}")
        print(f"Properties successfully parsed: {scraper.properties_parsed}")
        print(f"Total requests made: {scraper.requests_made}")
        print(f"Total errors: {len(scraper.errors)}")
        stats = scraper.get_stats()
        print(f"Duration: {stats['duration_seconds']}s\n")

        if scraper.errors:
            print("ERRORS:")
            for err in scraper.errors[:5]:
                print(f"  - {err}")
            if len(scraper.errors) > 5:
                print(f"  ... and {len(scraper.errors) - 5} more errors")
            print()

        if properties:
            print("=" * 70)
            print("DATABASE SAVE")
            print("=" * 70)

            # Create database session
            engine = create_engine(settings.database_url)
            Session = sessionmaker(bind=engine)
            with Session() as db:
                stats_db = save_properties(db, properties)
                print(
                    f"Saved: {stats_db['saved']}, Updated: {stats_db['updated']}, Skipped: {stats_db['skipped']}\n"
                )

            print("=" * 70)
            print("SAMPLE PROPERTIES")
            print("=" * 70)
            for prop in properties[:3]:
                print(f"\n  Title: {prop['title']}")
                print(f"  Area: {prop['area_slug']}")
                print(f"  Bedrooms: {prop['bedrooms']}")
                print(f"  Price: AED {prop['price_aed']:,} ({prop['price_bucket']})")
                print(f"  Slug: {prop['slug']}")

            print("\n✅ Scraper completed successfully!")
        else:
            print("⚠️  No properties scraped. Check network/selectors.")

    except Exception as e:
        print(f"\n❌ Scraper failed: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
