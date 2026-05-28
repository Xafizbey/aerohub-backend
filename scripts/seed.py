"""
Seed script — populates demo movies and music for AeroHub.
Run: python scripts/seed.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.security import hash_password
from app.models.analytics import PlayHistory, ViewHistory
from app.models.destination import Destination
from app.models.movie import Movie, MovieCategory
from app.models.music import Music, Playlist, PlaylistTrack
from app.models.user import User, UserRole

engine = create_async_engine(settings.DATABASE_URL, echo=False)
Session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


DESTINATIONS = [
    {
        "name": "Istanbul",
        "name_ru": "Стамбул",
        "name_kk": "Стамбул",
        "name_ky": "Стамбул",
        "iata_code": "IST",
        "country": "Turkey",
        "country_ru": "Турция",
        "country_kk": "Түркия",
        "country_ky": "Түркия",
        "region": "Europe",
        "subtitle": "Two continents, one heartbeat.",
        "subtitle_ru": "Два континента, одно сердце.",
        "subtitle_kk": "Екі континент, бір жүрек.",
        "subtitle_ky": "Эки континент, бир жүрөк.",
        "description": "From the old quarter at dusk to the Bosphorus at dawn, Istanbul rewards the curious traveler at every turn.",
        "description_ru": "От старого квартала в сумерках до Босфора на рассвете — Стамбул вознаграждает любопытного путешественника на каждом шагу.",
        "coords": "41°00′N · 28°58′E · UTC+3",
        "timezone": "UTC+3",
        "airport_info": "IST · Istanbul Intl.",
        "airport_hint": "45 min · M11",
        "currency": "₺ Turkish Lira",
        "currency_hint": "1 USD ≈ 33 ₺",
        "language_info": "Turkish · English",
        "language_hint": "RU widely spoken",
        "plug_info": "Type C / F · 230V",
        "plug_hint": "Adapter recommended",
        "flight_duration": "3H 50M",
        "display_order": 1,
    },
    {
        "name": "Dubai",
        "name_ru": "Дубай",
        "name_kk": "Дубай",
        "name_ky": "Дубай",
        "iata_code": "DXB",
        "country": "UAE",
        "country_ru": "ОАЭ",
        "country_kk": "БАӘ",
        "country_ky": "БАЭ",
        "region": "Middle East",
        "subtitle": "Where the desert meets the sky.",
        "subtitle_ru": "Там, где пустыня встречает небо.",
        "subtitle_kk": "Шөл мен аспан тоғысқан жер.",
        "subtitle_ky": "Чөл менен асман жолуккан жер.",
        "description": "A city of superlatives — the tallest tower, the largest mall, the most ambitious skyline on earth.",
        "description_ru": "Город превосходных степеней — самая высокая башня, самый большой торговый центр, самый амбициозный горизонт.",
        "coords": "25°12′N · 55°16′E · UTC+4",
        "timezone": "UTC+4",
        "airport_info": "DXB · Dubai Intl.",
        "airport_hint": "35 min · Metro Red Line",
        "currency": "AED Dirham",
        "currency_hint": "1 USD ≈ 3.67 AED",
        "language_info": "Arabic · English",
        "language_hint": "RU widely spoken",
        "plug_info": "Type G · 230V",
        "plug_hint": "UK plug, adapter needed",
        "flight_duration": "4H 20M",
        "display_order": 2,
    },
    {
        "name": "Moscow",
        "name_ru": "Москва",
        "name_kk": "Мәскеу",
        "name_ky": "Москва",
        "iata_code": "SVO",
        "country": "Russia",
        "country_ru": "Россия",
        "country_kk": "Ресей",
        "country_ky": "Россия",
        "region": "Europe",
        "subtitle": "The city that never surrenders.",
        "subtitle_ru": "Город, который никогда не сдаётся.",
        "subtitle_kk": "Ешқашан берілмейтін қала.",
        "subtitle_ky": "Эч качан берилбеген шаар.",
        "description": "Red Square, golden domes, underground palaces — Moscow is a city of grand gestures and quiet corners.",
        "description_ru": "Красная площадь, золотые купола, подземные дворцы — Москва — это город великих жестов и тихих уголков.",
        "coords": "55°45′N · 37°37′E · UTC+3",
        "timezone": "UTC+3",
        "airport_info": "SVO · Sheremetyevo Intl.",
        "airport_hint": "40 min · Aeroexpress",
        "currency": "₽ Russian Ruble",
        "currency_hint": "1 USD ≈ 90 ₽",
        "language_info": "Russian",
        "language_hint": "English in tourist areas",
        "plug_info": "Type C / F · 220V",
        "plug_hint": "Standard EU plug",
        "flight_duration": "3H 10M",
        "display_order": 3,
    },
    {
        "name": "Almaty",
        "name_ru": "Алматы",
        "name_kk": "Алматы",
        "name_ky": "Алматы",
        "iata_code": "ALA",
        "country": "Kazakhstan",
        "country_ru": "Казахстан",
        "country_kk": "Қазақстан",
        "country_ky": "Казакстан",
        "region": "Central Asia",
        "subtitle": "City of apples, mountains at your door.",
        "subtitle_ru": "Город яблок, горы у порога.",
        "subtitle_kk": "Алма қаласы, есіктің алдындағы тауы.",
        "subtitle_ky": "Алма шаары, эшигиңдеги тоолор.",
        "description": "Perched at the foot of the Tian Shan, Almaty blends Soviet grandeur with Central Asian warmth and modern energy.",
        "description_ru": "У подножия Тянь-Шаня Алматы сочетает советское величие с центральноазиатским теплом и современной энергией.",
        "coords": "43°15′N · 76°54′E · UTC+5",
        "timezone": "UTC+5",
        "airport_info": "ALA · Almaty Intl.",
        "airport_hint": "30 min · taxi",
        "currency": "₸ Tenge",
        "currency_hint": "1 USD ≈ 455 ₸",
        "language_info": "Kazakh · Russian",
        "language_hint": "English in hotels",
        "plug_info": "Type C / F · 220V",
        "plug_hint": "Standard EU plug",
        "flight_duration": "1H 30M",
        "display_order": 4,
    },
    {
        "name": "Tashkent",
        "name_ru": "Ташкент",
        "name_kk": "Ташкент",
        "name_ky": "Ташкент",
        "iata_code": "TAS",
        "country": "Uzbekistan",
        "country_ru": "Узбекистан",
        "country_kk": "Өзбекстан",
        "country_ky": "Өзбекстан",
        "region": "Central Asia",
        "subtitle": "The crossroads of the ancient Silk Road.",
        "subtitle_ru": "Перекрёсток древнего Шёлкового пути.",
        "subtitle_kk": "Ежелгі Жібек жолының тоғысы.",
        "subtitle_ky": "Байыркы Жибек жолунун айкашы.",
        "description": "Wide Soviet boulevards, ancient mosques, and the best non (bread) in Central Asia — Tashkent is warm and welcoming.",
        "description_ru": "Широкие советские бульвары, древние мечети и лучший нон в Средней Азии — Ташкент тёплый и гостеприимный.",
        "coords": "41°17′N · 69°13′E · UTC+5",
        "timezone": "UTC+5",
        "airport_info": "TAS · Islam Karimov Intl.",
        "airport_hint": "20 min · taxi",
        "currency": "UZS Som",
        "currency_hint": "1 USD ≈ 12 800 UZS",
        "language_info": "Uzbek · Russian",
        "language_hint": "English limited",
        "plug_info": "Type C / F · 220V",
        "plug_hint": "Standard EU plug",
        "flight_duration": "1H 50M",
        "display_order": 5,
    },
    {
        "name": "Bishkek",
        "name_ru": "Бишкек",
        "name_kk": "Бішкек",
        "name_ky": "Бишкек",
        "iata_code": "FRU",
        "country": "Kyrgyzstan",
        "country_ru": "Кыргызстан",
        "country_kk": "Қырғызстан",
        "country_ky": "Кыргызстан",
        "region": "Central Asia",
        "subtitle": "Gateway to the mountains of Kyrgyzstan.",
        "subtitle_ru": "Ворота в горы Кыргызстана.",
        "subtitle_kk": "Қырғызстан тауларының қақпасы.",
        "subtitle_ky": "Кыргызстандын тоолоруна дарбаза.",
        "description": "A relaxed capital surrounded by breathtaking mountain scenery, where Soviet heritage meets nomadic traditions.",
        "description_ru": "Спокойная столица, окружённая захватывающими горными пейзажами, где советское наследие встречает кочевые традиции.",
        "coords": "42°52′N · 74°34′E · UTC+6",
        "timezone": "UTC+6",
        "airport_info": "FRU · Manas Intl.",
        "airport_hint": "30 min · taxi",
        "currency": "KGS Som",
        "currency_hint": "1 USD ≈ 87 KGS",
        "language_info": "Kyrgyz · Russian",
        "language_hint": "English limited",
        "plug_info": "Type C / F · 220V",
        "plug_hint": "Standard EU plug",
        "flight_duration": "Home",
        "display_order": 6,
    },
    {
        "name": "Frankfurt",
        "name_ru": "Франкфурт",
        "name_kk": "Франкфурт",
        "name_ky": "Франкфурт",
        "iata_code": "FRA",
        "country": "Germany",
        "country_ru": "Германия",
        "country_kk": "Германия",
        "country_ky": "Германия",
        "region": "Europe",
        "subtitle": "Europe's financial pulse, with old-town soul.",
        "subtitle_ru": "Финансовый пульс Европы с душой старого города.",
        "subtitle_kk": "Ескі қала жанымен Еуропаның қаржылық соғысы.",
        "subtitle_ky": "Европанын финансылык ритми, эски шаардын жаны менен.",
        "description": "Skyscrapers and half-timbered houses coexist in Frankfurt, a hub for art, finance and world-class transport connections.",
        "description_ru": "Небоскрёбы и фахверковые дома соседствуют во Франкфурте — центре искусства, финансов и транспортных связей.",
        "coords": "50°06′N · 8°41′E · UTC+1",
        "timezone": "UTC+1",
        "airport_info": "FRA · Frankfurt Intl.",
        "airport_hint": "15 min · S-Bahn",
        "currency": "€ Euro",
        "currency_hint": "1 USD ≈ 0.92 €",
        "language_info": "German · English",
        "language_hint": "English widely spoken",
        "plug_info": "Type C / F · 230V",
        "plug_hint": "Standard EU plug",
        "flight_duration": "6H 30M",
        "display_order": 7,
    },
    {
        "name": "Beijing",
        "name_ru": "Пекин",
        "name_kk": "Пекин",
        "name_ky": "Пекин",
        "iata_code": "PEK",
        "country": "China",
        "country_ru": "Китай",
        "country_kk": "Қытай",
        "country_ky": "Кытай",
        "region": "Asia",
        "subtitle": "Five thousand years in a single city.",
        "subtitle_ru": "Пять тысяч лет в одном городе.",
        "subtitle_kk": "Бір қалада бес мың жыл.",
        "subtitle_ky": "Бир шаарда беш миң жыл.",
        "description": "The Great Wall, the Forbidden City, and roast duck at a hutong courtyard — Beijing rewards patience and curiosity.",
        "description_ru": "Великая стена, Запретный город и жареная утка во дворике хутуна — Пекин вознаграждает терпение и любопытство.",
        "coords": "39°54′N · 116°23′E · UTC+8",
        "timezone": "UTC+8",
        "airport_info": "PEK · Beijing Capital Intl.",
        "airport_hint": "45 min · Express Rail",
        "currency": "¥ Chinese Yuan",
        "currency_hint": "1 USD ≈ 7.2 ¥",
        "language_info": "Mandarin Chinese",
        "language_hint": "English limited outside hotels",
        "plug_info": "Type A / C / I · 220V",
        "plug_hint": "Universal adapter needed",
        "flight_duration": "5H 10M",
        "display_order": 8,
    },
]

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


async def _exists(db: AsyncSession, model, **filters) -> bool:
    clause = select(model).filter_by(**filters)
    result = await db.execute(clause)
    return result.scalar_one_or_none() is not None


async def seed() -> None:
    async with Session() as db:
        # Users
        if not await _exists(db, User, email="admin@aerohub.kz"):
            db.add(User(
                email="admin@aerohub.kz", username="admin",
                hashed_password=hash_password("Admin1234!"),
                full_name="AeroHub Admin", role=UserRole.admin,
            ))
            print("  + admin user")

        demo = None
        if not await _exists(db, User, email="passenger@aerohub.kz"):
            demo = User(
                email="passenger@aerohub.kz", username="passenger1",
                hashed_password=hash_password("Pass1234!"),
                full_name="Demo Passenger", seat_number="12A", role=UserRole.passenger,
            )
            db.add(demo)
            print("  + demo passenger")
        await db.flush()

        if demo is None:
            result = await db.execute(select(User).filter_by(email="passenger@aerohub.kz"))
            demo = result.scalar_one()

        # Categories
        cat_map: dict[str, MovieCategory] = {}
        for c in CATEGORIES:
            if not await _exists(db, MovieCategory, slug=c["slug"]):
                cat = MovieCategory(**c)
                db.add(cat)
                await db.flush()
                cat_map[c["slug"]] = cat
                print(f"  + category: {c['slug']}")
            else:
                result = await db.execute(select(MovieCategory).filter_by(slug=c["slug"]))
                cat_map[c["slug"]] = result.scalar_one()

        # Movies
        movie_objs: list[Movie] = []
        for m in MOVIES:
            m = dict(m)
            slug = m.pop("category_slug")
            if not await _exists(db, Movie, title=m["title"]):
                movie = Movie(**m, category_id=cat_map[slug].id)
                db.add(movie)
                await db.flush()
                movie_objs.append(movie)
                print(f"  + movie: {m['title']}")

        # Music
        music_objs: list[Music] = []
        for t in MUSIC:
            if not await _exists(db, Music, title=t["title"], artist=t["artist"]):
                track = Music(**t)
                db.add(track)
                await db.flush()
                music_objs.append(track)
                print(f"  + track: {t['title']}")

        # Demo playlist (only if we have new music)
        if music_objs and not await _exists(db, Playlist, name="My Favourites"):
            playlist = Playlist(name="My Favourites")
            db.add(playlist)
            await db.flush()
            for i, track in enumerate(music_objs[:2]):
                db.add(PlaylistTrack(playlist_id=playlist.id, music_id=track.id, position=i))
            print("  + playlist: My Favourites")

        # Destinations
        for d in DESTINATIONS:
            if not await _exists(db, Destination, iata_code=d["iata_code"]):
                db.add(Destination(**d))
                print(f"  + destination: {d['name']} ({d['iata_code']})")

        await db.commit()
        print("✓ Seed complete")
        print("  Admin     → admin@aerohub.kz / Admin1234!")
        print("  Passenger → passenger@aerohub.kz / Pass1234!")


if __name__ == "__main__":
    asyncio.run(seed())
