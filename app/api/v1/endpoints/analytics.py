import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.schemas.analytics import (
    MovieStats, MusicStats, PlayHistoryOut, TrackPlay, TrackView, ViewHistoryOut,
)
from app.services.analytics import (
    get_movie_stats, get_music_stats, track_movie_view, track_music_play,
)
from app.services.auth import require_admin

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# ── Public tracking (no auth — passengers are anonymous) ─────────────────────

@router.post("/views", response_model=ViewHistoryOut, status_code=201)
async def record_view(
    data: TrackView,
    db: AsyncSession = Depends(get_db),
):
    return await track_movie_view(data, user_id=None, db=db)


@router.post("/plays", response_model=PlayHistoryOut, status_code=201)
async def record_play(
    data: TrackPlay,
    db: AsyncSession = Depends(get_db),
):
    return await track_music_play(data, user_id=None, db=db)


# ── Crew-only stats ───────────────────────────────────────────────────────────

@router.get("/movies/top", response_model=list[MovieStats])
async def top_movies(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    return await get_movie_stats(db, limit=limit)


@router.get("/music/top", response_model=list[MusicStats])
async def top_music(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    return await get_music_stats(db, limit=limit)
