#!/usr/bin/env python3
"""Run Google Places scraper demo.

This script:
1. Initializes database connection
2. Creates all tables (if they don't exist)
3. Runs the Google Places scraper for ~500 restaurants
4. Prints statistics

Usage:
    python run_scraper_demo.py

Requirements:
- .env file with DATABASE_URL and GOOGLE_PLACES_API_KEY set
- PostgreSQL database running and accessible
"""

import asyncio
import sys
import os
from datetime import datetime

# Add backend to path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import engine, AsyncSessionLocal, Base
from app.scrapers.google_places_demo import GooglePlacesScraper
from app.config import settings

logger = structlog.get_logger()


async def main():
    """Main entry point."""
    logger.info("scraper_demo_start", environment=settings.ENVIRONMENT)

    # 1. Create tables
    logger.info("creating_database_tables")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("database_tables_created")
    except Exception as e:
        logger.error("database_creation_failed", error=str(e), exc_info=True)
        return 1

    # 2. Run scraper
    logger.info("initializing_scraper")
    async with AsyncSessionLocal() as session:
        try:
            scraper = GooglePlacesScraper(session)

            logger.info("running_scraper")
            result = await scraper.scrape()

            # Commit changes (handle pending rollback from errors)
            try:
                await session.commit()
            except Exception as e:
                logger.error("commit_failed", error=str(e))
                await session.rollback()
                await session.commit()  # Commit what we can

            # Print results
            print("\n" + "=" * 60)
            print("GOOGLE PLACES SCRAPER DEMO — RESULTS")
            print("=" * 60)
            print(f"⏱️  Start Time: {datetime.utcnow().isoformat()}")
            print(f"\n📊 Statistics:")
            print(f"   ✅ Venues Inserted: {result['inserted']}")
            print(f"   🔄 Venues Updated: {result['updated']}")
            print(f"   ⊘  Venues Skipped: {result['skipped']}")
            print(f"   ❌ Parse Errors: {result['errors']}")
            print(f"   🔗 API Calls: {result['api_calls']}")
            print(f"   ⏱️  Duration: {result['duration_seconds']}s")
            print("\n" + "=" * 60)

            if result["inserted"] + result["updated"] == 0:
                print(
                    "\n⚠️  WARNING: No venues were scraped."
                    "\nPossible reasons:"
                    "\n- GOOGLE_PLACES_API_KEY not set or invalid"
                    "\n- API quota exceeded"
                    "\n- Network error"
                    "\nCheck your .env file and Google Cloud Console."
                )
                return 1

            print("\n✅ Scraper completed successfully!")
            print(
                f"\nNext steps:"
                f"\n1. Run scoring engine: python -m app.pipeline.tasks"
                f"\n2. Trigger Next.js rebuild"
                f"\n3. Check storyofdubai.com for live pages"
            )
            return 0

        except Exception as e:
            logger.error("scraper_failed", error=str(e), exc_info=True)
            print(f"\n❌ Scraper failed: {str(e)}")
            return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
