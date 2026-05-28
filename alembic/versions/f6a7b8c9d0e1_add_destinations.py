"""add destinations and destination photos

Revision ID: f6a7b8c9d0e1
Revises: d4e5f6a7b8c9
Create Date: 2026-05-28 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f6a7b8c9d0e1"
down_revision: Union[str, None] = "a9f3b2c1d8e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "destinations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("name_ru", sa.String(100), nullable=True),
        sa.Column("name_kk", sa.String(100), nullable=True),
        sa.Column("name_ky", sa.String(100), nullable=True),
        sa.Column("iata_code", sa.String(10), nullable=False, index=True),
        sa.Column("country", sa.String(100), nullable=False),
        sa.Column("country_ru", sa.String(100), nullable=True),
        sa.Column("country_kk", sa.String(100), nullable=True),
        sa.Column("country_ky", sa.String(100), nullable=True),
        sa.Column("region", sa.String(100), nullable=True),
        sa.Column("subtitle", sa.Text(), nullable=True),
        sa.Column("subtitle_ru", sa.Text(), nullable=True),
        sa.Column("subtitle_kk", sa.Text(), nullable=True),
        sa.Column("subtitle_ky", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("description_ru", sa.Text(), nullable=True),
        sa.Column("description_kk", sa.Text(), nullable=True),
        sa.Column("description_ky", sa.Text(), nullable=True),
        sa.Column("coords", sa.String(200), nullable=True),
        sa.Column("timezone", sa.String(50), nullable=True),
        sa.Column("airport_info", sa.String(200), nullable=True),
        sa.Column("airport_hint", sa.String(100), nullable=True),
        sa.Column("currency", sa.String(100), nullable=True),
        sa.Column("currency_hint", sa.String(100), nullable=True),
        sa.Column("language_info", sa.String(200), nullable=True),
        sa.Column("language_hint", sa.String(200), nullable=True),
        sa.Column("plug_info", sa.String(100), nullable=True),
        sa.Column("plug_hint", sa.String(100), nullable=True),
        sa.Column("flight_duration", sa.String(50), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "destination_photos",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "destination_id",
            sa.Integer(),
            sa.ForeignKey("destinations.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("photo_path", sa.String(512), nullable=False),
        sa.Column("caption", sa.String(255), nullable=True),
        sa.Column("caption_ru", sa.String(255), nullable=True),
        sa.Column("caption_kk", sa.String(255), nullable=True),
        sa.Column("caption_ky", sa.String(255), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_table("destination_photos")
    op.drop_table("destinations")
