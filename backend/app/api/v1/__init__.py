from fastapi import APIRouter
from app.api.v1 import venues, areas, categories, properties, visa_guides, page_paths

router = APIRouter()

router.include_router(venues.router, prefix="/venues", tags=["venues"])
router.include_router(areas.router, prefix="/areas", tags=["areas"])
router.include_router(categories.router, prefix="/categories", tags=["categories"])
router.include_router(properties.router, prefix="/properties", tags=["properties"])
router.include_router(visa_guides.router, prefix="/visa-guides", tags=["visa-guides"])
router.include_router(page_paths.router, prefix="/page-paths", tags=["page-paths"])
