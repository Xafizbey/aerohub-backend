from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import AsyncSessionLocal
from app.models.destination import Destination, DestinationPhoto
from app.schemas.destination import DestinationListItem, DestinationOut

router = APIRouter(prefix="/destinations", tags=["destinations"])


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.get("", response_model=list[DestinationListItem])
async def list_destinations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Destination)
        .where(Destination.is_active.is_(True))
        .options(selectinload(Destination.photos))
        .order_by(Destination.display_order, Destination.name)
    )
    destinations = result.scalars().all()

    items = []
    for d in destinations:
        cover = d.photos[0].photo_path if d.photos else None
        items.append(DestinationListItem(
            id=d.id,
            name=d.name,
            name_ru=d.name_ru,
            name_kk=d.name_kk,
            name_ky=d.name_ky,
            iata_code=d.iata_code,
            country=d.country,
            country_ru=d.country_ru,
            country_kk=d.country_kk,
            country_ky=d.country_ky,
            region=d.region,
            cover_photo=cover,
            display_order=d.display_order,
        ))
    return items


@router.get("/{destination_id}", response_model=DestinationOut)
async def get_destination(destination_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Destination)
        .where(Destination.id == destination_id, Destination.is_active.is_(True))
        .options(selectinload(Destination.photos))
    )
    dest = result.scalar_one_or_none()
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")
    return dest
