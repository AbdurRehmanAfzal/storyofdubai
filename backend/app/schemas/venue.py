from typing import Optional, List
from pydantic import BaseModel, Field


class AreaBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    meta_description: Optional[str] = Field(None, max_length=160)
    character_tags: Optional[str] = None


class AreaCreate(AreaBase):
    pass


class AreaResponse(AreaBase):
    id: str
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str
    slug: str
    parent_id: Optional[str] = None
    display_order: int = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: str
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class AreaSlugName(BaseModel):
    slug: str
    name: str


class CategorySlugName(BaseModel):
    slug: str
    name: str


class VenueBase(BaseModel):
    name: str
    slug: str
    area_id: str
    category_id: str
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    rating: Optional[float] = None
    review_count: int = 0
    composite_score: float
    price_tier: Optional[int] = None
    google_place_id: Optional[str] = None
    affiliate_url: Optional[str] = None
    last_scraped_at: Optional[str] = None


class VenueCreate(VenueBase):
    pass


class VenueResponse(VenueBase):
    id: str
    google_rating: Optional[float] = None
    ai_summary: Optional[str] = None
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class VenueListItem(BaseModel):
    id: str
    name: str
    slug: str
    composite_score: float
    google_rating: Optional[float] = None
    review_count: int
    price_tier: Optional[int] = None
    area: AreaSlugName
    category: CategorySlugName
    affiliate_url: Optional[str] = None

    class Config:
        from_attributes = True
