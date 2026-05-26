from pathlib import Path

from fastapi import FastAPI
from sqladmin import Admin
from sqlalchemy import select

from app.admin.auth import AdminAuth
from app.admin.views import (
    BannerAdmin,
    CafeCategoryAdmin,
    CafeItemAdmin,
    CafeOrderAdmin,
    CompanySettingsAdmin,
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
from app.db.session import engine, AsyncSessionLocal

_TEMPLATES_DIR = str(Path(__file__).parent / "templates")

_DEFAULT_LOGO = "/media/logo.png"


async def _get_logo_url() -> str:
    """Read company logo from DB at startup; fall back to default."""
    try:
        from app.models.company import CompanySettings
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(CompanySettings).where(CompanySettings.id == 1)
            )
            obj = result.scalar_one_or_none()
            if obj and obj.logo_path:
                return f"/{obj.logo_path}"
    except Exception:
        pass
    return _DEFAULT_LOGO


def create_admin(app: FastAPI) -> Admin:
    auth_backend = AdminAuth(secret_key=settings.SECRET_KEY)

    admin = Admin(
        app,
        engine,
        authentication_backend=auth_backend,
        title="AeroHub",
        base_url="/admin",
        logo_url=_DEFAULT_LOGO,
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

    # Settings
    admin.add_view(CompanySettingsAdmin)

    # Analytics (read-only)
    admin.add_base_view(GenreStatsView)
    admin.add_view(ViewHistoryAdmin)
    admin.add_view(PlayHistoryAdmin)

    return admin
