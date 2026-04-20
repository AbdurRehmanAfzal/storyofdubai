from sqlalchemy import String, Integer, Text, Index, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Company(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "companies"
    __table_args__ = (
        Index("idx_company_sector_active", "sector", "is_active"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    sector: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    registration_year: Mapped[int] = mapped_column(Integer, nullable=True)
    freezone: Mapped[str] = mapped_column(String(100), nullable=True)
    is_mainland: Mapped[bool] = mapped_column(Boolean, default=False)
    employee_count_range: Mapped[str] = mapped_column(String(50), nullable=True)
    ai_summary: Mapped[str] = mapped_column(Text, nullable=True)
    website: Mapped[str] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    last_scraped_at: Mapped[str] = mapped_column(String(30), nullable=True)
