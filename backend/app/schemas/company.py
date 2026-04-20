from typing import Optional
from pydantic import BaseModel


class CompanyBase(BaseModel):
    name: str
    slug: str
    sector: str
    registration_year: Optional[int] = None
    freezone: Optional[str] = None
    is_mainland: bool = False
    employee_count_range: Optional[str] = None
    website: Optional[str] = None
    ai_summary: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyResponse(CompanyBase):
    id: str
    is_active: bool
    last_scraped_at: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class CompanyListItem(BaseModel):
    id: str
    name: str
    slug: str
    sector: str
    employee_count_range: Optional[str] = None

    class Config:
        from_attributes = True
