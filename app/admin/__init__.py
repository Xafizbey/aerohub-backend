from pathlib import Path

from fastapi import FastAPI
from sqladmin import Admin

from app.admin.auth import AdminAuth
from app.admin.views import (
    BannerAdmin,
    CafeCategoryAdmin,
    CafeItemAdmin,
    CafeOrderAdmin,
    FlightInfoAdmin,
    GenreStatsView,
    MovieAdmin,
    MovieCategoryAdmin,
    MusicAdmin,
    MusicCategoryAdmin,
    PlayHistoryAdmin,
    PlaylistAdmin,
    UserAdmin,
    ViewHistoryAdmin,
)
from app.core.config import settings
from app.db.session import engine

_TEMPLATES_DIR = str(Path(__file__).parent / "templates")


def create_admin(app: FastAPI) -> Admin:
    auth_backend = AdminAuth(secret_key=settings.SECRET_KEY)

    admin = Admin(
        app,
        engine,
        authentication_backend=auth_backend,
        title="AeroHub",
        base_url="/admin",
        logo_url="/media/logo.png",
        favicon_url=None,
        templates_dir=_TEMPLATES_DIR,
    )

    # Accounts
    admin.add_view(UserAdmin)

    # Movies
    admin.add_view(MovieCategoryAdmin)
    admin.add_view(MovieAdmin)

    # Music
    admin.add_view(MusicCategoryAdmin)
    admin.add_view(MusicAdmin)
    admin.add_view(PlaylistAdmin)

    # Content
    admin.add_view(BannerAdmin)
    admin.add_view(FlightInfoAdmin)

    # Air Cafe
    admin.add_view(CafeCategoryAdmin)
    admin.add_view(CafeItemAdmin)
    admin.add_view(CafeOrderAdmin)

    # Analytics (read-only)
    admin.add_base_view(GenreStatsView)
    admin.add_view(ViewHistoryAdmin)
    admin.add_view(PlayHistoryAdmin)

    return admin
