from openai import OpenAI
from sqlalchemy.orm import Session
from sqlalchemy import select
import time
import structlog

from app.config import settings
from app.models.venue import Venue, Area, Category
from app.models.visa import VisaNationalityGuide, Nationality, VisaType
from app.models.property import Property, Developer
from app.ai_enrichment.prompts import (
    INDIVIDUAL_VENUE_PROMPT,
    VISA_GUIDE_PROMPT,
    PROPERTY_PROMPT,
)

logger = structlog.get_logger()
client = OpenAI(api_key=settings.OPENAI_API_KEY)

DAILY_COST_LIMIT = 3.0
COST_PER_CALL = 0.0002
_session_cost = 0.0


def _under_budget() -> bool:
    return _session_cost < DAILY_COST_LIMIT


def _generate(prompt: str, max_tokens: int = 400) -> str | None:
    global _session_cost
    if not _under_budget():
        logger.warning("budget_limit_reached", spent=_session_cost)
        return None
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=max_tokens,
        )
        _session_cost += COST_PER_CALL
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error("openai_error", error=str(e))
        return None


def enrich_venues(db: Session, limit: int = 500) -> int:
    from sqlalchemy import or_
    venues = db.execute(
        select(Venue)
        .where(Venue.is_active == True, or_(Venue.description == "", Venue.description == None))
        .limit(limit)
    ).scalars().all()

    enriched = 0
    price_labels = {
        1: "budget-friendly ($)",
        2: "mid-range ($$)",
        3: "upscale ($$$)",
        4: "luxury ($$$$)",
    }

    for venue in venues:
        if not _under_budget():
            logger.warning("budget_reached_venues", enriched=enriched)
            break
        area = db.get(Area, venue.area_id)
        category = db.get(Category, venue.category_id)
        if not area or not category:
            continue

        prompt = INDIVIDUAL_VENUE_PROMPT.format(
            venue_name=venue.name,
            area_name=area.name,
            category=category.name,
            rating=venue.rating or "unrated",
            review_count=f"{venue.review_count:,}" if venue.review_count else "a number of",
            price_tier=getattr(venue, 'price_tier', 2) if hasattr(venue, 'price_tier') else 2,
        )

        text = _generate(prompt)
        if text:
            venue.description = text
            enriched += 1

        if enriched % 10 == 0 and enriched > 0:
            db.commit()
            logger.info("venues_progress", enriched=enriched, cost=f"${_session_cost:.3f}")
        time.sleep(0.3)

    db.commit()
    logger.info("venues_done", enriched=enriched, cost=f"${_session_cost:.3f}")
    return enriched


def enrich_visa_guides(db: Session, limit: int = 400) -> int:
    from sqlalchemy import or_
    guides = db.execute(
        select(VisaNationalityGuide)
        .where(or_(VisaNationalityGuide.ai_guide == "", VisaNationalityGuide.ai_guide == None))
        .limit(limit)
    ).scalars().all()

    enriched = 0
    for guide in guides:
        if not _under_budget():
            logger.warning("budget_reached_visas", enriched=enriched)
            break

        nat = db.get(Nationality, guide.nationality_id)
        vt = db.get(VisaType, guide.visa_type_id)
        if not nat or not vt:
            continue

        years = vt.duration_days // 365
        duration_years = f"{years} year{'s' if years > 1 else ''}"

        prompt = VISA_GUIDE_PROMPT.format(
            nationality=nat.name,
            visa_name=vt.name,
            cost_aed=f"{vt.cost_aed:,}",
            processing_days=vt.processing_days,
            duration_days=vt.duration_days,
            duration_years=duration_years,
            category=vt.category,
        )

        text = _generate(prompt, max_tokens=500)
        if text:
            guide.ai_guide = text
            enriched += 1

        if enriched % 10 == 0 and enriched > 0:
            db.commit()
            logger.info("visas_progress", enriched=enriched, cost=f"${_session_cost:.3f}")
        time.sleep(0.3)

    db.commit()
    logger.info("visas_done", enriched=enriched, cost=f"${_session_cost:.3f}")
    return enriched


def enrich_properties(db: Session, limit: int = 306) -> int:
    from sqlalchemy import or_
    props = db.execute(
        select(Property)
        .where(Property.is_active == True, or_(Property.description == "", Property.description == None))
        .limit(limit)
    ).scalars().all()

    enriched = 0
    bucket_labels = {
        "under-50k": "budget-friendly",
        "50k-100k": "mid-range",
        "100k-200k": "upscale",
        "200k-plus": "luxury",
    }

    for prop in props:
        if not _under_budget():
            logger.warning("budget_reached_properties", enriched=enriched)
            break

        area = db.get(Area, prop.area_id)
        dev = db.get(Developer, prop.developer_id) if prop.developer_id else None
        if not area:
            continue

        prompt = PROPERTY_PROMPT.format(
            bedrooms=prop.bedrooms,
            area_name=area.name,
            price_aed=f"{prop.price_aed:,}",
            size_sqft=int(prop.size_sqft) if prop.size_sqft else "spacious",
            developer=dev.name if dev else "a leading UAE developer",
            price_bucket=bucket_labels.get(prop.price_bucket, "mid-range"),
        )

        text = _generate(prompt)
        if text:
            prop.description = text
            enriched += 1

        if enriched % 10 == 0 and enriched > 0:
            db.commit()
            logger.info("props_progress", enriched=enriched, cost=f"${_session_cost:.3f}")
        time.sleep(0.3)

    db.commit()
    logger.info("props_done", enriched=enriched, cost=f"${_session_cost:.3f}")
    return enriched
