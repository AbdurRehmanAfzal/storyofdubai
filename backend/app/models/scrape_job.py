from sqlalchemy import String, Integer, Text, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class ScrapeJob(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "scrape_jobs"
    __table_args__ = (
        Index("idx_scrape_job_scraper_name", "scraper_name"),
    )

    scraper_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    started_at: Mapped[str] = mapped_column(String(30), nullable=False)
    completed_at: Mapped[str] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # running, completed, failed
    records_collected: Mapped[int] = mapped_column(Integer, default=0)
    records_failed: Mapped[int] = mapped_column(Integer, default=0)
    error_log: Mapped[str] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict] = mapped_column(JSON, nullable=True)
