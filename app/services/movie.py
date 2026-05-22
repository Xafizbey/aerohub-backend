import math
import uuid
import logging

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.models.movie import Movie, MovieCategory
from app.schemas.movie import CategoryCreate, MovieCreate, MovieUpdate
from app.schemas.common import PaginatedResponse

logger = logging.getLogger(__name__)


# ── Categories ──────────────────────────────────────────────────────────────

async def create_category(data: CategoryCreate, db: AsyncSession) -> MovieCategory:
    exists = await db.execute(select(MovieCategory).where(MovieCategory.slug == data.slug))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Category slug already exists")
    cat = MovieCategory(**data.model_dump())
    db.add(cat)
    await db.flush()
    await db.refresh(cat)
    return cat


async def list_categories(db: AsyncSession) -> list[MovieCategory]:
    result = await db.execute(select(MovieCategory).order_by(MovieCategory.name))
    return list(result.scalars().all())


# ── Movies ───────────────────────────────────────────────────────────────────

async def create_movie(data: MovieCreate, db: AsyncSession) -> Movie:
    movie = Movie(**data.model_dump())
    db.add(movie)
    await db.flush()
    await db.refresh(movie, ["category"])
    return movie


async def get_movie(movie_id: uuid.UUID, db: AsyncSession) -> Movie:
    result = await db.execute(
        select(Movie)
        .options(selectinload(Movie.category))
        .where(Movie.id == movie_id)
    )
    movie = result.scalar_one_or_none()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


async def list_movies(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    category_id: int | None = None,
    language: str | None = None,
    published_only: bool = True,
) -> PaginatedResponse:
    stmt = select(Movie).options(selectinload(Movie.category))

    if published_only:
        stmt = stmt.where(Movie.is_published.is_(True))
    if category_id:
        stmt = stmt.where(Movie.category_id == category_id)
    if language:
        stmt = stmt.where(Movie.language == language)
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            or_(
                Movie.title.ilike(pattern),
                Movie.title_ru.ilike(pattern),
                Movie.title_kk.ilike(pattern),
                Movie.title_ky.ilike(pattern),
                Movie.description.ilike(pattern),
            )
        )

    count_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = count_result.scalar_one()

    stmt = stmt.order_by(Movie.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = list(result.scalars().all())

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


async def update_movie(movie_id: uuid.UUID, data: MovieUpdate, db: AsyncSession) -> Movie:
    movie = await get_movie(movie_id, db)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(movie, field, value)
    await db.flush()
    await db.refresh(movie, ["category"])
    return movie


async def delete_movie(movie_id: uuid.UUID, db: AsyncSession) -> None:
    movie = await get_movie(movie_id, db)
    await db.delete(movie)


async def increment_view_count(movie_id: uuid.UUID, db: AsyncSession) -> None:
    await db.execute(
        update(Movie).where(Movie.id == movie_id).values(view_count=Movie.view_count + 1)
    )
