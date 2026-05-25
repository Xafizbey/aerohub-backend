"""cafe_item: add stock field

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-05-25

"""
from typing import Union
import sqlalchemy as sa
from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "cafe_items",
        sa.Column("stock", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("cafe_items", "stock")
