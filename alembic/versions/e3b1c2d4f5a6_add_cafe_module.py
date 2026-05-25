"""add cafe module

Revision ID: e3b1c2d4f5a6
Revises: 31fdefa95221
Create Date: 2026-05-24 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "e3b1c2d4f5a6"
down_revision: Union[str, None] = "31fdefa95221"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # cafe_categories
    op.create_table(
        "cafe_categories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("name_ru", sa.String(100), nullable=True),
        sa.Column("name_kk", sa.String(100), nullable=True),
        sa.Column("name_ky", sa.String(100), nullable=True),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("icon", sa.String(50), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_cafe_categories_slug", "cafe_categories", ["slug"])

    # cafe_items
    op.create_table(
        "cafe_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("name_ru", sa.String(255), nullable=True),
        sa.Column("name_kk", sa.String(255), nullable=True),
        sa.Column("name_ky", sa.String(255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("description_ru", sa.Text(), nullable=True),
        sa.Column("description_kk", sa.Text(), nullable=True),
        sa.Column("description_ky", sa.Text(), nullable=True),
        sa.Column("ingredients", sa.Text(), nullable=True),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("image_path", sa.String(512), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("is_available", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_chef_special", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_duty_free", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("order_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("like_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["cafe_categories.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cafe_items_name", "cafe_items", ["name"])
    op.create_index("ix_cafe_items_category_id", "cafe_items", ["category_id"])
    op.create_index("ix_cafe_items_is_available", "cafe_items", ["is_available"])
    op.create_index("ix_cafe_items_is_featured", "cafe_items", ["is_featured"])
    op.create_index("ix_cafe_items_is_published", "cafe_items", ["is_published"])

    # order_status enum
    op.execute("CREATE TYPE order_status AS ENUM ('pending','confirmed','preparing','delivered','cancelled')")

    # cafe_orders
    op.create_table(
        "cafe_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("seat_number", sa.String(10), nullable=False),
        sa.Column("status", postgresql.ENUM("pending", "confirmed", "preparing", "delivered", "cancelled", name="order_status", create_type=False), nullable=False, server_default="pending"),
        sa.Column("total_price", sa.Float(), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cafe_orders_seat_number", "cafe_orders", ["seat_number"])
    op.create_index("ix_cafe_orders_status", "cafe_orders", ["status"])
    op.create_index("ix_cafe_orders_created_at", "cafe_orders", ["created_at"])

    # cafe_order_items
    op.create_table(
        "cafe_order_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("unit_price", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["cafe_orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["item_id"], ["cafe_items.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cafe_order_items_order_id", "cafe_order_items", ["order_id"])


def downgrade() -> None:
    op.drop_table("cafe_order_items")
    op.drop_table("cafe_orders")
    op.execute("DROP TYPE IF EXISTS order_status")
    op.drop_table("cafe_items")
    op.drop_table("cafe_categories")
