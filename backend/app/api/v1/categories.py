from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Category
from app.schemas.base import APIResponse
from app.schemas.venue import CategoryResponse
from app.services.cache import cache
from app.config import settings
from typing import List

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=APIResponse[List[CategoryResponse]])
async def list_categories(db: AsyncSession = Depends(get_db)):
    """List all categories (cached 24 hours)"""
    cache_key = "categories:all"

    # Try cache
    cached = await cache.get(cache_key)
    if cached:
        return APIResponse.ok(cached)

    # Query
    result = await db.execute(select(Category).where(Category.is_active == True))
    categories = result.scalars().all()

    cat_list = [
        CategoryResponse(
            id=str(c.id),
            name=c.name,
            slug=c.slug,
            parent_id=str(c.parent_id) if c.parent_id else None,
            display_order=c.display_order,
            is_active=c.is_active,
            created_at=c.created_at.isoformat(),
            updated_at=c.updated_at.isoformat(),
        )
        for c in categories
    ]

    # Cache for 24 hours
    await cache.set(
        cache_key,
        [c.model_dump() for c in cat_list],
        ttl=settings.CACHE_TTL_VENUE,
    )

    return APIResponse.ok(cat_list)


@router.get("/{slug}/", response_model=APIResponse[CategoryResponse])
async def get_category(slug: str, db: AsyncSession = Depends(get_db)):
    """Get single category by slug"""
    cache_key = f"category:{slug}"

    # Try cache
    cached = await cache.get(cache_key)
    if cached:
        return APIResponse.ok(cached)

    # Query
    result = await db.execute(select(Category).where(Category.slug == slug))
    category = result.scalar_one_or_none()

    if not category:
        return APIResponse.fail(
            "CATEGORY_NOT_FOUND", f"Category with slug '{slug}' not found"
        )

    response = CategoryResponse(
        id=str(category.id),
        name=category.name,
        slug=category.slug,
        parent_id=str(category.parent_id) if category.parent_id else None,
        display_order=category.display_order,
        is_active=category.is_active,
        created_at=category.created_at.isoformat(),
        updated_at=category.updated_at.isoformat(),
    )

    # Cache for 24 hours
    await cache.set(cache_key, response.model_dump(), ttl=settings.CACHE_TTL_VENUE)

    return APIResponse.ok(response)
