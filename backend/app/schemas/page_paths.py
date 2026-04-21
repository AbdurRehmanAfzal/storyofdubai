from pydantic import BaseModel


class VenueAreaPath(BaseModel):
    category_slug: str
    area_slug: str


class PropertyPath(BaseModel):
    area_slug: str
    bedrooms: int
    price_bucket: str
    slug: str


class VisaGuidePath(BaseModel):
    nationality_slug: str
    visa_type_slug: str
