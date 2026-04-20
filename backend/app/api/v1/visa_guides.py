from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.database import get_db
from app.models import VisaNationalityGuide, Nationality, VisaType
from app.schemas.base import APIResponse, PaginationMeta
from app.schemas.visa import VisaNationalityGuideResponse
from app.services.cache import cache
from app.config import settings
from typing import List, Optional

router = APIRouter(prefix="/visa-guides", tags=["visa-guides"])


@router.get("/", response_model=APIResponse[List[VisaNationalityGuideResponse]])
async def list_visa_guides(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    nationality: Optional[str] = None,
    visa_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List visa guides with optional filters"""
    cache_key = f"visa_guides:list:{page}:{per_page}:{nationality}:{visa_type}"

    # Try cache
    cached = await cache.get(cache_key)
    if cached:
        return APIResponse.ok(cached["data"], cached["meta"])

    # Build query
    query = select(VisaNationalityGuide)

    if nationality:
        query = query.join(Nationality).where(Nationality.slug == nationality)
    if visa_type:
        query = query.join(VisaType).where(VisaType.slug == visa_type)

    # Get total count
    count_result = await db.execute(select(func.count(VisaNationalityGuide.id)))
    total = count_result.scalar() or 0

    # Pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)

    # Fetch
    result = await db.execute(query)
    guides = result.scalars().all()

    guide_list = [
        VisaNationalityGuideResponse(
            id=str(g.id),
            nationality_id=str(g.nationality_id),
            visa_type_id=str(g.visa_type_id),
            specific_requirements=g.specific_requirements,
            ai_guide=g.ai_guide,
            created_at=g.created_at.isoformat(),
            updated_at=g.updated_at.isoformat(),
        )
        for g in guides
    ]

    meta = PaginationMeta(
        total=total,
        page=page,
        per_page=per_page,
        has_next=(page * per_page) < total,
        has_prev=page > 1,
    )

    # Cache for 7 days (visa info rarely changes)
    await cache.set(
        cache_key,
        {"data": [g.model_dump() for g in guide_list], "meta": meta.model_dump()},
        ttl=settings.CACHE_TTL_VISA,
    )

    return APIResponse.ok(guide_list, meta)


@router.get(
    "/{nationality_slug}/{visa_type_slug}/",
    response_model=APIResponse[VisaNationalityGuideResponse],
)
async def get_visa_guide(
    nationality_slug: str, visa_type_slug: str, db: AsyncSession = Depends(get_db)
):
    """Get specific visa guide by nationality and type"""
    cache_key = f"visa_guide:{nationality_slug}:{visa_type_slug}"

    # Try cache
    cached = await cache.get(cache_key)
    if cached:
        return APIResponse.ok(cached)

    # Query
    result = await db.execute(
        select(VisaNationalityGuide)
        .join(Nationality)
        .join(VisaType)
        .where(
            and_(
                Nationality.slug == nationality_slug,
                VisaType.slug == visa_type_slug,
            )
        )
    )
    guide = result.scalar_one_or_none()

    if not guide:
        return APIResponse.fail(
            "VISA_GUIDE_NOT_FOUND",
            f"Visa guide for {nationality_slug}/{visa_type_slug} not found",
        )

    response = VisaNationalityGuideResponse(
        id=str(guide.id),
        nationality_id=str(guide.nationality_id),
        visa_type_id=str(guide.visa_type_id),
        specific_requirements=guide.specific_requirements,
        ai_guide=guide.ai_guide,
        created_at=guide.created_at.isoformat(),
        updated_at=guide.updated_at.isoformat(),
    )

    # Cache for 7 days
    await cache.set(cache_key, response.model_dump(), ttl=settings.CACHE_TTL_VISA)

    return APIResponse.ok(response)
