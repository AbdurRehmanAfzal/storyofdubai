from sqlalchemy import String, Integer, Text, Index, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Nationality(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "nationalities"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    iso_code: Mapped[str] = mapped_column(String(3), nullable=False, unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False, index=True)

    visa_guides = relationship("VisaNationalityGuide", back_populates="nationality")


class VisaType(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "visa_types"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )  # employment, investor, tourist, freelancer, retirement
    duration_days: Mapped[int] = mapped_column(Integer, nullable=True)
    cost_aed: Mapped[int] = mapped_column(Integer, nullable=True)
    processing_days: Mapped[int] = mapped_column(Integer, nullable=True)
    ai_guide: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False, index=True)

    visa_guides = relationship("VisaNationalityGuide", back_populates="visa_type")


class VisaNationalityGuide(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "visa_nationality_guides"
    __table_args__ = (
        UniqueConstraint("nationality_id", "visa_type_id", name="unique_nationality_visa_type"),
    )

    nationality_id: Mapped[str] = mapped_column(String(36), ForeignKey("nationalities.id", ondelete="CASCADE"), nullable=False)
    visa_type_id: Mapped[str] = mapped_column(String(36), ForeignKey("visa_types.id", ondelete="CASCADE"), nullable=False)
    specific_requirements: Mapped[str] = mapped_column(Text, nullable=True)
    ai_guide: Mapped[str] = mapped_column(Text, nullable=True)
    last_updated: Mapped[str] = mapped_column(String(30), nullable=True)

    nationality = relationship("Nationality", back_populates="visa_guides")
    visa_type = relationship("VisaType", back_populates="visa_guides")
