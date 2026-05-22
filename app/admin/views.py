from typing import Any

from sqladmin import ModelView
from starlette.requests import Request
from wtforms import FileField

from app.models.analytics import PlayHistory, ViewHistory
from app.models.content import Banner, FlightInfo
from app.models.movie import Movie, MovieCategory
from app.models.music import Music, Playlist
from app.models.user import User
from app.services.media import upload_poster, upload_video


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
        User.hashed_password, User.view_history, User.play_history, User.playlists,
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

class MusicAdmin(ModelView, model=Music):
    name = "Track"
    name_plural = "Music"
    icon = "fa-solid fa-music"
    category = "Music"

    column_list = [
        Music.title, Music.artist, Music.album, Music.genre,
        Music.language, Music.duration_seconds, Music.is_published, Music.play_count, Music.created_at,
    ]
    column_searchable_list = [Music.title, Music.title_ru, Music.title_kk, Music.title_ky, Music.artist, Music.album, Music.genre]
    column_filters = [Music.is_published, Music.genre, Music.language, Music.year]
    column_sortable_list = [
        Music.title, Music.artist, Music.genre, Music.is_published,
        Music.play_count, Music.created_at,
    ]
    column_default_sort = [(Music.created_at, True)]

    column_labels = {
        "title": "Title (EN)",
        "title_ru": "Title (RU)",
        "title_kk": "Title (KZ)",
        "title_ky": "Title (KY)",
        "artist": "Artist",
        "album": "Album",
        "genre": "Genre (EN)",
        "genre_ru": "Genre (RU)",
        "genre_kk": "Genre (KZ)",
        "genre_ky": "Genre (KY)",
        "duration_seconds": "Duration (s)",
        "year": "Year",
        "language": "Language",
        "cover_path": "Cover Path",
        "audio_path": "Audio Path",
        "play_count": "Plays",
        "is_published": "Published",
        "created_at": "Created",
        "updated_at": "Updated",
    }

    form_excluded_columns = [Music.play_history, Music.playlist_tracks, Music.play_count]
    page_size = 25
    page_size_options = [10, 25, 50, 100]


class PlaylistAdmin(ModelView, model=Playlist):
    name = "Playlist"
    name_plural = "Playlists"
    icon = "fa-solid fa-list"
    category = "Music"

    column_list = [Playlist.name, Playlist.owner, Playlist.created_at]
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
        "owner": "Owner",
        "created_at": "Created",
    }

    form_excluded_columns = [Playlist.tracks]
    page_size = 25


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


# ── Analytics (read-only) ──────────────────────────────────────────────────────

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
