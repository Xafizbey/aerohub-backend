import math
import uuid
import logging

from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cafe import CafeCategory, CafeItem, CafeOrder, CafeOrderItem, OrderStatus
from app.schemas.cafe import OrderCreate
from app.schemas.common import PaginatedResponse

logger = logging.getLogger(__name__)


# ── Categories ────────────────────────────────────────────────────────────────

async def list_categories(db: AsyncSession) -> list[CafeCategory]:
    result = await db.execute(
        select(CafeCategory).order_by(CafeCategory.display_order, CafeCategory.name)
    )
    return list(result.scalars().all())


# ── Items ─────────────────────────────────────────────────────────────────────

async def list_items(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    category_id: int | None = None,
    featured: bool | None = None,
    chef_special: bool | None = None,
    duty_free: bool | None = None,
    search: str | None = None,
    lang: str | None = None,
) -> PaginatedResponse:
    q = select(CafeItem).options(selectinload(CafeItem.category)).where(CafeItem.is_published == True)

    if category_id is not None:
        q = q.where(CafeItem.category_id == category_id)
    if featured is not None:
        q = q.where(CafeItem.is_featured == featured)
    if chef_special is not None:
        q = q.where(CafeItem.is_chef_special == chef_special)
    if duty_free is not None:
        q = q.where(CafeItem.is_duty_free == duty_free)
    if search:
        term = f"%{search}%"
        q = q.where(or_(
            CafeItem.name.ilike(term),
            CafeItem.name_ru.ilike(term),
            CafeItem.name_kk.ilike(term),
            CafeItem.name_ky.ilike(term),
            CafeItem.ingredients.ilike(term),
        ))

    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar_one()

    q = q.order_by(CafeItem.is_featured.desc(), CafeItem.order_count.desc(), CafeItem.name)
    q = q.offset((page - 1) * page_size).limit(page_size)
    items = list((await db.execute(q)).scalars().all())

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=max(1, math.ceil(total / page_size)),
    )


async def get_item(item_id: uuid.UUID, db: AsyncSession) -> CafeItem:
    result = await db.execute(
        select(CafeItem).options(selectinload(CafeItem.category)).where(CafeItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item


# ── Orders ────────────────────────────────────────────────────────────────────

async def create_order(data: OrderCreate, db: AsyncSession) -> CafeOrder:
    # Fetch and validate all items in one query
    item_ids = [i.item_id for i in data.items]
    result = await db.execute(
        select(CafeItem).where(CafeItem.id.in_(item_ids), CafeItem.is_published == True)
    )
    db_items = {i.id: i for i in result.scalars().all()}

    missing = [str(i) for i in item_ids if i not in db_items]
    if missing:
        raise HTTPException(status_code=422, detail=f"Items not found: {', '.join(missing)}")

    unavailable = [db_items[i].name for i in item_ids if not db_items[i].is_available]
    if unavailable:
        raise HTTPException(status_code=422, detail=f"Items unavailable: {', '.join(unavailable)}")

    total = sum(db_items[i.item_id].price * i.quantity for i in data.items)

    order = CafeOrder(
        seat_number=data.seat_number,
        notes=data.notes,
        total_price=round(total, 2),
        status=OrderStatus.pending,
    )
    db.add(order)
    await db.flush()

    for line in data.items:
        db_item = db_items[line.item_id]
        db.add(CafeOrderItem(
            order_id=order.id,
            item_id=line.item_id,
            quantity=line.quantity,
            unit_price=db_item.price,
        ))
        db_item.order_count += line.quantity
        if db_item.stock is not None:
            db_item.stock = max(0, db_item.stock - line.quantity)
            if db_item.stock == 0:
                db_item.is_available = False

    await db.flush()
    await db.refresh(order, ["items"])
    return order


async def get_order(order_id: uuid.UUID, db: AsyncSession) -> CafeOrder:
    result = await db.execute(
        select(CafeOrder)
        .options(selectinload(CafeOrder.items).selectinload(CafeOrderItem.item).selectinload(CafeItem.category))
        .where(CafeOrder.id == order_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


async def update_order_status(order_id: uuid.UUID, status: OrderStatus, db: AsyncSession) -> CafeOrder:
    order = await get_order(order_id, db)
    order.status = status
    await db.flush()
    return order


async def list_orders(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 25,
    status: OrderStatus | None = None,
    seat_number: str | None = None,
) -> PaginatedResponse:
    q = select(CafeOrder).options(
        selectinload(CafeOrder.items).selectinload(CafeOrderItem.item)
    )
    if status:
        q = q.where(CafeOrder.status == status)
    if seat_number:
        q = q.where(CafeOrder.seat_number == seat_number)

    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar_one()

    q = q.order_by(CafeOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    orders = list((await db.execute(q)).scalars().all())

    return PaginatedResponse(
        items=orders,
        total=total,
        page=page,
        page_size=page_size,
        pages=max(1, math.ceil(total / page_size)),
    )
