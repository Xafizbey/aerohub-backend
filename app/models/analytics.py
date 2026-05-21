import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ViewHistory(Base):
    __tablename__ = "view_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )
    movie_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("movies.id", ondelete="CASCADE"), index=True
    )
    watched_seconds: Mapped[int] = mapped_column(Integer, default=0)
    completed: Mapped[bool] = mapped_column(default=False)
    seat_number: Mapped[str | None] = mapped_column(String(10))

    viewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="view_history")
    movie: Mapped["Movie"] = relationship(back_populates="view_history")

    __table_args__ = (
        Index("ix_view_history_viewed_at", "viewed_at"),
        Index("ix_view_history_user_movie", "user_id", "movie_id"),
    )


class PlayHistory(Base):
    __tablename__ = "play_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )
    music_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("music.id", ondelete="CASCADE"), index=True
    )
    played_seconds: Mapped[int] = mapped_column(Integer, default=0)
    completed: Mapped[bool] = mapped_column(default=False)

    played_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="play_history")
    music: Mapped["Music"] = relationship(back_populates="play_history")

    __table_args__ = (
        Index("ix_play_history_played_at", "played_at"),
        Index("ix_play_history_user_music", "user_id", "music_id"),
    )
