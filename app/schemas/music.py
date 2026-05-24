import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class MusicCategoryBase(BaseModel):
    name: str = Field(max_length=100)
    name_ru: str | None = None
    name_kk: str | None = None
    name_ky: str | None = None
    slug: str = Field(max_length=100)
    description: str | None = None
    description_ru: str | None = None
    description_kk: str | None = None
    description_ky: str | None = None
    icon: str | None = None


class MusicCategoryCreate(MusicCategoryBase):
    pass


class MusicCategoryOut(MusicCategoryBase):
    model_config = {"from_attributes": True}
    id: int


class MusicBase(BaseModel):
    title: str = Field(max_length=255)
    artist: str = Field(max_length=255)
    album: str | None = None
    genre: str | None = None
    duration_seconds: int | None = Field(default=None, ge=1)
    year: int | None = None
    language: str | None = Field(default=None, max_length=10)
    category_id: int | None = None
    is_published: bool = True


class MusicCreate(MusicBase):
    playlist_id: uuid.UUID | None = None


class MusicUpdate(BaseModel):
    title: str | None = None
    artist: str | None = None
    album: str | None = None
    genre: str | None = None
    duration_seconds: int | None = None
    year: int | None = None
    language: str | None = None
    category_id: int | None = None
    is_published: bool | None = None
    playlist_id: uuid.UUID | None = None


class MusicOut(MusicBase):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    cover_path: str | None
    audio_path: str | None
    play_count: int
    category: MusicCategoryOut | None = None
    created_at: datetime
    updated_at: datetime


class PlayRecordCreate(BaseModel):
    played_seconds: int = 0
    completed: bool = False


class PlaylistCreate(BaseModel):
    name: str = Field(max_length=255)
    name_ru: str | None = None
    name_kk: str | None = None
    name_ky: str | None = None
    description: str | None = None
    description_ru: str | None = None
    description_kk: str | None = None
    description_ky: str | None = None
    banner_path: str | None = None


class PlaylistUpdate(BaseModel):
    name: str | None = None
    name_ru: str | None = None
    name_kk: str | None = None
    name_ky: str | None = None
    description: str | None = None
    description_ru: str | None = None
    description_kk: str | None = None
    description_ky: str | None = None
    banner_path: str | None = None


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
    banner_path: str | None
    created_at: datetime
    tracks: list["PlaylistTrackOut"] = []


class PlaylistTrackOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    position: int
    music: MusicOut


PlaylistOut.model_rebuild()
