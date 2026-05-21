import uuid

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.music import (
    MusicCreate, MusicOut, MusicUpdate,
    PlaylistCreate, PlaylistOut, PlaylistTrackAdd, PlaylistUpdate,
)
from app.services.auth import get_current_user, require_admin
from app.services import music as music_svc
from app.services.media import upload_audio, upload_poster

router = APIRouter(prefix="/music", tags=["Music"])


# ── Music (public) ────────────────────────────────────────────────────────────

@router.get("", response_model=PaginatedResponse)
async def list_music(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    genre: str | None = Query(None),
    artist: str | None = Query(None),
    language: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    result = await music_svc.list_music(
        db, page=page, page_size=page_size,
        search=search, genre=genre, artist=artist, language=language,
    )
    result.items = [MusicOut.model_validate(m) for m in result.items]
    return result


@router.get("/{music_id}", response_model=MusicOut)
async def get_music(
    music_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await music_svc.get_music(music_id, db)


# ── Music CRUD (crew only) ────────────────────────────────────────────────────

@router.post("", response_model=MusicOut, status_code=201)
async def create_music(
    data: MusicCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    return await music_svc.create_music(data, db)


@router.patch("/{music_id}", response_model=MusicOut)
async def update_music(
    music_id: uuid.UUID,
    data: MusicUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    return await music_svc.update_music(music_id, data, db)


@router.delete("/{music_id}", response_model=MessageResponse)
async def delete_music(
    music_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    await music_svc.delete_music(music_id, db)
    return MessageResponse(message="Music deleted")


@router.post("/{music_id}/cover", response_model=MusicOut)
async def upload_cover(
    music_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    music = await music_svc.get_music(music_id, db)
    music.cover_path = await upload_poster(file)
    await db.flush()
    await db.refresh(music)
    return music


@router.post("/{music_id}/audio", response_model=MusicOut)
async def upload_audio_file(
    music_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    music = await music_svc.get_music(music_id, db)
    music.audio_path = await upload_audio(file)
    await db.flush()
    await db.refresh(music)
    return music


# ── Playlists (crew only — requires login) ────────────────────────────────────

@router.get("/playlists/me", response_model=list[PlaylistOut])
async def my_playlists(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await music_svc.list_playlists(current_user.id, db)


@router.post("/playlists", response_model=PlaylistOut, status_code=201)
async def create_playlist(
    data: PlaylistCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await music_svc.create_playlist(data, current_user.id, db)


@router.get("/playlists/{playlist_id}", response_model=PlaylistOut)
async def get_playlist(
    playlist_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await music_svc.get_playlist(playlist_id, current_user.id, db)


@router.patch("/playlists/{playlist_id}", response_model=PlaylistOut)
async def update_playlist(
    playlist_id: uuid.UUID,
    data: PlaylistUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await music_svc.update_playlist(playlist_id, data, current_user.id, db)


@router.delete("/playlists/{playlist_id}", response_model=MessageResponse)
async def delete_playlist(
    playlist_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await music_svc.delete_playlist(playlist_id, current_user.id, db)
    return MessageResponse(message="Playlist deleted")


@router.post("/playlists/{playlist_id}/tracks", response_model=PlaylistOut)
async def add_track(
    playlist_id: uuid.UUID,
    data: PlaylistTrackAdd,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await music_svc.add_track_to_playlist(playlist_id, data, current_user.id, db)


@router.delete("/playlists/{playlist_id}/tracks/{track_id}", response_model=PlaylistOut)
async def remove_track(
    playlist_id: uuid.UUID,
    track_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await music_svc.remove_track_from_playlist(playlist_id, track_id, current_user.id, db)
