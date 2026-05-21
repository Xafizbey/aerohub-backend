import math
import uuid
import logging

from fastapi import HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.music import Music, Playlist, PlaylistTrack
from app.schemas.music import MusicCreate, MusicUpdate, PlaylistCreate, PlaylistTrackAdd, PlaylistUpdate
from app.schemas.common import PaginatedResponse

logger = logging.getLogger(__name__)


# ── Music ────────────────────────────────────────────────────────────────────

async def create_music(data: MusicCreate, db: AsyncSession) -> Music:
    music = Music(**data.model_dump())
    db.add(music)
    await db.flush()
    await db.refresh(music)
    return music


async def get_music(music_id: uuid.UUID, db: AsyncSession) -> Music:
    result = await db.execute(select(Music).where(Music.id == music_id))
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
) -> PaginatedResponse:
    stmt = select(Music).where(Music.is_published.is_(True))

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
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(music, field, value)
    await db.flush()
    await db.refresh(music)
    return music


async def delete_music(music_id: uuid.UUID, db: AsyncSession) -> None:
    music = await get_music(music_id, db)
    await db.delete(music)


async def increment_play_count(music_id: uuid.UUID, db: AsyncSession) -> None:
    await db.execute(
        update(Music).where(Music.id == music_id).values(play_count=Music.play_count + 1)
    )


# ── Playlists ────────────────────────────────────────────────────────────────

async def create_playlist(data: PlaylistCreate, owner_id: uuid.UUID, db: AsyncSession) -> Playlist:
    playlist = Playlist(**data.model_dump(), owner_id=owner_id)
    db.add(playlist)
    await db.flush()
    await db.refresh(playlist, ["tracks"])
    return playlist


async def get_playlist(playlist_id: uuid.UUID, owner_id: uuid.UUID, db: AsyncSession) -> Playlist:
    result = await db.execute(
        select(Playlist)
        .options(selectinload(Playlist.tracks).selectinload(PlaylistTrack.music))
        .where(Playlist.id == playlist_id, Playlist.owner_id == owner_id)
    )
    playlist = result.scalar_one_or_none()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return playlist


async def list_playlists(owner_id: uuid.UUID, db: AsyncSession) -> list[Playlist]:
    result = await db.execute(
        select(Playlist)
        .options(selectinload(Playlist.tracks).selectinload(PlaylistTrack.music))
        .where(Playlist.owner_id == owner_id)
        .order_by(Playlist.created_at.desc())
    )
    return list(result.scalars().all())


async def update_playlist(
    playlist_id: uuid.UUID, data: PlaylistUpdate, owner_id: uuid.UUID, db: AsyncSession
) -> Playlist:
    playlist = await get_playlist(playlist_id, owner_id, db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(playlist, field, value)
    await db.flush()
    return playlist


async def delete_playlist(playlist_id: uuid.UUID, owner_id: uuid.UUID, db: AsyncSession) -> None:
    playlist = await get_playlist(playlist_id, owner_id, db)
    await db.delete(playlist)


async def add_track_to_playlist(
    playlist_id: uuid.UUID, data: PlaylistTrackAdd, owner_id: uuid.UUID, db: AsyncSession
) -> Playlist:
    playlist = await get_playlist(playlist_id, owner_id, db)
    await get_music(data.music_id, db)  # verify exists

    track = PlaylistTrack(
        playlist_id=playlist_id, music_id=data.music_id, position=data.position
    )
    db.add(track)
    await db.flush()
    return await get_playlist(playlist_id, owner_id, db)


async def remove_track_from_playlist(
    playlist_id: uuid.UUID, track_id: int, owner_id: uuid.UUID, db: AsyncSession
) -> Playlist:
    playlist = await get_playlist(playlist_id, owner_id, db)
    result = await db.execute(
        select(PlaylistTrack).where(
            PlaylistTrack.id == track_id, PlaylistTrack.playlist_id == playlist_id
        )
    )
    track = result.scalar_one_or_none()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found in playlist")
    await db.delete(track)
    return await get_playlist(playlist_id, owner_id, db)
