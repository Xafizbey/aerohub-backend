import uuid
from typing import Any

from sqladmin import BaseView, ModelView, expose
from sqlalchemy import delete, select
from starlette.requests import Request
from wtforms import FileField, SelectField

from app.db.session import AsyncSessionLocal
from app.models.analytics import PlayHistory, ViewHistory
from app.models.cafe import CafeCategory, CafeItem, CafeOrder, CafeOrderItem
from app.models.content import Banner, FlightInfo
from app.models.movie import Movie, MovieCategory
from app.models.music import Music, MusicCategory, Playlist, PlaylistTrack
from app.models.user import User
from app.services.analytics import get_genre_stats
from app.services.media import upload_audio, upload_poster, upload_video, upload_cafe_image


# ── Accounts ──────────────────────────────────────────────────────────────────

class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-users"
    category = "Accounts"

    column_list = [
        User.username, User.email, User.full_name,
        User.seat_number, User.role, User.is_active, User.created_at,
    ]
    column_searchable_list = [User.username, User.email, User.full_name]
    column_filters = [User.role, User.is_active, User.created_at]
    column_sortable_list = [User.username, User.email, User.role, User.is_active, User.created_at]
    column_default_sort = [(User.created_at, True)]

    column_labels = {
        "username": "Username",
        "email": "Email",
        "full_name": "Full Name",
        "seat_number": "Seat",
        "role": "Role",
        "is_active": "Active",
        "created_at": "Joined",
        "updated_at": "Updated",
        "hashed_password": "Password Hash",
    }

    # Never expose the hashed password in forms or detail views
    form_excluded_columns = [
        User.hashed_password, User.view_history, User.play_history,
        User.created_at, User.updated_at,
    ]
    column_details_exclude_list = [User.hashed_password]

    page_size = 25
    page_size_options = [10, 25, 50, 100]


# ── Movies ────────────────────────────────────────────────────────────────────

class MovieCategoryAdmin(ModelView, model=MovieCategory):
    name = "Category"
    name_plural = "Movie Categories"
    icon = "fa-solid fa-tags"
    category = "Movies"

    column_list = [MovieCategory.id, MovieCategory.name, MovieCategory.slug, MovieCategory.description]
    column_searchable_list = [MovieCategory.name, MovieCategory.name_ru, MovieCategory.name_kk, MovieCategory.name_ky, MovieCategory.slug]
    column_sortable_list = [MovieCategory.id, MovieCategory.name, MovieCategory.slug]

    column_labels = {
        "name": "Name (EN)",
        "name_ru": "Name (RU)",
        "name_kk": "Name (KZ)",
        "name_ky": "Name (KY)",
        "slug": "Slug",
        "description": "Description (EN)",
        "description_ru": "Description (RU)",
        "description_kk": "Description (KZ)",
        "description_ky": "Description (KY)",
    }

    form_excluded_columns = [MovieCategory.movies]
    page_size = 25


class MovieAdmin(ModelView, model=Movie):
    name = "Movie"
    name_plural = "Movies"
    icon = "fa-solid fa-film"
    category = "Movies"

    column_list = [
        Movie.title, Movie.year, Movie.rating, Movie.language,
        Movie.category, Movie.is_published, Movie.view_count, Movie.created_at,
    ]
    column_searchable_list = [Movie.title, Movie.title_ru, Movie.title_kk, Movie.title_ky]
    column_filters = [Movie.is_published, Movie.language, Movie.year, Movie.category]
    column_sortable_list = [
        Movie.title, Movie.year, Movie.rating, Movie.is_published,
        Movie.view_count, Movie.created_at,
    ]
    column_default_sort = [(Movie.created_at, True)]

    column_labels = {
        "title": "Title (EN)",
        "title_ru": "Title (RU)",
        "title_kk": "Title (KZ)",
        "title_ky": "Title (KY)",
        "description": "Description (EN)",
        "description_ru": "Description (RU)",
        "description_kk": "Description (KZ)",
        "description_ky": "Description (KY)",
        "year": "Year",
        "duration_minutes": "Duration (min)",
        "rating": "Rating",
        "language": "Language",
        "poster_path": "Poster Path",
        "video_path": "Video Path",
        "hls_path": "HLS Path",
        "category": "Category",
        "view_count": "Views",
        "is_published": "Published",
        "created_at": "Created",
        "updated_at": "Updated",
    }

    form_excluded_columns = [
        Movie.view_history, Movie.view_count,
        Movie.poster_path, Movie.video_path, Movie.hls_path,
        Movie.duration_minutes, Movie.created_at, Movie.updated_at,
    ]
    page_size = 25
    page_size_options = [10, 25, 50, 100]

    async def scaffold_form(self) -> type:
        form_class = await super().scaffold_form()
        form_class.poster_upload = FileField("Poster Image (JPEG/PNG/WebP)")
        form_class.video_upload = FileField("Video File (MP4/MKV/MOV — leave empty to keep current)")
        return form_class

    async def on_model_change(self, data: dict, model: Any, is_created: bool, request: Request) -> None:
        poster_file = data.get("poster_upload")
        if poster_file and getattr(poster_file, "filename", None):
            model.poster_path = await upload_poster(poster_file)

        video_file = data.get("video_upload")
        if video_file and getattr(video_file, "filename", None):
            model.video_path = await upload_video(video_file)


