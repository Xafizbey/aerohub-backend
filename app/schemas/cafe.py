import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.cafe import OrderStatus


# ── Category ──────────────────────────────────────────────────────────────────

class CafeCategoryOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    name: str
    name_ru: str | None = None
    name_kk: str | None = None
    name_ky: str | None = None
    slug: str
    icon: str | None = None
    image_path: str | None = None
    display_order: int


# ── Item ──────────────────────────────────────────────────────────────────────

class CafeItemListOut(BaseModel):
    model_config = {"from_attributes": True}
    id: uuid.UUID
    name: str
    name_ru: str | None = None
    name_kk: str | None = None
    name_ky: str | None = None
    ingredients: str | None = None
    price: float
    image_path: str | None = None
    category: CafeCategoryOut | None = None
    is_available: bool
    is_featured: bool
    is_chef_special: bool
    is_duty_free: bool
    like_count: int
    order_count: int


class CafeItemOut(CafeItemListOut):
    description: str | None = None
    description_ru: str | None = None
    description_kk: str | None = None
    description_ky: str | None = None
    created_at: datetime


# ── Orders ────────────────────────────────────────────────────────────────────

class OrderItemCreate(BaseModel):
    item_id: uuid.UUID
    quantity: int = Field(ge=1, le=20, default=1)


class OrderCreate(BaseModel):
    seat_number: str = Field(max_length=10)
    notes: str | None = Field(default=None, max_length=500)
    items: list[OrderItemCreate] = Field(min_length=1)


class OrderItemOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    item_id: uuid.UUID
    quantity: int
    unit_price: float
    item: CafeItemListOut


class OrderOut(BaseModel):
    model_config = {"from_attributes": True}
    id: uuid.UUID
    seat_number: str
    status: OrderStatus
    total_price: float
    notes: str | None = None
    items: list[OrderItemOut]
    created_at: datetime


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
