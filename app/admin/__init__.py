from pathlib import Path

from fastapi import FastAPI
from sqladmin import Admin
from sqlalchemy import select

from app.admin.auth import AdminAuth
from app.admin.views import (
    BannerAdmin,
    CafeCategoryAdmin,
    CafeItemAdmin,
    CafeOrdersView,
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
_admin: Admin | None = None


def set_admin_logo(logo_path: str | None) -> None:
    """Update the sidebar logo at runtime without a server restart."""
    if _admin is None:
        return
    _admin.logo_url = f"/{logo_path}" if logo_path else _DEFAULT_LOGO


async def _load_logo_from_db() -> None:
    """Read company logo from DB at startup and apply it."""
    try:
        from app.models.company import CompanySettings
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(CompanySettings).where(CompanySettings.id == 1)
            )
            obj = result.scalar_one_or_none()
            if obj:
                set_admin_logo(obj.logo_path)
    except Exception:
        pass


def create_admin(app: FastAPI) -> Admin:
    global _admin
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
    _admin = admin

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
    admin.add_base_view(CafeOrdersView)

    # Settings
    admin.add_view(CompanySettingsAdmin)

    # Analytics (read-only)
    admin.add_base_view(GenreStatsView)
    admin.add_view(ViewHistoryAdmin)
    admin.add_view(PlayHistoryAdmin)

    return admin