# ── Music ─────────────────────────────────────────────────────────────────────

class MusicCategoryAdmin(ModelView, model=MusicCategory):
    name = "Category"
    name_plural = "Music Categories"
    icon = "fa-solid fa-tags"
    category = "Music"

    column_list = [MusicCategory.id, MusicCategory.name, MusicCategory.slug, MusicCategory.icon, MusicCategory.description]
    column_searchable_list = [MusicCategory.name, MusicCategory.name_ru, MusicCategory.name_kk, MusicCategory.name_ky, MusicCategory.slug]
    column_sortable_list = [MusicCategory.id, MusicCategory.name, MusicCategory.slug]

    column_labels = {
        "name": "Name (EN)",
        "name_ru": "Name (RU)",
        "name_kk": "Name (KZ)",
        "name_ky": "Name (KY)",
        "slug": "Slug",
        "icon": "Icon (emoji)",
        "description": "Description (EN)",
        "description_ru": "Description (RU)",
        "description_kk": "Description (KZ)",
        "description_ky": "Description (KY)",
    }

    form_excluded_columns = [MusicCategory.tracks]
    page_size = 25


class MusicAdmin(ModelView, model=Music):
    name = "Track"
    name_plural = "Music"
    icon = "fa-solid fa-music"
    category = "Music"

    column_list = [
        Music.title, Music.artist, Music.album, Music.genre,
        Music.category, Music.language, Music.duration_seconds,
        Music.is_published, Music.play_count, Music.created_at,
    ]
    column_searchable_list = [Music.title, Music.artist, Music.album, Music.genre]
    column_filters = [Music.is_published, Music.category, Music.genre, Music.language, Music.year]
    column_sortable_list = [
        Music.title, Music.artist, Music.genre, Music.is_published,
        Music.play_count, Music.created_at,
    ]
    column_default_sort = [(Music.created_at, True)]

    column_labels = {
        "title": "Title",
        "artist": "Artist",
        "album": "Album",
        "genre": "Genre",
        "duration_seconds": "Duration (s)",
        "year": "Year",
        "language": "Language",
        "category": "Category",
        "cover_path": "Cover Path",
        "audio_path": "Audio Path",
        "play_count": "Plays",
        "is_published": "Published",
        "created_at": "Created",
        "updated_at": "Updated",
    }

    form_excluded_columns = [
        Music.play_history, Music.playlist_tracks, Music.play_count,
        Music.cover_path, Music.audio_path,
        Music.album, Music.genre, Music.year, Music.language, Music.duration_seconds,
        Music.created_at, Music.updated_at,
    ]
    page_size = 25
    page_size_options = [10, 25, 50, 100]

    async def scaffold_form(self) -> type:
        form_class = await super().scaffold_form()
        form_class.cover_upload = FileField("Cover Image (JPEG/PNG/WebP)")
        form_class.audio_upload = FileField("Audio File (MP3/AAC/FLAC — leave empty to keep current)")

        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Playlist).order_by(Playlist.name))
            playlists = result.scalars().all()

        choices = [("", "— No playlist —")] + [(str(p.id), p.name) for p in playlists]
        form_class.playlist_select = SelectField(
            "Playlist (optional)",
            choices=choices,
            default="",
        )
        return form_class

    async def on_model_change(self, data: dict, model: Any, is_created: bool, request: Request) -> None:
        cover_file = data.get("cover_upload")
        if cover_file and getattr(cover_file, "filename", None):
            model.cover_path = await upload_poster(cover_file)

        audio_file = data.get("audio_upload")
        if audio_file and getattr(audio_file, "filename", None):
            model.audio_path = await upload_audio(audio_file)

    async def after_model_change(self, data: dict, model: Any, is_created: bool, request: Request) -> None:
        playlist_id_str = data.get("playlist_select") or ""
        if not playlist_id_str:
            return
        async with AsyncSessionLocal() as session:
            await session.execute(delete(PlaylistTrack).where(PlaylistTrack.music_id == model.id))
            track = PlaylistTrack(
                playlist_id=uuid.UUID(playlist_id_str),
                music_id=model.id,
                position=0,
            )
            session.add(track)
            await session.commit()


