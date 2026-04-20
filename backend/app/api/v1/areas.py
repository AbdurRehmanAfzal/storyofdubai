from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Area
from app.schemas.base import APIResponse
from app.schemas.venue import AreaResponse
from app.services.cache import cache
from app.config import settings
from typing import List

router = APIRouter(prefix="/areas", tags=["areas"])


@router.get("/", response_model=APIResponse[List[AreaResponse]])
async def list_areas(db: AsyncSession = Depends(get_db)):
    """List all areas (cached 24 hours)"""
    cache_key = "areas:all"

    # Try cache
    cached = await cache.get(cache_key)
    if cached:
        return APIResponse.ok(cached)

    # Query
    result = await db.execute(select(Area).where(Area.is_active == True))
    areas = result.scalars().all()

    area_list = [
        AreaResponse(
            id=str(a.id),
            name=a.name,
            slug=a.slug,
            description=a.description,
            latitude=a.latitude,
            longitude=a.longitude,
            meta_description=a.meta_description,
            character_tags=a.character_tags,
            is_active=a.is_active,
            created_at=a.created_at.isoformat(),
            updated_at=a.updated_at.isoformat(),
        )
        for a in areas
    ]

    # Cache for 24 hours
    await cache.set(
        cache_key,
        [a.model_dump() for a in area_list],
        ttl=settings.CACHE_TTL_VENUE,
    )

    return APIResponse.ok(area_list)


@router.get("/{slug}/", response_model=APIResponse[AreaResponse])
async def get_area(slug: str, db: AsyncSession = Depends(get_db)):
    """Get single area by slug"""
    cache_key = f"area:{slug}"

    # Try cache
    cached = await cache.get(cache_key)
    if cached:
        return APIResponse.ok(cached)

    # Query
    result = await db.execute(select(Area).where(Area.slug == slug))
    area = result.scalar_one_or_none()

    if not area:
        return APIResponse.fail("AREA_NOT_FOUND", f"Area with slug '{slug}' not found")

    response = AreaResponse(
        id=str(area.id),
        name=area.name,
        slug=area.slug,
        description=area.description,
        latitude=area.latitude,
        longitude=area.longitude,
        meta_description=area.meta_description,
        character_tags=area.character_tags,
        is_active=area.is_active,
        created_at=area.created_at.isoformat(),
        updated_at=area.updated_at.isoformat(),
    )

    # Cache for 24 hours
    await cache.set(cache_key, response.model_dump(), ttl=settings.CACHE_TTL_VENUE)

    return APIResponse.ok(response)
