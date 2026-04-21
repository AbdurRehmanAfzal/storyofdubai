from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import Company
from app.schemas.base import APIResponse
from app.services.cache import cache
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/sectors", tags=["sectors"])


class SectorResponse(BaseModel):
    id: str
    slug: str
    name: str


@router.get("/", response_model=APIResponse[List[SectorResponse]])
async def list_sectors(db: AsyncSession = Depends(get_db)):
    """List all sectors from companies"""
    cache_key = "sectors:list:v1"

    # Try cache
    cached = await cache.get(cache_key)
    if cached:
        return APIResponse.ok(cached)

    # Get distinct sectors where companies are active
    result = await db.execute(
        select(Company.sector)
        .where(Company.is_active == True)
        .distinct()
        .order_by(Company.sector)
    )
    sectors = result.scalars().all()

    # Convert to response format
    response = [
        SectorResponse(
            id=sector.lower().replace(" ", "-"),
            slug=sector.lower().replace(" ", "-"),
            name=sector,
        )
        for sector in sectors
        if sector  # Filter out None values
    ]

    # Cache for 24 hours
    await cache.set(cache_key, [r.model_dump() for r in response], ttl=86400)

    return APIResponse.ok(response)
