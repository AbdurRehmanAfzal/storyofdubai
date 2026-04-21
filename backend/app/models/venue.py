from sqlalchemy import String, Float, Integer, Boolean, Text, Index, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin
from uuid import UUID


class Area(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "areas"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    meta_description: Mapped[str] = mapped_column(String(160), nullable=True)
    character_tags: Mapped[str] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    venues = relationship("Venue", back_populates="area", cascade="all, delete-orphan")
    properties = relationship("Property", back_populates="area", cascade="all, delete-orphan")


class Category(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    parent_id: Mapped[UUID | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    venues = relationship("Venue", back_populates="category")


class Venue(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "venues"
    __table_args__ = (
        Index("idx_venue_area_category_score", "area_id", "category_id", "composite_score"),
        Index("idx_venue_area_category_active", "area_id", "category_id", "is_active"),
        UniqueConstraint("slug", "area_id", name="unique_venue_slug_area"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    review_count: Mapped[int | None] = mapped_column(Integer, default=0, nullable=True)
    composite_score: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    area_id: Mapped[UUID] = mapped_column(ForeignKey("areas.id", ondelete="CASCADE"), nullable=False)
    category_id: Mapped[UUID] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    last_scraped_at: Mapped[str | None] = mapped_column(String(30), nullable=True)
    affiliate_url_thefork: Mapped[str | None] = mapped_column(String(500), nullable=True)
    affiliate_url_booking: Mapped[str | None] = mapped_column(String(500), nullable=True)
    google_place_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    area = relationship("Area", back_populates="venues")
    category = relationship("Category", back_populates="venues")
