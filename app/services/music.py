import math
import uuid
import logging

from fastapi import HTTPException
from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.analytics import PlayHistory
from app.models.music import Music, MusicCategory, Playlist, PlaylistTrack
from app.schemas.music import MusicCategoryCreate, MusicCreate, MusicUpdate, PlaylistCreate, PlaylistTrackAdd, PlaylistUpdate
from app.schemas.common import PaginatedResponse

logger = logging.getLogger(__name__)


# ── Music Categories ─────────────────────────────────────────────────────────

async def list_categories(db: AsyncSession) -> list[MusicCategory]:
    result = await db.execute(select(MusicCategory).order_by(MusicCategory.name))
    return list(result.scalars().all())


async def create_category(data: MusicCategoryCreate, db: AsyncSession) -> MusicCategory:
    category = MusicCategory(**data.model_dump())
    db.add(category)
    await db.flush()
    await db.refresh(category)
    return category


# ── Music ────────────────────────────────────────────────────────────────────

async def create_music(data: MusicCreate, db: AsyncSession) -> Music:
    playlist_id = data.playlist_id
    music_data = data.model_dump(exclude={"playlist_id"})
    music = Music(**music_data)
    db.add(music)
    await db.flush()
    if playlist_id:
        await _set_music_playlist(music.id, playlist_id, db)
    await db.refresh(music, ["category"])
    return music


async def get_music(music_id: uuid.UUID, db: AsyncSession) -> Music:
    result = await db.execute(
        select(Music).options(selectinload(Music.category)).where(Music.id == music_id)
    )
    music = result.scalar_one_or_none()
    if not music:
        raise HTTPException(status_code=404, detail="Music not found")
    return music


async def list_music(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    genre: str | None = None,
    artist: str | None = None,
    language: str | None = None,
    category_id: int | None = None,
) -> PaginatedResponse:
    stmt = select(Music).options(selectinload(Music.category)).where(Music.is_published.is_(True))

    if category_id is not None:
        stmt = stmt.where(Music.category_id == category_id)
    if genre:
        stmt = stmt.where(Music.genre == genre)
    if artist:
        stmt = stmt.where(Music.artist.ilike(f"%{artist}%"))
    if language:
        stmt = stmt.where(Music.language == language)
    if search:
        pattern = f"%{search}%"
        from sqlalchemy import or_
        stmt = stmt.where(
            or_(Music.title.ilike(pattern), Music.artist.ilike(pattern), Music.album.ilike(pattern))
        )

    count_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = count_result.scalar_one()

    stmt = stmt.order_by(Music.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = list(result.scalars().all())

    return PaginatedResponse(
        items=items, total=total, page=page, page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


async def update_music(music_id: uuid.UUID, data: MusicUpdate, db: AsyncSession) -> Music:
    music = await get_music(music_id, db)
    update_fields = data.model_dump(exclude_unset=True, exclude={"playlist_id"})
    for field, value in update_fields.items():
        setattr(music, field, value)
    if "playlist_id" in data.model_fields_set:
        await _set_music_playlist(music_id, data.playlist_id, db)
    await db.flush()
    await db.refresh(music, ["category"])
    return music


async def delete_music(music_id: uuid.UUID, db: AsyncSession) -> None:
    music = await get_music(music_id, db)
    await db.delete(music)


async def record_play(
    music_id: uuid.UUID,
    played_seconds: int,
    completed: bool,
    db: AsyncSession,
) -> None:
    exists = await db.execute(select(Music.id).where(Music.id == music_id))
    if not exists.scalar_one_or_none():
        return
    entry = PlayHistory(music_id=music_id, played_seconds=played_seconds, completed=completed)
    db.add(entry)
    await db.execute(
        update(Music).where(Music.id == music_id).values(play_count=Music.play_count + 1)
    )


async def increment_play_count(music_id: uuid.UUID, db: AsyncSession) -> None:
    await db.execute(
        update(Music).where(Music.id == music_id).values(play_count=Music.play_count + 1)
    )


async def _set_music_playlist(
    music_id: uuid.UUID, playlist_id: uuid.UUID | None, db: AsyncSession
) -> None:
    """Replace the track's playlist membership with the given playlist (or clear it)."""
    await db.execute(delete(PlaylistTrack).where(PlaylistTrack.music_id == music_id))
    if playlist_id:
        track = PlaylistTrack(playlist_id=playlist_id, music_id=music_id, position=0)
        db.add(track)


# ── Playlists ────────────────────────────────────────────────────────────────

async def create_playlist(data: PlaylistCreate, db: AsyncSession) -> Playlist:
    playlist = Playlist(**data.model_dump())
    db.add(playlist)
    await db.flush()
    await db.refresh(playlist, ["tracks"])
    return playlist


async def get_playlist(playlist_id: uuid.UUID, db: AsyncSession) -> Playlist:
    result = await db.execute(
        select(Playlist)
        .options(selectinload(Playlist.tracks).selectinload(PlaylistTrack.music).selectinload(Music.category))
        .where(Playlist.id == playlist_id)
    )
    playlist = result.scalar_one_or_none()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return playlist


async def list_playlists(db: AsyncSession) -> list[Playlist]:
    result = await db.execute(
        select(Playlist)
        .options(selectinload(Playlist.tracks).selectinload(PlaylistTrack.music).selectinload(Music.category))
        .order_by(Playlist.created_at.desc())
    )
    return list(result.scalars().all())


async def update_playlist(playlist_id: uuid.UUID, data: PlaylistUpdate, db: AsyncSession) -> Playlist:
    playlist = await get_playlist(playlist_id, db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(playlist, field, value)
    await db.flush()
    return await get_playlist(playlist_id, db)


async def delete_playlist(playlist_id: uuid.UUID, db: AsyncSession) -> None:
    playlist = await get_playlist(playlist_id, db)
    await db.delete(playlist)


async def add_track_to_playlist(
    playlist_id: uuid.UUID, data: PlaylistTrackAdd, db: AsyncSession
) -> Playlist:
    await get_playlist(playlist_id, db)
    await get_music(data.music_id, db)

    existing = await db.execute(
        select(PlaylistTrack).where(
            PlaylistTrack.playlist_id == playlist_id,
            PlaylistTrack.music_id == data.music_id,
        )
    )
    if not existing.scalar_one_or_none():
        track = PlaylistTrack(
            playlist_id=playlist_id, music_id=data.music_id, position=data.position
        )
        db.add(track)
        await db.flush()
    return await get_playlist(playlist_id, db)


async def remove_track_from_playlist(
    playlist_id: uuid.UUID, track_id: int, db: AsyncSession
) -> Playlist:
    await get_playlist(playlist_id, db)
    result = await db.execute(
        select(PlaylistTrack).where(
            PlaylistTrack.id == track_id, PlaylistTrack.playlist_id == playlist_id
        )
    )
    track = result.scalar_one_or_none()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found in playlist")
    await db.delete(track)
    return await get_playlist(playlist_id, db)
