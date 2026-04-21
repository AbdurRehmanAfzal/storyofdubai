from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Nationality
from app.schemas.base import APIResponse
from app.schemas.visa import NationalityResponse
from app.services.cache import cache
from typing import List

router = APIRouter(prefix="/nationalities", tags=["nationalities"])


@router.get("/", response_model=APIResponse[List[NationalityResponse]])
async def list_nationalities(db: AsyncSession = Depends(get_db)):
    """List all nationalities with visa guides"""
    cache_key = "nationalities:list:v1"

    # Try cache
    cached = await cache.get(cache_key)
    if cached:
        return APIResponse.ok(cached)

    # Query
    result = await db.execute(
        select(Nationality).where(Nationality.is_active == True)
    )
    nationalities = result.scalars().all()

    response = [
        NationalityResponse(
            id=str(n.id),
            name=n.name,
            slug=n.slug,
            iso_code=n.iso_code,
            is_active=n.is_active,
            created_at=n.created_at.isoformat(),
            updated_at=n.updated_at.isoformat(),
        )
        for n in nationalities
    ]

    # Cache for 24 hours
    await cache.set(cache_key, [r.model_dump() for r in response], ttl=86400)

    return APIResponse.ok(response)