class PlaylistAdmin(ModelView, model=Playlist):
    name = "Playlist"
    name_plural = "Playlists"
    icon = "fa-solid fa-list"
    category = "Music"

    column_list = [Playlist.name, Playlist.description, Playlist.created_at]
    column_searchable_list = [Playlist.name]
    column_sortable_list = [Playlist.name, Playlist.created_at]
    column_default_sort = [(Playlist.created_at, True)]

    column_labels = {
        "name": "Name (EN)",
        "name_ru": "Name (RU)",
        "name_kk": "Name (KZ)",
        "name_ky": "Name (KY)",
        "description": "Description (EN)",
        "description_ru": "Description (RU)",
        "description_kk": "Description (KZ)",
        "description_ky": "Description (KY)",
        "banner_path": "Banner Path",
        "created_at": "Created",
    }

    form_excluded_columns = [Playlist.tracks, Playlist.banner_path, Playlist.created_at]
    page_size = 25

    async def scaffold_form(self) -> type:
        form_class = await super().scaffold_form()
        form_class.banner_upload = FileField("Banner Image (JPEG/PNG/WebP)")
        return form_class

    async def on_model_change(self, data: dict, model: Any, is_created: bool, request: Request) -> None:
        banner_file = data.get("banner_upload")
        if banner_file and getattr(banner_file, "filename", None):
            model.banner_path = await upload_poster(banner_file)


# ── Content ───────────────────────────────────────────────────────────────────

class BannerAdmin(ModelView, model=Banner):
    name = "Banner"
    name_plural = "Banners"
    icon = "fa-solid fa-image"
    category = "Content"

    column_list = [
        Banner.id, Banner.title, Banner.subtitle,
        Banner.is_active, Banner.display_order, Banner.created_at,
    ]
    column_searchable_list = [Banner.title, Banner.subtitle]
    column_filters = [Banner.is_active]
    column_sortable_list = [Banner.display_order, Banner.title, Banner.is_active, Banner.created_at]
    column_default_sort = [(Banner.display_order, False)]

    column_labels = {
        "title": "Title (EN)",
        "title_ru": "Title (RU)",
        "title_kk": "Title (KZ)",
        "title_ky": "Title (KY)",
        "subtitle": "Subtitle (EN)",
        "subtitle_ru": "Subtitle (RU)",
        "subtitle_kk": "Subtitle (KZ)",
        "subtitle_ky": "Subtitle (KY)",
        "body": "Body (EN)",
        "body_ru": "Body (RU)",
        "body_kk": "Body (KZ)",
        "body_ky": "Body (KY)",
        "image_path": "Image Path",
        "link_url": "Link URL",
        "is_active": "Active",
        "display_order": "Order",
        "created_at": "Created",
        "updated_at": "Updated",
    }

    page_size = 25


