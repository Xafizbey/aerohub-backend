import uuid

from fastapi import APIRouter, Depends, Form, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.movie import CategoryCreate, CategoryOut, MovieCreate, MovieListOut, MovieOut, MovieUpdate
from app.services.auth import require_admin
from app.services import movie as movie_svc
from app.services.media import upload_poster, register_hls_path
from app.utils.i18n import apply_lang_to_category, apply_lang_to_movie, apply_lang_to_movie_list, resolve_lang

router = APIRouter(prefix="/movies", tags=["Movies"])


# ── Categories ───────────────────────────────────────────────────────────────

@router.get(
    "/categories",
    response_model=list[CategoryOut],
    summary="List all movie categories",
)
async def get_categories(
    lang: str | None = Query(None, description="UI language: en | ru | kk | ky"),
    db: AsyncSession = Depends(get_db),
):
    """Return all categories ordered by name. Pass `lang` to get localised name/description."""
    cats = await movie_svc.list_categories(db)
    if lang and lang != "en":
        resolved = resolve_lang(lang)
        return [apply_lang_to_category(c, resolved) for c in cats]
    return cats


@router.post(
    "/categories",
    response_model=CategoryOut,
    status_code=201,
    summary="Create a movie category (admin only)",
)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Create a new category. `slug` must be unique. Supports en / ru / kk / ky name and description."""
    return await movie_svc.create_category(data, db)


# ── Movies ────────────────────────────────────────────────────────────────────

@router.get("", response_model=PaginatedResponse, summary="List movies (paginated)")
async def list_movies(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str | None = Query(None, description="Full-text search across all language title/description fields"),
    category_id: int | None = Query(None, description="Filter by category ID"),
    language: str | None = Query(None, description="Filter by original audio language (en | ru | kk | ky)"),
    lang: str | None = Query(None, description="Response language for title/description (en | ru | kk | ky). Falls back to EN if translation is missing."),
    db: AsyncSession = Depends(get_db),
):
    """
    Return a paginated list of published movies.

    - **search** — matched against title and description in all 4 languages
    - **language** — filters by the *original* movie audio language
    - **lang** — controls which language the `title` and `description` fields are returned in
    """
    resolved = resolve_lang(lang)
    result = await movie_svc.list_movies(
        db, page=page, page_size=page_size,
        search=search, category_id=category_id, language=language,
    )
    result.items = [apply_lang_to_movie_list(m, resolved) for m in result.items]
    return result


@router.post("", response_model=MovieOut, status_code=201, summary="Create a movie (admin only)")
async def create_movie(
    title: str = Form(..., max_length=255),
    title_ru: str | None = Form(None),
    title_kk: str | None = Form(None),
    title_ky: str | None = Form(None),
    description: str | None = Form(None),
    description_ru: str | None = Form(None),
    description_kk: str | None = Form(None),
    description_ky: str | None = Form(None),
    year: int | None = Form(None),
    duration_minutes: int | None = Form(None),
    rating: float | None = Form(None, ge=0, le=10),
    language: str | None = Form(None, max_length=10),
    category_id: int | None = Form(None),
    is_published: bool = Form(True),
    poster: UploadFile | None = File(None, description="Poster image (JPEG/PNG/WebP)"),
    video: UploadFile | None = File(None, description="Video file (MP4/MKV/MOV)"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    Create a movie. Send as **multipart/form-data** to attach poster and video in one request.
    Files are optional — you can upload them later via `POST /movies/{id}/poster` and `POST /movies/{id}/video`.
    """
    from app.services.media import upload_video
    data = MovieCreate(
        title=title, title_ru=title_ru, title_kk=title_kk, title_ky=title_ky,
        description=description, description_ru=description_ru,
        description_kk=description_kk, description_ky=description_ky,
        year=year, duration_minutes=duration_minutes, rating=rating,
        language=language, category_id=category_id, is_published=is_published,
    )
    movie = await movie_svc.create_movie(data, db)

    if poster and poster.filename:
        movie.poster_path = await upload_poster(poster)
    if video and video.filename:
        movie.video_path = await upload_video(video)

    if (poster and poster.filename) or (video and video.filename):
        await db.flush()

    await db.refresh(movie, ["category"])
    return movie


@router.get("/{movie_id}", response_model=MovieOut, summary="Get a single movie")
async def get_movie(
    movie_id: uuid.UUID,
    lang: str | None = Query(None, description="Response language (en | ru | kk | ky)"),
    db: AsyncSession = Depends(get_db),
):
    """Fetch a movie by UUID. Use `lang` to get the localised title and description."""
    movie = await movie_svc.get_movie(movie_id, db)
    return apply_lang_to_movie(movie, resolve_lang(lang))


@router.patch("/{movie_id}", response_model=MovieOut, summary="Update a movie (admin only)")
async def update_movie(
    movie_id: uuid.UUID,
    data: MovieUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    Partial update — only fields included in the JSON body are changed.
    To replace poster or video files use `POST /movies/{id}/poster` and `POST /movies/{id}/video`.
    """
    return await movie_svc.update_movie(movie_id, data, db)


@router.delete("/{movie_id}", response_model=MessageResponse, summary="Delete a movie (admin only)")
async def delete_movie(
    movie_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    await movie_svc.delete_movie(movie_id, db)
    return MessageResponse(message="Movie deleted")


# ── Media uploads ─────────────────────────────────────────────────────────────

@router.post("/{movie_id}/poster", response_model=MovieOut, summary="Upload poster image (admin only)")
async def upload_movie_poster(
    movie_id: uuid.UUID,
    file: UploadFile = File(..., description="JPEG, PNG or WebP image"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Upload a poster image for a movie. Accepts JPEG / PNG / WebP. Also available via the admin panel."""
    movie = await movie_svc.get_movie(movie_id, db)
    movie.poster_path = await upload_poster(file)
    await db.flush()
    await db.refresh(movie, ["category"])
    return movie


@router.post("/{movie_id}/video", response_model=MovieOut, summary="Upload video file (admin only)")
async def upload_movie_video(
    movie_id: uuid.UUID,
    file: UploadFile = File(..., description="MP4, MKV, MOV, AVI or WebM video file"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    Upload an MP4 (or compatible) video file. Streamed to disk in chunks — suitable for large files.
    For HLS streaming, upload the pre-encoded `.m3u8` path via `POST /movies/{id}/hls`.
    Also available via the admin panel form.
    """
    from app.services.media import upload_video
    movie = await movie_svc.get_movie(movie_id, db)
    movie.video_path = await upload_video(file)
    await db.flush()
    await db.refresh(movie, ["category"])
    return movie


@router.post("/{movie_id}/hls", response_model=MovieOut, summary="Set HLS stream path (admin only)")
async def set_movie_hls(
    movie_id: uuid.UUID,
    hls_path: str = Query(..., description="Absolute or relative path to the .m3u8 playlist file"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    Register a pre-encoded HLS stream. The path must end with `.m3u8`.
    The segments should already exist in the media storage accessible to the server.
    """
    movie = await movie_svc.get_movie(movie_id, db)
    movie.hls_path = register_hls_path(hls_path)
    await db.flush()
    await db.refresh(movie, ["category"])
    return movie
