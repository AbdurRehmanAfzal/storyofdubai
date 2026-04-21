from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import joinedload
from app.database import get_db
from app.models import VisaNationalityGuide, Nationality, VisaType
from app.schemas.base import APIResponse, PaginationMeta
from app.schemas.visa import VisaNationalityGuideResponse
from app.services.cache import cache
from app.config import settings
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/visa-guides", tags=["visa-guides"])

# Enhanced response schemas
class NationalityDetail(BaseModel):
    slug: str
    name: str
    iso_code: str

class VisaTypeDetail(BaseModel):
    slug: str
    name: str
    category: str
    duration_days: Optional[int] = None
    cost_aed: Optional[int] = None
    processing_days: Optional[int] = None
    ai_guide: Optional[str] = None

class VisaNationalityGuideDetailResponse(BaseModel):
    id: str
    nationality: NationalityDetail
    visa_type: VisaTypeDetail
    requirements: Optional[str] = None
    ai_guide: Optional[str] = None
    created_at: str
    updated_at: str

class VisaGuidePath(BaseModel):
    nationality_slug: str
    visa_type_slug: str


@router.get("/", response_model=APIResponse[List[VisaNationalityGuideDetailResponse]])
async def list_visa_guides(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=1000),
    nationality: Optional[str] = None,
    visa_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List visa guides with optional filters and nested details"""
    cache_key = f"visa_guides:list:{page}:{per_page}:{nationality}:{visa_type}"

    # Try cache
    cached = await cache.get(cache_key)
    if cached:
        return APIResponse.ok(cached["data"], cached["meta"])

    # Build query with explicit joins
    query = select(VisaNationalityGuide, Nationality, VisaType).join(
        Nationality, VisaNationalityGuide.nationality_id == Nationality.id
    ).join(VisaType, VisaNationalityGuide.visa_type_id == VisaType.id)

    if nationality:
        query = query.where(Nationality.slug == nationality)
    if visa_type:
        query = query.where(VisaType.slug == visa_type)

    # Get total count
    count_query = select(func.count(VisaNationalityGuide.id))
    if nationality or visa_type:
        count_query = count_query.select_from(VisaNationalityGuide).join(
            Nationality, VisaNationalityGuide.nationality_id == Nationality.id
        ).join(VisaType, VisaNationalityGuide.visa_type_id == VisaType.id)
        if nationality:
            count_query = count_query.where(Nationality.slug == nationality)
        if visa_type:
            count_query = count_query.where(VisaType.slug == visa_type)

    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)

    # Fetch
    result = await db.execute(query)
    rows = result.all()

    guide_list = [
        VisaNationalityGuideDetailResponse(
            id=str(guide.id),
            nationality={
                "slug": nationality_obj.slug,
                "name": nationality_obj.name,
                "iso_code": nationality_obj.iso_code,
            },
            visa_type={
                "slug": visa_type_obj.slug,
                "name": visa_type_obj.name,
                "category": visa_type_obj.category,
                "duration_days": visa_type_obj.duration_days,
                "cost_aed": visa_type_obj.cost_aed,
                "processing_days": visa_type_obj.processing_days,
                "ai_guide": visa_type_obj.ai_guide,
            },
            requirements=guide.requirements,
            ai_guide=guide.ai_guide,
            created_at=guide.created_at.isoformat(),
            updated_at=guide.updated_at.isoformat(),
        )
        for guide, nationality_obj, visa_type_obj in rows
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
    response_model=APIResponse[VisaNationalityGuideDetailResponse],
)
async def get_visa_guide(
    nationality_slug: str, visa_type_slug: str, db: AsyncSession = Depends(get_db)
):
    """Get specific visa guide by nationality and type with nested details"""
    cache_key = f"visa_guide:{nationality_slug}:{visa_type_slug}"

    # Try cache
    cached = await cache.get(cache_key)
    if cached:
        return APIResponse.ok(cached)

    # Query with explicit joins
    result = await db.execute(
        select(VisaNationalityGuide, Nationality, VisaType)
        .join(Nationality, VisaNationalityGuide.nationality_id == Nationality.id)
        .join(VisaType, VisaNationalityGuide.visa_type_id == VisaType.id)
        .where(
            and_(
                Nationality.slug == nationality_slug,
                VisaType.slug == visa_type_slug,
            )
        )
    )
    row = result.one_or_none()

    if not row:
        return APIResponse.fail(
            "VISA_GUIDE_NOT_FOUND",
            f"Visa guide for {nationality_slug}/{visa_type_slug} not found",
        )

    guide, nationality, visa_type = row

    response = VisaNationalityGuideDetailResponse(
        id=str(guide.id),
        nationality={
            "slug": nationality.slug,
            "name": nationality.name,
            "iso_code": nationality.iso_code,
        },
        visa_type={
            "slug": visa_type.slug,
            "name": visa_type.name,
            "category": visa_type.category,
            "duration_days": visa_type.duration_days,
            "cost_aed": visa_type.cost_aed,
            "processing_days": visa_type.processing_days,
            "ai_guide": visa_type.ai_guide,
        },
        requirements=guide.requirements,
        ai_guide=guide.ai_guide,
        created_at=guide.created_at.isoformat(),
        updated_at=guide.updated_at.isoformat(),
    )

    # Cache for 7 days
    await cache.set(cache_key, response.model_dump(), ttl=settings.CACHE_TTL_VISA)

    return APIResponse.ok(response)


@router.get("/page-paths/", response_model=APIResponse[List[VisaGuidePath]])
async def get_visa_guide_page_paths(db: AsyncSession = Depends(get_db)):
    """Get all visa guide page paths for getStaticPaths (Next.js)"""
    cache_key = "visa_guide_page_paths:v1"

    # Try cache (6 hours)
    cached = await cache.get(cache_key)
    if cached:
        return APIResponse.ok(cached)

    # Get all active visa guides with nationality and visa type info
    result = await db.execute(
        select(VisaNationalityGuide, Nationality, VisaType)
        .join(Nationality, VisaNationalityGuide.nationality_id == Nationality.id)
        .join(VisaType, VisaNationalityGuide.visa_type_id == VisaType.id)
        .where(VisaNationalityGuide.is_active == True)
    )

    rows = result.all()
    paths = [
        VisaGuidePath(
            nationality_slug=nationality.slug,
            visa_type_slug=visa_type.slug,
        )
        for guide, nationality, visa_type in rows
    ]

    # Cache for 6 hours (page generation cache)
    await cache.set(cache_key, [p.model_dump() for p in paths], ttl=21600)

    return APIResponse.ok(paths)
