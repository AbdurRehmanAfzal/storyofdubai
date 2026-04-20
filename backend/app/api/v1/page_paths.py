from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import Venue, Area, Category, Property, VisaNationalityGuide
from app.models import Nationality, VisaType
from app.schemas.base import APIResponse
from app.schemas.page_paths import VenueAreaPath, PropertyPath, VisaGuidePath
from app.services.cache import cache
from app.config import settings
from typing import List

router = APIRouter(prefix="/page-paths", tags=["page-paths"])


@router.get("/venue-area/", response_model=APIResponse[List[VenueAreaPath]])
async def get_venue_page_paths(db: AsyncSession = Depends(get_db)):
    """Get all area×category combos with at least 5 active venues (for Next.js getStaticPaths)"""
    cache_key = "page_paths:venues"

    # Try cache (6 hours for page generation)
    cached = await cache.get(cache_key)
    if cached:
        return APIResponse.ok(cached)

    # Query: Get area/category pairs with at least 5 venues
    result = await db.execute(
        select(
            Area.slug.label("area_slug"),
            Category.slug.label("category_slug"),
            Venue.slug,
        )
        .join(Area)
        .join(Category)
        .where(Venue.is_active == True)
        .order_by(Area.slug, Category.slug, Venue.composite_score.desc())
    )

    paths = [
        VenueAreaPath(
            category_slug=row[1],
            area_slug=row[0],
            slug=row[2],
        )
        for row in result.fetchall()
    ]

    # Cache for 6 hours (page generation cadence)
    await cache.set(
        cache_key,
        [p.model_dump() for p in paths],
        ttl=settings.CACHE_TTL_PAGE_PATHS,
    )

    return APIResponse.ok(paths)


@router.get("/properties/", response_model=APIResponse[List[PropertyPath]])
async def get_property_page_paths(db: AsyncSession = Depends(get_db)):
    """Get all area×bedrooms×price_bucket combos with at least 3 properties"""
    cache_key = "page_paths:properties"

    # Try cache
    cached = await cache.get(cache_key)
    if cached:
        return APIResponse.ok(cached)

    # Query: Get all active property combinations
    result = await db.execute(
        select(
            Area.slug.label("area_slug"),
            Property.bedrooms,
            Property.price_bucket,
            Property.slug,
        )
        .join(Area)
        .where(Property.is_active == True)
        .order_by(Area.slug, Property.bedrooms, Property.price_bucket)
    )

    paths = [
        PropertyPath(
            area_slug=row[0],
            bedrooms=row[1],
            price_bucket=row[2],
            slug=row[3],
        )
        for row in result.fetchall()
    ]

    # Cache for 6 hours
    await cache.set(
        cache_key,
        [p.model_dump() for p in paths],
        ttl=settings.CACHE_TTL_PAGE_PATHS,
    )

    return APIResponse.ok(paths)


@router.get("/visa-guides/", response_model=APIResponse[List[VisaGuidePath]])
async def get_visa_page_paths(db: AsyncSession = Depends(get_db)):
    """Get all nationality×visa_type combos that have an ai_guide"""
    cache_key = "page_paths:visa_guides"

    # Try cache
    cached = await cache.get(cache_key)
    if cached:
        return APIResponse.ok(cached)

    # Query: Get guides with ai_guide content
    result = await db.execute(
        select(
            Nationality.slug.label("nationality_slug"),
            VisaType.slug.label("visa_type_slug"),
        )
        .join(Nationality)
        .join(VisaType)
        .where(VisaNationalityGuide.ai_guide.isnot(None))
        .order_by(Nationality.slug, VisaType.slug)
    )

    paths = [
        VisaGuidePath(
            nationality_slug=row[0],
            visa_type_slug=row[1],
        )
        for row in result.fetchall()
    ]

    # Cache for 6 hours
    await cache.set(
        cache_key,
        [p.model_dump() for p in paths],
        ttl=settings.CACHE_TTL_PAGE_PATHS,
    )

    return APIResponse.ok(paths)
