from typing import Optional
from pydantic import BaseModel


class NationalityBase(BaseModel):
    name: str
    slug: str
    iso_code: str


class NationalityResponse(NationalityBase):
    id: str
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class VisaTypeBase(BaseModel):
    name: str
    slug: str
    category: str
    duration_days: Optional[int] = None
    cost_aed: Optional[int] = None
    processing_days: Optional[int] = None
    ai_guide: Optional[str] = None


class VisaTypeResponse(VisaTypeBase):
    id: str
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class VisaNationalityGuideBase(BaseModel):
    nationality_id: str
    visa_type_id: str
    requirements: Optional[str] = None
    ai_guide: Optional[str] = None


class VisaNationalityGuideCreate(VisaNationalityGuideBase):
    pass


class VisaNationalityGuideResponse(VisaNationalityGuideBase):
    id: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