class FlightInfoAdmin(ModelView, model=FlightInfo):
    name = "Flight"
    name_plural = "Flight Info"
    icon = "fa-solid fa-plane"
    category = "Content"

    column_list = [
        FlightInfo.flight_number,
        FlightInfo.origin_iata, FlightInfo.origin_city,
        FlightInfo.destination_iata, FlightInfo.destination_city,
        FlightInfo.departure_time, FlightInfo.arrival_time,
        FlightInfo.aircraft_type, FlightInfo.is_active,
    ]
    column_searchable_list = [
        FlightInfo.flight_number, FlightInfo.origin_city,
        FlightInfo.destination_city, FlightInfo.origin_iata, FlightInfo.destination_iata,
    ]
    column_filters = [FlightInfo.is_active, FlightInfo.aircraft_type]
    column_sortable_list = [
        FlightInfo.flight_number, FlightInfo.departure_time, FlightInfo.arrival_time, FlightInfo.is_active,
    ]
    column_default_sort = [(FlightInfo.departure_time, True)]

    column_labels = {
        "flight_number": "Flight №",
        "origin_iata": "From (IATA)",
        "origin_city": "Origin City (EN)",
        "origin_city_ru": "Origin City (RU)",
        "origin_city_kk": "Origin City (KZ)",
        "origin_city_ky": "Origin City (KY)",
        "destination_iata": "To (IATA)",
        "destination_city": "Destination City (EN)",
        "destination_city_ru": "Destination City (RU)",
        "destination_city_kk": "Destination City (KZ)",
        "destination_city_ky": "Destination City (KY)",
        "departure_time": "Departure",
        "arrival_time": "Arrival",
        "aircraft_type": "Aircraft",
        "altitude_ft": "Altitude (ft)",
        "speed_kmh": "Speed (km/h)",
        "temperature_c": "Temp (°C)",
        "is_active": "Active Flight",
        "created_at": "Created",
        "updated_at": "Updated",
    }

    page_size = 25


# ── Air Cafe ──────────────────────────────────────────────────────────────────

class CafeCategoryAdmin(ModelView, model=CafeCategory):
    name = "Category"
    name_plural = "Cafe Categories"
    icon = "fa-solid fa-utensils"
    category = "Air Cafe"

    column_list = [CafeCategory.id, CafeCategory.name, CafeCategory.slug, CafeCategory.icon, CafeCategory.display_order]
    column_searchable_list = [CafeCategory.name, CafeCategory.slug]
    column_sortable_list = [CafeCategory.id, CafeCategory.display_order, CafeCategory.name]
    column_default_sort = [(CafeCategory.display_order, False)]

    column_labels = {
        "name": "Name (EN)", "name_ru": "Name (RU)", "name_kk": "Name (KZ)", "name_ky": "Name (KY)",
        "slug": "Slug", "icon": "Icon (emoji)", "display_order": "Order",
        "image_path": "Image Path",
    }

    form_excluded_columns = [CafeCategory.items, CafeCategory.image_path]
    page_size = 25

    async def scaffold_form(self) -> type:
        form_class = await super().scaffold_form()
        form_class.image_upload = FileField("Category Image (JPEG/PNG/WebP)")
        return form_class

    async def on_model_change(self, data: dict, model: Any, is_created: bool, request: Request) -> None:
        image_file = data.get("image_upload")
        if image_file and getattr(image_file, "filename", None):
            model.image_path = await upload_cafe_image(image_file)


class CafeItemAdmin(ModelView, model=CafeItem):
    name = "Menu Item"
    name_plural = "Menu Items"
    icon = "fa-solid fa-burger"
    category = "Air Cafe"

    column_list = [
        CafeItem.name, CafeItem.category, CafeItem.price,
        CafeItem.is_available, CafeItem.is_featured, CafeItem.is_chef_special,
        CafeItem.order_count, CafeItem.created_at,
    ]
    column_searchable_list = [CafeItem.name, CafeItem.name_ru, CafeItem.ingredients]
    column_filters = [CafeItem.is_available, CafeItem.is_featured, CafeItem.is_chef_special, CafeItem.is_duty_free, CafeItem.category]
    column_sortable_list = [CafeItem.name, CafeItem.price, CafeItem.is_available, CafeItem.order_count, CafeItem.created_at]
    column_default_sort = [(CafeItem.created_at, True)]

    column_labels = {
        "name": "Name (EN)", "name_ru": "Name (RU)", "name_kk": "Name (KZ)", "name_ky": "Name (KY)",
        "description": "Description (EN)", "description_ru": "Description (RU)",
        "description_kk": "Description (KZ)", "description_ky": "Description (KY)",
        "ingredients": "Ingredients", "price": "Price ($)",
        "image_path": "Image Path", "category": "Category",
        "is_available": "Available", "is_featured": "Featured",
        "is_chef_special": "Chef Special", "is_duty_free": "Duty Free",
        "is_published": "Published", "order_count": "Orders", "like_count": "Likes",
        "created_at": "Created", "updated_at": "Updated",
    }

    form_excluded_columns = [
        CafeItem.image_path, CafeItem.order_count, CafeItem.like_count,
        CafeItem.order_items, CafeItem.created_at, CafeItem.updated_at,
    ]
    page_size = 25

    async def scaffold_form(self) -> type:
        form_class = await super().scaffold_form()
        form_class.image_upload = FileField("Item Image (JPEG/PNG/WebP)")
        return form_class

    async def on_model_change(self, data: dict, model: Any, is_created: bool, request: Request) -> None:
        image_file = data.get("image_upload")
        if image_file and getattr(image_file, "filename", None):
            model.image_path = await upload_cafe_image(image_file)


