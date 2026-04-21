from fastapi import APIRouter
from app.api.v1 import (
    venues,
    areas,
    categories,
    properties,
    visa_guides,
    page_paths,
    nationalities,
    sectors,
)

router = APIRouter()

# Routers already have their own prefixes in the router definitions
router.include_router(venues.router)
router.include_router(areas.router)
router.include_router(categories.router)
router.include_router(properties.router)
router.include_router(visa_guides.router)
router.include_router(page_paths.router)
router.include_router(nationalities.router)
router.include_router(sectors.router)
