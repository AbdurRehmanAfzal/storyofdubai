from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.venue import Area
from app.models.property import Property
import structlog
import uuid
from datetime import datetime

logger = structlog.get_logger()


def save_properties(db: Session, properties: list[dict]) -> dict:
    """Save scraped properties to database.

    Args:
        db: SQLAlchemy session
        properties: List of property dictionaries from scraper

    Returns:
        Dictionary with counts: {saved, updated, skipped}
    """
    saved = 0
    updated = 0
    skipped = 0

    for prop_data in properties:
        try:
            area_slug = prop_data.get("area_slug")
            area = db.execute(select(Area).where(Area.slug == area_slug)).scalar_one_or_none()
            if not area:
                logger.warning("property_area_not_found", area_slug=area_slug)
                skipped += 1
                continue

            # Check for duplicate by slug
            existing = db.execute(
                select(Property).where(Property.slug == prop_data["slug"])
            ).scalar_one_or_none()

            if existing:
                # Update existing property
                existing.price_aed = prop_data["price_aed"]
                existing.price_bucket = prop_data["price_bucket"]
                existing.affiliate_url = prop_data.get("affiliate_url", "")
                existing.last_scraped_at = datetime.utcnow().isoformat()
                db.merge(existing)
                updated += 1
            else:
                # Create new property
                prop = Property(
                    id=str(uuid.uuid4()),
                    title=prop_data["title"],
                    slug=prop_data["slug"],
                    area_id=area.id,
                    bedrooms=prop_data["bedrooms"],
                    bathrooms=prop_data.get("bathrooms"),
                    size_sqft=prop_data.get("size_sqft"),
                    price_aed=prop_data["price_aed"],
                    price_bucket=prop_data["price_bucket"],
                    property_type=prop_data.get("property_type", "apartment"),
                    affiliate_url=prop_data.get("affiliate_url", ""),
                    composite_score=0.0,
                    is_active=True,
                    last_scraped_at=datetime.utcnow().isoformat(),
                )
                db.add(prop)
                saved += 1

        except Exception as e:
            logger.error("property_save_error", error=str(e), slug=prop_data.get("slug"))
            skipped += 1

    db.commit()
    logger.info("properties_saved", saved=saved, updated=updated, skipped=skipped)
    return {"saved": saved, "updated": updated, "skipped": skipped}
