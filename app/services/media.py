import logging
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.core.config import settings

logger = logging.getLogger(__name__)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/mp4", "audio/ogg", "audio/wav"}


def _save_path(subfolder: str, filename: str) -> Path:
    dest = settings.MEDIA_ROOT / subfolder
    dest.mkdir(parents=True, exist_ok=True)
    return dest / filename


async def upload_poster(file: UploadFile) -> str:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=415, detail="Only JPEG/PNG/WebP images are accepted")

    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds {settings.MAX_UPLOAD_SIZE_MB} MB limit",
        )

    suffix = Path(file.filename or "file").suffix or ".jpg"
    filename = f"{uuid.uuid4()}{suffix}"
    path = _save_path("posters", filename)
    path.write_bytes(content)

    relative = f"media/posters/{filename}"
    logger.info("Poster saved: %s", relative)
    return relative


async def upload_audio(file: UploadFile) -> str:
    if file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(status_code=415, detail="Only MP3/MP4/OGG/WAV audio is accepted")

    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds {settings.MAX_UPLOAD_SIZE_MB} MB limit",
        )

    suffix = Path(file.filename or "file").suffix or ".mp3"
    filename = f"{uuid.uuid4()}{suffix}"
    path = _save_path("music", filename)
    path.write_bytes(content)

    relative = f"media/music/{filename}"
    logger.info("Audio saved: %s", relative)
    return relative


ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mpeg", ".mov", ".avi", ".mkv", ".webm"}


async def upload_video(file: UploadFile) -> str:
    suffix = Path(file.filename or "file").suffix.lower() or ".mp4"
    if suffix not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported video format. Allowed: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}",
        )

    filename = f"{uuid.uuid4()}{suffix}"
    path = _save_path("videos", filename)

    # Stream to disk in 4MB chunks to handle large video files
    with open(path, "wb") as f:
        while True:
            chunk = await file.read(4 * 1024 * 1024)
            if not chunk:
                break
            f.write(chunk)

    relative = f"media/videos/{filename}"
    logger.info("Video saved: %s", relative)
    return relative


async def upload_cafe_image(file: UploadFile) -> str:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=415, detail="Only JPEG/PNG/WebP images are accepted")

    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds {settings.MAX_UPLOAD_SIZE_MB} MB limit",
        )

    suffix = Path(file.filename or "file").suffix or ".jpg"
    filename = f"{uuid.uuid4()}{suffix}"
    path = _save_path("cafe", filename)
    path.write_bytes(content)

    relative = f"media/cafe/{filename}"
    logger.info("Cafe image saved: %s", relative)
    return relative


ALLOWED_LOGO_TYPES = {"image/jpeg", "image/png", "image/webp", "image/svg+xml"}


async def upload_company_logo(file: UploadFile) -> str:
    if file.content_type not in ALLOWED_LOGO_TYPES:
        raise HTTPException(status_code=415, detail="Only JPEG/PNG/WebP/SVG images are accepted")

    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds {settings.MAX_UPLOAD_SIZE_MB} MB limit",
        )

    suffix = Path(file.filename or "logo").suffix or ".png"
    dest = settings.MEDIA_ROOT / "logos"
    dest.mkdir(parents=True, exist_ok=True)
    # Always write to the same filename so the URL stays stable
    filename = f"logo{suffix}"
    path = dest / filename
    path.write_bytes(content)

    relative = f"media/logos/{filename}"
    logger.info("Company logo saved: %s", relative)
    return relative


async def upload_destination_photo(file: UploadFile) -> str:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=415, detail="Only JPEG/PNG/WebP images are accepted")

    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds {settings.MAX_UPLOAD_SIZE_MB} MB limit",
        )

    suffix = Path(file.filename or "file").suffix or ".jpg"
    filename = f"{uuid.uuid4()}{suffix}"
    path = _save_path("destinations", filename)
    path.write_bytes(content)

    relative = f"media/destinations/{filename}"
    logger.info("Destination photo saved: %s", relative)
    return relative


def register_hls_path(hls_path: str) -> str:
    """Validate and normalise an HLS path supplied by admin."""
    p = Path(hls_path)
    if p.suffix.lower() != ".m3u8":
        raise HTTPException(status_code=400, detail="HLS path must end with .m3u8")
    return str(p)