class CafeOrderAdmin(ModelView, model=CafeOrder):
    name = "Order"
    name_plural = "Cafe Orders"
    icon = "fa-solid fa-receipt"
    category = "Air Cafe"

    can_create = False
    can_delete = False

    column_list = [
        CafeOrder.id, CafeOrder.seat_number, CafeOrder.status,
        CafeOrder.total_price, CafeOrder.created_at,
    ]
    column_filters = [CafeOrder.status, CafeOrder.seat_number, CafeOrder.created_at]
    column_sortable_list = [CafeOrder.seat_number, CafeOrder.status, CafeOrder.total_price, CafeOrder.created_at]
    column_default_sort = [(CafeOrder.created_at, True)]

    column_labels = {
        "seat_number": "Seat", "status": "Status",
        "total_price": "Total ($)", "notes": "Notes",
        "created_at": "Ordered At", "updated_at": "Updated",
    }

    form_excluded_columns = [CafeOrder.items, CafeOrder.created_at, CafeOrder.updated_at]
    page_size = 50


# ── Analytics (read-only) ──────────────────────────────────────────────────────


class GenreStatsView(BaseView):
    name = "Genre Stats"
    icon = "fa-solid fa-chart-bar"
    category = "Analytics"

    @expose("/genre-stats", methods=["GET"])
    async def genre_stats(self, request: Request):
        async with AsyncSessionLocal() as session:
            stats = await get_genre_stats(session)
        total_views = sum(s.total_views for s in stats)
        return await self.templates.TemplateResponse(
            request,
            "sqladmin/genre_stats.html",
            {
                "stats": stats,
                "total_views": total_views,
                "title": "Genre Statistics",
                "subtitle": "Movie views by genre",
            },
        )


class ViewHistoryAdmin(ModelView, model=ViewHistory):
    name = "View"
    name_plural = "View History"
    icon = "fa-solid fa-eye"
    category = "Analytics"

    can_create = False
    can_edit = False
    can_delete = False

    column_list = [
        ViewHistory.id, ViewHistory.user, ViewHistory.movie,
        ViewHistory.watched_seconds, ViewHistory.completed,
        ViewHistory.seat_number, ViewHistory.viewed_at,
    ]
    column_filters = [ViewHistory.completed, ViewHistory.viewed_at]
    column_sortable_list = [ViewHistory.watched_seconds, ViewHistory.completed, ViewHistory.viewed_at]
    column_default_sort = [(ViewHistory.viewed_at, True)]

    column_labels = {
        "user": "User",
        "movie": "Movie",
        "watched_seconds": "Watched (s)",
        "completed": "Completed",
        "seat_number": "Seat",
        "viewed_at": "Viewed At",
    }

    page_size = 50


class PlayHistoryAdmin(ModelView, model=PlayHistory):
    name = "Play"
    name_plural = "Play History"
    icon = "fa-solid fa-headphones"
    category = "Analytics"

    can_create = False
    can_edit = False
    can_delete = False

    column_list = [
        PlayHistory.id, PlayHistory.user, PlayHistory.music,
        PlayHistory.played_seconds, PlayHistory.completed, PlayHistory.played_at,
    ]
    column_filters = [PlayHistory.completed, PlayHistory.played_at]
    column_sortable_list = [PlayHistory.played_seconds, PlayHistory.completed, PlayHistory.played_at]
    column_default_sort = [(PlayHistory.played_at, True)]

    column_labels = {
        "user": "User",
        "music": "Track",
        "played_seconds": "Played (s)",
        "completed": "Completed",
        "played_at": "Played At",
    }

    page_size = 50
