from sqlalchemy import String, Float, Integer, Boolean, Text, Index, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Developer(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "developers"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    established_year: Mapped[int] = mapped_column(Integer, nullable=True)
    total_projects: Mapped[int] = mapped_column(Integer, default=0)
    ai_summary: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    properties = relationship("Property", back_populates="developer")


class Property(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "properties"
    __table_args__ = (
        Index("idx_property_area_bedrooms_price", "area_id", "bedrooms", "price_bucket"),
        Index("idx_property_area_type_score", "area_id", "property_type", "composite_score"),
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    area_id: Mapped[str] = mapped_column(String(36), ForeignKey("areas.id", ondelete="CASCADE"), nullable=False)
    bedrooms: Mapped[int] = mapped_column(Integer, nullable=False)
    bathrooms: Mapped[int] = mapped_column(Integer, nullable=True)
    size_sqft: Mapped[float] = mapped_column(Float, nullable=True)
    price_aed: Mapped[int] = mapped_column(Integer, nullable=False)
    price_bucket: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )  # under-50k, 50k-100k, 100k-200k, 200k-plus
    property_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )  # apartment, villa, studio, penthouse, townhouse
    developer_id: Mapped[str] = mapped_column(String(36), ForeignKey("developers.id", ondelete="SET NULL"), nullable=True)
    composite_score: Mapped[float] = mapped_column(Float, default=0, index=True)
    affiliate_url: Mapped[str] = mapped_column(String(500), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    last_scraped_at: Mapped[str] = mapped_column(String(30), nullable=True)

    area = relationship("Area", back_populates="properties")
    developer = relationship("Developer", back_populates="properties")
