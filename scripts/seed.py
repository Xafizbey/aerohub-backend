"""
Seed script — populates demo movies and music for AeroHub.
Run: python scripts/seed.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.security import hash_password
from app.models.analytics import PlayHistory, ViewHistory
from app.models.movie import Movie, MovieCategory
from app.models.music import Music, Playlist, PlaylistTrack
from app.models.user import User, UserRole

engine = create_async_engine(settings.DATABASE_URL, echo=False)
Session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


CATEGORIES = [
    {"name": "Action", "slug": "action", "description": "Action movies"},
    {"name": "Comedy", "slug": "comedy", "description": "Comedy films"},
    {"name": "Drama", "slug": "drama", "description": "Drama films"},
    {"name": "Documentary", "slug": "documentary", "description": "Documentaries"},
    {"name": "Animation", "slug": "animation", "description": "Animated features"},
]

MOVIES = [
    {
        "title": "Wings of the Steppes",
        "title_ru": "Крылья степей",
        "title_kk": "Дала қанаттары",
        "description": "An epic journey across the Kazakh steppe.",
        "year": 2023,
        "duration_minutes": 112,
        "rating": 8.2,
        "language": "kk",
        "category_slug": "drama",
        "hls_path": "/media/videos/wings/index.m3u8",
        "poster_path": "media/posters/placeholder.jpg",
    },
    {
        "title": "Sky High",
        "title_ru": "Высь",
        "title_kk": "Аспан биіктігі",
        "description": "A thrilling aviation adventure.",
        "year": 2022,
        "duration_minutes": 98,
        "rating": 7.5,
        "language": "en",
        "category_slug": "action",
        "hls_path": "/media/videos/sky_high/index.m3u8",
        "poster_path": "media/posters/placeholder.jpg",
    },
    {
        "title": "The Last Nomad",
        "title_ru": "Последний кочевник",
        "title_kk": "Соңғы көшпенді",
        "description": "Documentary about nomadic traditions in Central Asia.",
        "year": 2021,
        "duration_minutes": 85,
        "rating": 9.0,
        "language": "kk",
        "category_slug": "documentary",
        "hls_path": "/media/videos/nomad/index.m3u8",
        "poster_path": "media/posters/placeholder.jpg",
    },
]

MUSIC = [
    {
        "title": "Fly Away",
        "artist": "Dimash Kudaibergen",
        "album": "Infinite",
        "genre": "Pop",
        "duration_seconds": 245,
        "year": 2023,
        "language": "kk",
        "audio_path": "media/music/placeholder.mp3",
    },
    {
        "title": "Golden Eagle",
        "artist": "Abay Ensemble",
        "album": "Steppe Sounds",
        "genre": "Folk",
        "duration_seconds": 318,
        "year": 2022,
        "language": "kk",
        "audio_path": "media/music/placeholder.mp3",
    },
    {
        "title": "Turbulence",
        "artist": "AstanaBeats",
        "album": "Electronic Horizons",
        "genre": "Electronic",
        "duration_seconds": 192,
        "year": 2024,
        "language": "en",
        "audio_path": "media/music/placeholder.mp3",
    },
    {
        "title": "Alma-Ata Nights",
        "artist": "Jazz Collective KZ",
        "album": "City of Apples",
        "genre": "Jazz",
        "duration_seconds": 276,
        "year": 2023,
        "language": "ru",
        "audio_path": "media/music/placeholder.mp3",
    },
]


async def seed() -> None:
    async with Session() as db:
        # Admin user
        admin = User(
            email="admin@aerohub.kz",
            username="admin",
            hashed_password=hash_password("Admin1234!"),
            full_name="AeroHub Admin",
            role=UserRole.admin,
        )
        demo = User(
            email="passenger@aerohub.kz",
            username="passenger1",
            hashed_password=hash_password("Pass1234!"),
            full_name="Demo Passenger",
            seat_number="12A",
            role=UserRole.passenger,
        )
        db.add_all([admin, demo])
        await db.flush()

        # Categories
        cat_map: dict[str, MovieCategory] = {}
        for c in CATEGORIES:
            cat = MovieCategory(**c)
            db.add(cat)
            await db.flush()
            cat_map[c["slug"]] = cat

        # Movies
        movie_objs: list[Movie] = []
        for m in MOVIES:
            slug = m.pop("category_slug")
            movie = Movie(**m, category_id=cat_map[slug].id)
            db.add(movie)
            await db.flush()
            movie_objs.append(movie)

        # Music
        music_objs: list[Music] = []
        for t in MUSIC:
            track = Music(**t)
            db.add(track)
            await db.flush()
            music_objs.append(track)

        # Demo playlist
        playlist = Playlist(name="My Favourites", owner_id=demo.id)
        db.add(playlist)
        await db.flush()
        for i, track in enumerate(music_objs[:2]):
            db.add(PlaylistTrack(playlist_id=playlist.id, music_id=track.id, position=i))

        # Demo view history
        db.add(ViewHistory(user_id=demo.id, movie_id=movie_objs[0].id, watched_seconds=600, completed=True, seat_number="12A"))

        await db.commit()
        print("✓ Seed complete")
        print("  Admin   → admin@aerohub.kz / Admin1234!")
        print("  Passenger → passenger@aerohub.kz / Pass1234!")


if __name__ == "__main__":
    asyncio.run(seed())
