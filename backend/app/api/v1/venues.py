from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import joinedload
from app.database import get_db
from app.models import Venue, Area, Category
from app.schemas.base import APIResponse, PaginationMeta
from app.schemas.venue import (
    VenueResponse,
    VenueListItem,
    AreaSlugName,
    CategorySlugName,
)
from app.services.cache import cache
from app.config import settings
from typing import List, Optional

router = APIRouter(prefix="/venues", tags=["venues"])


@router.get("/", response_model=APIResponse[List[VenueListItem]])
async def list_venues(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    area: Optional[str] = None,
    category: Optional[str] = None,
    min_score: Optional[float] = None,
    ordering: str = "-composite_score",
    db: AsyncSession = Depends(get_db),
):
    """List venues with pagination and filters"""
    # Build cache key
    cache_key = f"venues:list:{page}:{per_page}:{area}:{category}:{min_score}:{ordering}"

    # Try cache first
    cached = await cache.get(cache_key)
    if cached:
        return APIResponse.ok(cached["data"], cached["meta"])

    # Build base query with eager loading to prevent N+1
    query = select(Venue).options(joinedload(Venue.area), joinedload(Venue.category)).where(Venue.is_active == True)

    if area:
        query = query.join(Area).where(Area.slug == area)
    if category:
        query = query.join(Category).where(Category.slug == category)
    if min_score is not None:
        query = query.where(Venue.composite_score >= min_score)

    # Get total count
    count_query = select(func.count(Venue.id)).where(Venue.is_active == True)
    if area:
        count_query = count_query.join(Area).where(Area.slug == area)
    if category:
        count_query = count_query.join(Category).where(Category.slug == category)
    if min_score is not None:
        count_query = count_query.where(Venue.composite_score >= min_score)

    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Ordering
    if ordering.startswith("-"):
        order_field = getattr(Venue, ordering[1:], Venue.composite_score)
        query = query.order_by(order_field.desc())
    else:
        order_field = getattr(Venue, ordering, Venue.composite_score)
        query = query.order_by(order_field)

    # Pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)

    # Fetch results
    result = await db.execute(query)
    venues = result.unique().scalars().all()

    # Format response
    venue_list = [
        VenueListItem(
            id=str(v.id),
            name=v.name,
            slug=v.slug,
            composite_score=v.composite_score,
            rating=v.rating,
            review_count=v.review_count,
            area=AreaSlugName(slug=v.area.slug, name=v.area.name),
            category=CategorySlugName(slug=v.category.slug, name=v.category.name),
        )
        for v in venues
    ]

    meta = PaginationMeta(
        total=total,
        page=page,
        per_page=per_page,
        has_next=(page * per_page) < total,
        has_prev=page > 1,
    )

    # Cache result
    await cache.set(
        cache_key,
        {"data": [v.model_dump() for v in venue_list], "meta": meta.model_dump()},
        ttl=settings.CACHE_TTL_RANKINGS,
    )

    return APIResponse.ok(venue_list, meta)


@router.get("/{slug}/", response_model=APIResponse[VenueResponse])
async def get_venue(slug: str, db: AsyncSession = Depends(get_db)):
    """Get single venue by slug with area and category"""
    cache_key = f"venue:{slug}"

    # Try cache
    cached = await cache.get(cache_key)
    if cached:
        return APIResponse.ok(cached)

    # Query venue
    result = await db.execute(
        select(Venue).where(Venue.slug == slug)
    )
    venue = result.scalar_one_or_none()

    if not venue:
        return APIResponse.fail(
            "VENUE_NOT_FOUND", f"Venue with slug '{slug}' not found"
        )

    # Query area and category relationships explicitly
    area_result = await db.execute(
        select(Area).where(Area.id == venue.area_id)
    )
    area_obj = area_result.scalar_one()

    category_result = await db.execute(
        select(Category).where(Category.id == venue.category_id)
    )
    category_obj = category_result.scalar_one()

    response = VenueResponse(
        id=str(venue.id),
        name=venue.name,
        slug=venue.slug,
        description=venue.description,
        address=venue.address,
        phone=venue.phone,
        website=venue.website,
        email=venue.email,
        rating=venue.rating,
        review_count=venue.review_count,
        composite_score=venue.composite_score,
        google_place_id=venue.google_place_id,
        is_active=venue.is_active,
        created_at=venue.created_at.isoformat(),
        updated_at=venue.updated_at.isoformat(),
        area=AreaSlugName(slug=area_obj.slug, name=area_obj.name),
        category=CategorySlugName(slug=category_obj.slug, name=category_obj.name),
    )

    # TODO: Cache the response with complex objects serialized properly
    # For now, skip caching to avoid losing relationship data
    # await cache.set(cache_key, response.model_dump(), ttl=settings.CACHE_TTL_VENUE)

    return APIResponse.ok(response)


@router.get(
    "/area/{area_slug}/category/{category_slug}/",
    response_model=APIResponse[List[VenueListItem]],
)
async def get_venues_for_page(
    area_slug: str, category_slug: str, db: AsyncSession = Depends(get_db)
):
    """Get top 20 venues for a page (aggressive caching)"""
    cache_key = f"page:venues:{area_slug}:{category_slug}"

    # Try cache (6 hours for page generation)
    cached = await cache.get(cache_key)
    if cached:
        return APIResponse.ok(cached)

    # Query top 20
    result = await db.execute(
        select(Venue)
        .options(joinedload(Venue.area), joinedload(Venue.category))
        .join(Area)
        .join(Category)
        .where(
            and_(
                Venue.is_active == True,
                Area.slug == area_slug,
                Category.slug == category_slug,
            )
        )
        .order_by(Venue.composite_score.desc())
        .limit(20)
    )
    venues = result.unique().scalars().all()

    venue_list = [
        VenueListItem(
            id=str(v.id),
            name=v.name,
            slug=v.slug,
            composite_score=v.composite_score,
            rating=v.rating,
            review_count=v.review_count,
            area=AreaSlugName(slug=v.area.slug, name=v.area.name),
            category=CategorySlugName(slug=v.category.slug, name=v.category.name),
        )
        for v in venues
    ]

    # Cache with 6-hour TTL for page generation
    await cache.set(
        cache_key,
        [v.model_dump() for v in venue_list],
        ttl=settings.CACHE_TTL_PAGE_PATHS,
    )

    return APIResponse.ok(venue_list, None)
