"""add music categories

Revision ID: f1a2b3c4d5e6
Revises: ('ad476c813f71', 'e3b1c2d4f5a6')
Create Date: 2026-05-24 10:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, tuple] = ("ad476c813f71", "e3b1c2d4f5a6")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "music_categories",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("name_ru", sa.String(100), nullable=True),
        sa.Column("name_kk", sa.String(100), nullable=True),
        sa.Column("name_ky", sa.String(100), nullable=True),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("description_ru", sa.Text(), nullable=True),
        sa.Column("description_kk", sa.Text(), nullable=True),
        sa.Column("description_ky", sa.Text(), nullable=True),
        sa.Column("icon", sa.String(20), nullable=True),
    )
    op.create_index("ix_music_categories_slug", "music_categories", ["slug"])

    op.add_column("music", sa.Column("category_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_music_category_id",
        "music",
        "music_categories",
        ["category_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_music_category_id", "music", ["category_id"])


def downgrade() -> None:
    op.drop_index("ix_music_category_id", table_name="music")
    op.drop_constraint("fk_music_category_id", "music", type_="foreignkey")
    op.drop_column("music", "category_id")

    op.drop_index("ix_music_categories_slug", table_name="music_categories")
    op.drop_table("music_categories")
