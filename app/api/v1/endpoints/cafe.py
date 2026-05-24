import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.cafe import OrderStatus
from app.models.user import User
from app.schemas.cafe import (
    CafeCategoryOut, CafeItemListOut, CafeItemOut,
    OrderCreate, OrderOut, OrderStatusUpdate,
)
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services import cafe as cafe_svc
from app.services.auth import require_admin

router = APIRouter(prefix="/cafe", tags=["Air Cafe"])


# ── Categories ────────────────────────────────────────────────────────────────

@router.get("/categories", response_model=list[CafeCategoryOut])
async def get_categories(db: AsyncSession = Depends(get_db)):
    """All menu categories ordered by display_order."""
    return await cafe_svc.list_categories(db)


# ── Menu Items ────────────────────────────────────────────────────────────────

@router.get("/items", response_model=PaginatedResponse)
async def list_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: int | None = Query(None),
    featured: bool | None = Query(None),
    chef_special: bool | None = Query(None),
    duty_free: bool | None = Query(None),
    search: str | None = Query(None),
    lang: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    result = await cafe_svc.list_items(
        db, page=page, page_size=page_size,
        category_id=category_id, featured=featured,
        chef_special=chef_special, duty_free=duty_free,
        search=search, lang=lang,
    )
    result.items = [CafeItemListOut.model_validate(i) for i in result.items]
    return result


@router.get("/items/{item_id}", response_model=CafeItemOut)
async def get_item(item_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await cafe_svc.get_item(item_id, db)


# ── Orders ────────────────────────────────────────────────────────────────────

@router.post("/orders", response_model=OrderOut, status_code=201)
async def create_order(data: OrderCreate, db: AsyncSession = Depends(get_db)):
    """Place a new food order from a seat."""
    order = await cafe_svc.create_order(data, db)
    return await cafe_svc.get_order(order.id, db)


@router.get("/orders/{order_id}", response_model=OrderOut)
async def get_order(order_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get order status by ID."""
    return await cafe_svc.get_order(order_id, db)


@router.patch(
    "/orders/{order_id}/status",
    response_model=OrderOut,
    summary="Update order status (admin only)",
)
async def update_order_status(
    order_id: uuid.UUID,
    data: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    await cafe_svc.update_order_status(order_id, data.status, db)
    return await cafe_svc.get_order(order_id, db)


@router.get("/orders", response_model=PaginatedResponse, summary="List orders (admin only)")
async def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    status: OrderStatus | None = Query(None),
    seat_number: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await cafe_svc.list_orders(db, page=page, page_size=page_size, status=status, seat_number=seat_number)
    result.items = [OrderOut.model_validate(o) for o in result.items]
    return result
