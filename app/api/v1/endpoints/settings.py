from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.schemas.company import CompanySettingsOut, CompanySettingsUpdate
from app.services.auth import require_admin
from app.services.company import get_or_create_settings
from app.services.media import upload_company_logo

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("/", response_model=CompanySettingsOut)
async def get_settings(db: AsyncSession = Depends(get_db)):
    return await get_or_create_settings(db)


@router.patch("/", response_model=CompanySettingsOut)
async def update_settings(
    data: CompanySettingsUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    obj = await get_or_create_settings(db)
    if data.airline_name is not None:
        obj.airline_name = data.airline_name
    await db.flush()
    await db.refresh(obj)
    return obj


@router.post("/logo/", response_model=CompanySettingsOut)
async def upload_logo(
    logo: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    obj = await get_or_create_settings(db)
    path = await upload_company_logo(logo, old_path=obj.logo_path)
    obj.logo_path = path
    await db.flush()
    await db.refresh(obj)
    return obj
