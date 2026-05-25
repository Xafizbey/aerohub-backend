"""cafe_category: add image_path

Revision ID: c3d4e5f6a7b8
Revises: a1b2c3d4e5f6
Create Date: 2026-05-25

"""
from typing import Union
import sqlalchemy as sa
from alembic import op

revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, tuple] = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("cafe_categories", sa.Column("image_path", sa.String(512), nullable=True))


def downgrade() -> None:
    op.drop_column("cafe_categories", "image_path")
