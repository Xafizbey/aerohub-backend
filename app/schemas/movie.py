import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(max_length=100)
    slug: str = Field(max_length=100)
    description: str | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryOut(CategoryBase):
    model_config = {"from_attributes": True}
    id: int


class MovieBase(BaseModel):
    title: str = Field(max_length=255)
    title_ru: str | None = None
    title_kk: str | None = None
    description: str | None = None
    description_ru: str | None = None
    description_kk: str | None = None
    year: int | None = Field(default=None, ge=1900, le=2100)
    duration_minutes: int | None = Field(default=None, ge=1)
    rating: float | None = Field(default=None, ge=0, le=10)
    language: str | None = Field(default=None, max_length=10)
    category_id: int | None = None
    is_published: bool = True


class MovieCreate(MovieBase):
    pass


class MovieUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    title_ru: str | None = None
    title_kk: str | None = None
    description: str | None = None
    description_ru: str | None = None
    description_kk: str | None = None
    year: int | None = None
    duration_minutes: int | None = None
    rating: float | None = None
    language: str | None = None
    category_id: int | None = None
    is_published: bool | None = None


class MovieOut(MovieBase):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    poster_path: str | None
    video_path: str | None
    hls_path: str | None
    view_count: int
    category: CategoryOut | None
    created_at: datetime
    updated_at: datetime


class MovieListOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    title: str
    title_ru: str | None
    title_kk: str | None
    year: int | None
    duration_minutes: int | None
    rating: float | None
    language: str | None
    poster_path: str | None
    hls_path: str | None
    view_count: int
    category: CategoryOut | None
