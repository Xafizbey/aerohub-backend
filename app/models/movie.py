import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MovieCategory(Base):
    __tablename__ = "movie_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)

    movies: Mapped[list["Movie"]] = relationship(back_populates="category", lazy="select")


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    title_ru: Mapped[str | None] = mapped_column(String(255))
    title_kk: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    description_ru: Mapped[str | None] = mapped_column(Text)
    description_kk: Mapped[str | None] = mapped_column(Text)
    year: Mapped[int | None] = mapped_column(Integer)
    duration_minutes: Mapped[int | None] = mapped_column(Integer)
    rating: Mapped[float | None] = mapped_column(Float)
    language: Mapped[str | None] = mapped_column(String(10))  # en, ru, kk

    # Media paths (local storage for offline airplane use)
    poster_path: Mapped[str | None] = mapped_column(String(512))
    video_path: Mapped[str | None] = mapped_column(String(512))   # MP4 fallback
    hls_path: Mapped[str | None] = mapped_column(String(512))     # .m3u8 HLS stream

    category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("movie_categories.id", ondelete="SET NULL"), index=True
    )
    category: Mapped["MovieCategory | None"] = relationship(back_populates="movies")

    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_published: Mapped[bool] = mapped_column(default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    view_history: Mapped[list["ViewHistory"]] = relationship(back_populates="movie", lazy="select")

    __table_args__ = (
        Index("ix_movies_title", "title"),
        Index("ix_movies_year", "year"),
        Index("ix_movies_rating", "rating"),
        Index("ix_movies_is_published", "is_published"),
        Index("ix_movies_created_at", "created_at"),
    )
