from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.database import get_db
from app.models import Property, Area
from app.schemas.base import APIResponse, PaginationMeta
from app.schemas.property import PropertyResponse, PropertyListItem
from app.services.cache import cache
from app.config import settings
from typing import List, Optional

router = APIRouter(prefix="/properties", tags=["properties"])


@router.get("/", response_model=APIResponse[List[PropertyListItem]])
async def list_properties(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    area: Optional[str] = None,
    bedrooms: Optional[int] = None,
    price_bucket: Optional[str] = None,
    property_type: Optional[str] = None,
    ordering: str = "-composite_score",
    db: AsyncSession = Depends(get_db),
):
    """List properties with pagination and filters"""
    cache_key = f"properties:list:{page}:{per_page}:{area}:{bedrooms}:{price_bucket}:{property_type}:{ordering}"

    # Try cache
    cached = await cache.get(cache_key)
    if cached:
        return APIResponse.ok(cached["data"], cached["meta"])

    # Build query
    query = select(Property).where(Property.is_active == True)

    if area:
        query = query.join(Area).where(Area.slug == area)
    if bedrooms is not None:
        query = query.where(Property.bedrooms == bedrooms)
    if price_bucket:
        query = query.where(Property.price_bucket == price_bucket)
    if property_type:
        query = query.where(Property.property_type == property_type)

    # Get total count
    count_result = await db.execute(select(func.count(Property.id)).select_from(query))
    total = count_result.scalar() or 0

    # Ordering
    if ordering.startswith("-"):
        order_field = getattr(Property, ordering[1:], Property.composite_score)
        query = query.order_by(order_field.desc())
    else:
        order_field = getattr(Property, ordering, Property.composite_score)
        query = query.order_by(order_field)

    # Pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)

    # Fetch results
    result = await db.execute(query)
    properties = result.scalars().all()

    property_list = [
        PropertyListItem(
            id=str(p.id),
            title=p.title,
            slug=p.slug,
            bedrooms=p.bedrooms,
            price_aed=p.price_aed,
            price_bucket=p.price_bucket,
            composite_score=p.composite_score,
            affiliate_url=p.affiliate_url,
        )
        for p in properties
    ]

    meta = PaginationMeta(
        total=total,
        page=page,
        per_page=per_page,
        has_next=(page * per_page) < total,
        has_prev=page > 1,
    )

    # Cache
    await cache.set(
        cache_key,
        {"data": [p.model_dump() for p in property_list], "meta": meta.model_dump()},
        ttl=settings.CACHE_TTL_RANKINGS,
    )

    return APIResponse.ok(property_list, meta)


@router.get("/{slug}/", response_model=APIResponse[PropertyResponse])
async def get_property(slug: str, db: AsyncSession = Depends(get_db)):
    """Get single property by slug"""
    cache_key = f"property:{slug}"

    # Try cache
    cached = await cache.get(cache_key)
    if cached:
        return APIResponse.ok(cached)

    # Query
    result = await db.execute(select(Property).where(Property.slug == slug))
    prop = result.scalar_one_or_none()

    if not prop:
        return APIResponse.fail(
            "PROPERTY_NOT_FOUND", f"Property with slug '{slug}' not found"
        )

    response = PropertyResponse(
        id=str(prop.id),
        title=prop.title,
        slug=prop.slug,
        area_id=str(prop.area_id),
        bedrooms=prop.bedrooms,
        bathrooms=prop.bathrooms,
        size_sqft=prop.size_sqft,
        price_aed=prop.price_aed,
        price_bucket=prop.price_bucket,
        property_type=prop.property_type,
        developer_id=str(prop.developer_id) if prop.developer_id else None,
        composite_score=prop.composite_score,
        description=prop.description,
        affiliate_url=prop.affiliate_url,
        is_active=prop.is_active,
        last_scraped_at=prop.last_scraped_at,
        created_at=prop.created_at.isoformat(),
        updated_at=prop.updated_at.isoformat(),
    )

    # Cache for 24 hours
    await cache.set(cache_key, response.model_dump(), ttl=settings.CACHE_TTL_VENUE)

    return APIResponse.ok(response)
