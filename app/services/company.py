from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import CompanySettings


async def get_or_create_settings(db: AsyncSession) -> CompanySettings:
    result = await db.execute(select(CompanySettings).where(CompanySettings.id == 1))
    settings = result.scalar_one_or_none()
    if settings is None:
        settings = CompanySettings(id=1, airline_name="AeroHub")
        db.add(settings)
        await db.flush()
        await db.refresh(settings)
    return settings
