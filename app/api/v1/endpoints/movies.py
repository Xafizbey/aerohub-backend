import uuid

from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.movie import CategoryCreate, CategoryOut, MovieCreate, MovieListOut, MovieOut, MovieUpdate
from app.services.auth import require_admin
from app.services import movie as movie_svc
from app.services.media import upload_poster, register_hls_path

router = APIRouter(prefix="/movies", tags=["Movies"])


# ── Categories ───────────────────────────────────────────────────────────────

@router.get("/categories", response_model=list[CategoryOut])
async def get_categories(db: AsyncSession = Depends(get_db)):
    return await movie_svc.list_categories(db)


@router.post("/categories", response_model=CategoryOut, status_code=201)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    return await movie_svc.create_category(data, db)


# ── Movies ────────────────────────────────────────────────────────────────────

@router.get("", response_model=PaginatedResponse)
async def list_movies(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    category_id: int | None = Query(None),
    language: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    result = await movie_svc.list_movies(
        db, page=page, page_size=page_size,
        search=search, category_id=category_id, language=language,
    )
    result.items = [MovieListOut.model_validate(m) for m in result.items]
    return result


@router.post("", response_model=MovieOut, status_code=201)
async def create_movie(
    data: MovieCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    return await movie_svc.create_movie(data, db)


@router.get("/{movie_id}", response_model=MovieOut)
async def get_movie(
    movie_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await movie_svc.get_movie(movie_id, db)


@router.patch("/{movie_id}", response_model=MovieOut)
async def update_movie(
    movie_id: uuid.UUID,
    data: MovieUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    return await movie_svc.update_movie(movie_id, data, db)


@router.delete("/{movie_id}", response_model=MessageResponse)
async def delete_movie(
    movie_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    await movie_svc.delete_movie(movie_id, db)
    return MessageResponse(message="Movie deleted")


# ── Media uploads (crew only) ─────────────────────────────────────────────────

@router.post("/{movie_id}/poster", response_model=MovieOut)
async def upload_movie_poster(
    movie_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    movie = await movie_svc.get_movie(movie_id, db)
    movie.poster_path = await upload_poster(file)
    await db.flush()
    await db.refresh(movie, ["category"])
    return movie


@router.post("/{movie_id}/hls", response_model=MovieOut)
async def set_movie_hls(
    movie_id: uuid.UUID,
    hls_path: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    movie = await movie_svc.get_movie(movie_id, db)
    movie.hls_path = register_hls_path(hls_path)
    await db.flush()
    await db.refresh(movie, ["category"])
    return movie
