import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    DateTime, Float, ForeignKey, Index, Integer, String, Text, func, Enum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CafeCategory(Base):
    __tablename__ = "cafe_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name_ru: Mapped[str | None] = mapped_column(String(100))
    name_kk: Mapped[str | None] = mapped_column(String(100))
    name_ky: Mapped[str | None] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    icon: Mapped[str | None] = mapped_column(String(50))
    image_path: Mapped[str | None] = mapped_column(String(512))
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    items: Mapped[list["CafeItem"]] = relationship(back_populates="category", lazy="select")

    def __str__(self) -> str:
        return self.name


class CafeItem(Base):
    __tablename__ = "cafe_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    name_ru: Mapped[str | None] = mapped_column(String(255))
    name_kk: Mapped[str | None] = mapped_column(String(255))
    name_ky: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    description_ru: Mapped[str | None] = mapped_column(Text)
    description_kk: Mapped[str | None] = mapped_column(Text)
    description_ky: Mapped[str | None] = mapped_column(Text)
    ingredients: Mapped[str | None] = mapped_column(Text)

    price: Mapped[float] = mapped_column(Float, nullable=False)
    image_path: Mapped[str | None] = mapped_column(String(512))

    category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("cafe_categories.id", ondelete="SET NULL"), index=True
    )
    category: Mapped["CafeCategory | None"] = relationship(back_populates="items")

    is_available: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_featured: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_published: Mapped[bool] = mapped_column(default=True, nullable=False)

    # today's chef special
    is_chef_special: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Duty-free flag
    is_duty_free: Mapped[bool] = mapped_column(default=False, nullable=False)

    order_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    like_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Stub for sqladmin FileField — prevents AttributeError in sqladmin 0.19
    # _handle_form_data when no image is uploaded on edit.
    image_upload = None

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    order_items: Mapped[list["CafeOrderItem"]] = relationship(back_populates="item", lazy="select")

    __table_args__ = (
        Index("ix_cafe_items_name", "name"),
        Index("ix_cafe_items_is_available", "is_available"),
        Index("ix_cafe_items_is_featured", "is_featured"),
        Index("ix_cafe_items_is_published", "is_published"),
    )

    def __str__(self) -> str:
        return self.name


class OrderStatus(str, PyEnum):
    pending   = "pending"
    confirmed = "confirmed"
    preparing = "preparing"
    delivered = "delivered"
    cancelled = "cancelled"


class CafeOrder(Base):
    __tablename__ = "cafe_orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seat_number: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status"), default=OrderStatus.pending, nullable=False
    )
    total_price: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    items: Mapped[list["CafeOrderItem"]] = relationship(
        back_populates="order", lazy="selectin", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_cafe_orders_status", "status"),
        Index("ix_cafe_orders_created_at", "created_at"),
    )

    def __str__(self) -> str:
        return f"Order #{str(self.id)[:8]} · {self.seat_number}"


class CafeOrderItem(Base):
    __tablename__ = "cafe_order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cafe_orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cafe_items.id", ondelete="RESTRICT"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)

    order: Mapped["CafeOrder"] = relationship(back_populates="items")
    item: Mapped["CafeItem"] = relationship(back_populates="order_items")
