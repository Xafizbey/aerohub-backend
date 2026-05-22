import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class MusicBase(BaseModel):
    title: str = Field(max_length=255)
    title_ru: str | None = None
    title_kk: str | None = None
    title_ky: str | None = None
    artist: str = Field(max_length=255)
    album: str | None = None
    genre: str | None = None
    genre_ru: str | None = None
    genre_kk: str | None = None
    genre_ky: str | None = None
    duration_seconds: int | None = Field(default=None, ge=1)
    year: int | None = None
    language: str | None = Field(default=None, max_length=10)
    is_published: bool = True


class MusicCreate(MusicBase):
    pass


class MusicUpdate(BaseModel):
    title: str | None = None
    title_ru: str | None = None
    title_kk: str | None = None
    title_ky: str | None = None
    artist: str | None = None
    album: str | None = None
    genre: str | None = None
    genre_ru: str | None = None
    genre_kk: str | None = None
    genre_ky: str | None = None
    duration_seconds: int | None = None
    year: int | None = None
    language: str | None = None
    is_published: bool | None = None


class MusicOut(MusicBase):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    cover_path: str | None
    audio_path: str | None
    play_count: int
    created_at: datetime
    updated_at: datetime


class PlaylistCreate(BaseModel):
    name: str = Field(max_length=255)
    name_ru: str | None = None
    name_kk: str | None = None
    name_ky: str | None = None
    description: str | None = None
    description_ru: str | None = None
    description_kk: str | None = None
    description_ky: str | None = None


class PlaylistUpdate(BaseModel):
    name: str | None = None
    name_ru: str | None = None
    name_kk: str | None = None
    name_ky: str | None = None
    description: str | None = None
    description_ru: str | None = None
    description_kk: str | None = None
    description_ky: str | None = None


class PlaylistTrackAdd(BaseModel):
    music_id: uuid.UUID
    position: int = 0


class PlaylistOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    name_ru: str | None
    name_kk: str | None
    name_ky: str | None
    description: str | None
    description_ru: str | None
    description_kk: str | None
    description_ky: str | None
    owner_id: uuid.UUID
    created_at: datetime
    tracks: list["PlaylistTrackOut"] = []


class PlaylistTrackOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    position: int
    music: MusicOut


PlaylistOut.model_rebuild()
