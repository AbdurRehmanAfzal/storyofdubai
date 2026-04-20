import asyncio
from datetime import datetime
from typing import List
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models import ScrapeJob
from app.scrapers.google_places_demo import GooglePlacesScraper
from app.scoring.venue_scorer import VenueScorer

logger = structlog.get_logger()


def get_async_session() -> AsyncSession:
    """Get async session for Celery tasks (must use sync wrapper)"""
    return AsyncSessionLocal()


def create_scrape_job(scraper_name: str, session: AsyncSession) -> ScrapeJob:
    """Create a ScrapeJob record at task start"""
    job = ScrapeJob(
        scraper_name=scraper_name,
        started_at=datetime.utcnow().isoformat(),
        status="running",
        records_collected=0,
        records_failed=0,
    )
    session.add(job)
    session.flush()
    return job


def update_scrape_job(
    job: ScrapeJob,
    status: str,
    records_collected: int = 0,
    records_failed: int = 0,
    error_log: str = None,
    session: AsyncSession = None,
):
    """Update ScrapeJob record at task end"""
    job.status = status
    job.records_collected = records_collected
    job.records_failed = records_failed
    job.completed_at = datetime.utcnow().isoformat()
    if error_log:
        job.error_log = error_log
    if session:
        session.add(job)
        session.flush()


# ============================================================================
# SCRAPER TASKS
# ============================================================================


@celery_app.task(
    name="app.pipeline.tasks.scrape_google_places_all_areas",
    bind=True,
    queue="scrapers",
    max_retries=3,
)
def scrape_google_places_all_areas(self):
    """Scrape Google Places data for all Dubai areas (daily schedule)"""
    logger.info("task_start", task="scrape_google_places_all_areas")

    # Run async scraper synchronously in Celery
    session = AsyncSessionLocal()

    try:
        scraper = GooglePlacesScraper(session)
        result = asyncio.run(scraper.scrape())
        asyncio.run(session.commit())

        logger.info(
            "task_complete",
            task="scrape_google_places_all_areas",
            inserted=result.get("inserted"),
            updated=result.get("updated"),
            api_calls=result.get("api_calls"),
        )

        return {
            "task": "scrape_google_places_all_areas",
            "status": "completed",
            "result": result,
        }
    except Exception as e:
        logger.error(
            "task_failed",
            task="scrape_google_places_all_areas",
            error=str(e),
            exc_info=True,
        )
        raise
    finally:
        asyncio.run(session.close())


@celery_app.task(
    name="app.pipeline.tasks.scrape_google_places_single_area",
    bind=True,
    queue="scrapers",
    max_retries=3,
)
def scrape_google_places_single_area(self, area_slug: str, category_slug: str):
    """Scrape Google Places for a specific area and category"""
    logger.info("Starting: scrape_google_places_single_area", area=area_slug, category=category_slug)
    # TODO: Implement - call GooglePlacesScraper for this area/category
    return {
        "task": "scrape_google_places_single_area",
        "area": area_slug,
        "category": category_slug,
        "status": "pending",
        "message": "Task stub — implementation pending",
    }


# ============================================================================
# SCORING ENGINE TASKS
# ============================================================================


@celery_app.task(
    name="app.pipeline.tasks.run_scoring_engine_all",
    bind=True,
    queue="default",
    max_retries=2,
)
def run_scoring_engine_all(self):
    """Run scoring engine on all active venues (daily schedule)"""
    logger.info("task_start", task="run_scoring_engine_all")

    session = AsyncSessionLocal()

    try:
        from sqlalchemy import select
        from app.models import Venue
        from datetime import datetime, timedelta

        async def score_all():
            # Get all active venues
            stmt = select(Venue).where(Venue.is_active == True)
            result = await session.execute(stmt)
            venues = result.scalars().all()

            scorer = VenueScorer()
            updated_count = 0
            error_count = 0

            for venue in venues:
                try:
                    # Calculate days since last scrape
                    if venue.last_scraped_at:
                        last_scraped = datetime.fromisoformat(
                            venue.last_scraped_at
                        )
                        days_since = (
                            datetime.utcnow() - last_scraped
                        ).days
                    else:
                        days_since = 365

                    # Build score input
                    from app.scoring.venue_scorer import VenueScoreInput

                    score_input = VenueScoreInput(
                        id=venue.id,
                        google_rating=venue.google_rating,
                        review_count=venue.review_count,
                        price_tier=venue.price_tier or 2,
                        days_since_last_review=days_since,
                        has_photos=True,  # Assume Google Places has photos
                        has_phone=bool(venue.phone),
                        has_website=bool(venue.website),
                    )

                    # Score venue
                    score_result = scorer.score(score_input)

                    # Update venue
                    venue.composite_score = score_result.score
                    session.add(venue)
                    updated_count += 1

                except Exception as e:
                    logger.warning(
                        "venue_score_failed",
                        venue_id=venue.id,
                        venue_name=venue.name,
                        error=str(e),
                    )
                    error_count += 1

            # Commit all updates
            await session.commit()

            return {
                "updated": updated_count,
                "errors": error_count,
            }

        result = asyncio.run(score_all())

        logger.info(
            "task_complete",
            task="run_scoring_engine_all",
            updated=result.get("updated"),
            errors=result.get("errors"),
        )

        return {
            "task": "run_scoring_engine_all",
            "status": "completed",
            "result": result,
        }

    except Exception as e:
        logger.error(
            "task_failed",
            task="run_scoring_engine_all",
            error=str(e),
            exc_info=True,
        )
        raise
    finally:
        asyncio.run(session.close())


@celery_app.task(
    name="app.pipeline.tasks.run_scoring_engine_area",
    bind=True,
    queue="default",
)
def run_scoring_engine_area(self, area_slug: str):
    """Run scoring engine on venues in a specific area"""
    logger.info("Starting: run_scoring_engine_area", area=area_slug)
    # TODO: Implement - score all venues in this area
    return {
        "task": "run_scoring_engine_area",
        "area": area_slug,
        "status": "pending",
        "message": "Task stub — implementation pending",
    }


# ============================================================================
# AI ENRICHMENT TASKS
# ============================================================================


@celery_app.task(
    name="app.pipeline.tasks.run_ai_enrichment_pending",
    bind=True,
    queue="enrichment",
    max_retries=2,
)
def run_ai_enrichment_pending(self):
    """Generate AI summaries for venues/pages missing ai_summary (daily schedule)"""
    logger.info("Starting: run_ai_enrichment_pending")
    # TODO: Implement - find venues where ai_summary is NULL, call OpenAI
    return {
        "task": "run_ai_enrichment_pending",
        "status": "pending",
        "message": "Task stub — implementation pending",
    }


# ============================================================================
# DEPLOYMENT TASKS
# ============================================================================


@celery_app.task(
    name="app.pipeline.tasks.trigger_nextjs_rebuild",
    bind=True,
    queue="default",
    max_retries=2,
)
def trigger_nextjs_rebuild(self):
    """Trigger Next.js rebuild on Vercel (daily schedule)"""
    logger.info("Starting: trigger_nextjs_rebuild")
    # TODO: Implement - call Vercel deploy webhook to rebuild static pages
    return {
        "task": "trigger_nextjs_rebuild",
        "status": "pending",
        "message": "Task stub — implementation pending",
    }
