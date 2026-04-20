from typing import Optional
from pydantic import BaseModel


class DeveloperBase(BaseModel):
    name: str
    slug: str
    established_year: Optional[int] = None
    total_projects: int = 0


class DeveloperResponse(DeveloperBase):
    id: str
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class PropertyBase(BaseModel):
    title: str
    slug: str
    area_id: str
    bedrooms: int
    bathrooms: Optional[int] = None
    size_sqft: Optional[float] = None
    price_aed: int
    price_bucket: str
    property_type: str
    developer_id: Optional[str] = None
    composite_score: float
    description: Optional[str] = None
    affiliate_url: Optional[str] = None
    last_scraped_at: Optional[str] = None


class PropertyCreate(PropertyBase):
    pass


class PropertyResponse(PropertyBase):
    id: str
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class PropertyListItem(BaseModel):
    id: str
    title: str
    slug: str
    bedrooms: int
    price_aed: int
    price_bucket: str
    composite_score: float
    affiliate_url: Optional[str] = None

    class Config:
        from_attributes = True
