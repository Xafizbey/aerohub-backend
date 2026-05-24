import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MusicCategory(Base):
    __tablename__ = "music_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name_ru: Mapped[str | None] = mapped_column(String(100))
    name_kk: Mapped[str | None] = mapped_column(String(100))
    name_ky: Mapped[str | None] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    description_ru: Mapped[str | None] = mapped_column(Text)
    description_kk: Mapped[str | None] = mapped_column(Text)
    description_ky: Mapped[str | None] = mapped_column(Text)
    icon: Mapped[str | None] = mapped_column(String(20))

    tracks: Mapped[list["Music"]] = relationship(back_populates="category", lazy="select")

    def __str__(self) -> str:
        return self.name


class Music(Base):
    __tablename__ = "music"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    artist: Mapped[str] = mapped_column(String(255), nullable=False)
    album: Mapped[str | None] = mapped_column(String(255))
    genre: Mapped[str | None] = mapped_column(String(100))
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
    year: Mapped[int | None] = mapped_column(Integer)
    language: Mapped[str | None] = mapped_column(String(10))

    cover_path: Mapped[str | None] = mapped_column(String(512))
    audio_path: Mapped[str | None] = mapped_column(String(512))

    category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("music_categories.id", ondelete="SET NULL"), index=True
    )
    category: Mapped["MusicCategory | None"] = relationship(back_populates="tracks")

    play_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_published: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Stub attributes for sqladmin FileField
    cover_upload = None
    audio_upload = None

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    play_history: Mapped[list["PlayHistory"]] = relationship(back_populates="music", lazy="select", passive_deletes=True)
    playlist_tracks: Mapped[list["PlaylistTrack"]] = relationship(
        back_populates="music", lazy="select", passive_deletes=True
    )

    __table_args__ = (
        Index("ix_music_artist", "artist"),
        Index("ix_music_genre", "genre"),
        Index("ix_music_is_published", "is_published"),
    )


class Playlist(Base):
    __tablename__ = "playlists"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    name_ru: Mapped[str | None] = mapped_column(String(255))
    name_kk: Mapped[str | None] = mapped_column(String(255))
    name_ky: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    description_ru: Mapped[str | None] = mapped_column(Text)
    description_kk: Mapped[str | None] = mapped_column(Text)
    description_ky: Mapped[str | None] = mapped_column(Text)
    banner_path: Mapped[str | None] = mapped_column(String(512))

    # Stub for sqladmin FileField
    banner_upload = None

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    tracks: Mapped[list["PlaylistTrack"]] = relationship(
        back_populates="playlist", order_by="PlaylistTrack.position", lazy="select",
        cascade="all, delete-orphan",
    )


class PlaylistTrack(Base):
    __tablename__ = "playlist_tracks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    playlist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("playlists.id", ondelete="CASCADE"), index=True
    )
    music_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("music.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    playlist: Mapped["Playlist"] = relationship(back_populates="tracks")
    music: Mapped["Music"] = relationship(back_populates="playlist_tracks")
