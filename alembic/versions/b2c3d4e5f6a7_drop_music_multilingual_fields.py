"""drop music multilingual fields

Revision ID: b2c3d4e5f6a7
Revises: f1a2b3c4d5e6
Create Date: 2026-05-24 11:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "f1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("music", "title_ru")
    op.drop_column("music", "title_kk")
    op.drop_column("music", "title_ky")
    op.drop_column("music", "genre_ru")
    op.drop_column("music", "genre_kk")
    op.drop_column("music", "genre_ky")


def downgrade() -> None:
    op.add_column("music", sa.Column("genre_ky", sa.String(100), nullable=True))
    op.add_column("music", sa.Column("genre_kk", sa.String(100), nullable=True))
    op.add_column("music", sa.Column("genre_ru", sa.String(100), nullable=True))
    op.add_column("music", sa.Column("title_ky", sa.String(255), nullable=True))
    op.add_column("music", sa.Column("title_kk", sa.String(255), nullable=True))
    op.add_column("music", sa.Column("title_ru", sa.String(255), nullable=True))
