import uuid
import logging

from sqlalchemy import Integer, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import PlayHistory, ViewHistory
from app.models.movie import Movie, MovieCategory
from app.models.music import Music
from app.schemas.analytics import GenreStats, MovieStats, MusicStats, TrackPlay, TrackView
from app.services.movie import increment_view_count
from app.services.music import increment_play_count

logger = logging.getLogger(__name__)


async def track_movie_view(
    data: TrackView, user_id: uuid.UUID | None, db: AsyncSession
) -> ViewHistory:
    record = ViewHistory(
        user_id=user_id,
        movie_id=data.movie_id,
        watched_seconds=data.watched_seconds,
        completed=data.completed,
        seat_number=data.seat_number,
    )
    db.add(record)
    if data.completed:
        await increment_view_count(data.movie_id, db)
    await db.flush()
    return record


async def track_music_play(
    data: TrackPlay, user_id: uuid.UUID | None, db: AsyncSession
) -> PlayHistory:
    record = PlayHistory(
        user_id=user_id,
        music_id=data.music_id,
        played_seconds=data.played_seconds,
        completed=data.completed,
    )
    db.add(record)
    if data.completed:
        await increment_play_count(data.music_id, db)
    await db.flush()
    return record


async def get_movie_stats(db: AsyncSession, limit: int = 10) -> list[MovieStats]:
    stmt = (
        select(
            ViewHistory.movie_id,
            Movie.title,
            func.count(ViewHistory.id).label("total_views"),
            func.count(func.distinct(ViewHistory.user_id)).label("unique_viewers"),
            func.avg(ViewHistory.completed.cast(Integer)).label("completion_rate"),
        )
        .join(Movie, Movie.id == ViewHistory.movie_id)
        .group_by(ViewHistory.movie_id, Movie.title)
        .order_by(func.count(ViewHistory.id).desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [
        MovieStats(
            movie_id=row.movie_id,
            title=row.title,
            total_views=row.total_views,
            unique_viewers=row.unique_viewers,
            completion_rate=float(row.completion_rate or 0),
        )
        for row in rows
    ]


async def get_genre_stats(db: AsyncSession, limit: int = 30) -> list[GenreStats]:
    stmt = (
        select(
            MovieCategory.id.label("genre_id"),
            MovieCategory.name.label("genre_name"),
            func.count(ViewHistory.id).label("total_views"),
            func.count(func.distinct(ViewHistory.movie_id)).label("unique_movies"),
            func.avg(ViewHistory.completed.cast(Integer)).label("completion_rate"),
        )
        .join(Movie, Movie.category_id == MovieCategory.id)
        .join(ViewHistory, ViewHistory.movie_id == Movie.id)
        .group_by(MovieCategory.id, MovieCategory.name)
        .order_by(func.count(ViewHistory.id).desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [
        GenreStats(
            genre_id=row.genre_id,
            genre_name=row.genre_name,
            total_views=row.total_views,
            unique_movies=row.unique_movies,
            completion_rate=float(row.completion_rate or 0),
        )
        for row in rows
    ]


async def get_music_stats(db: AsyncSession, limit: int = 10) -> list[MusicStats]:
    stmt = (
        select(
            PlayHistory.music_id,
            Music.title,
            Music.artist,
            func.count(PlayHistory.id).label("total_plays"),
            func.count(func.distinct(PlayHistory.user_id)).label("unique_listeners"),
            func.avg(PlayHistory.completed.cast(Integer)).label("completion_rate"),
        )
        .join(Music, Music.id == PlayHistory.music_id)
        .group_by(PlayHistory.music_id, Music.title, Music.artist)
        .order_by(func.count(PlayHistory.id).desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [
        MusicStats(
            music_id=row.music_id,
            title=row.title,
            artist=row.artist,
            total_plays=row.total_plays,
            unique_listeners=row.unique_listeners,
            completion_rate=float(row.completion_rate or 0),
        )
        for row in rows
    ]
