import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class TrackView(BaseModel):
    movie_id: uuid.UUID
    watched_seconds: int = Field(ge=0, default=0)
    completed: bool = False
    seat_number: str | None = None


class TrackPlay(BaseModel):
    music_id: uuid.UUID
    played_seconds: int = Field(ge=0, default=0)
    completed: bool = False


class ViewHistoryOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    movie_id: uuid.UUID
    watched_seconds: int
    completed: bool
    seat_number: str | None
    viewed_at: datetime


class PlayHistoryOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    music_id: uuid.UUID
    played_seconds: int
    completed: bool
    played_at: datetime


class MovieStats(BaseModel):
    movie_id: uuid.UUID
    title: str
    total_views: int
    unique_viewers: int
    completion_rate: float


class MusicStats(BaseModel):
    music_id: uuid.UUID
    title: str
    artist: str
    total_plays: int
    unique_listeners: int
    completion_rate: float


class GenreStats(BaseModel):
    genre_id: int
    genre_name: str
    total_views: int
    unique_movies: int
    completion_rate: float
