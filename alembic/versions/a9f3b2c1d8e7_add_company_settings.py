"""add_company_settings

Revision ID: a9f3b2c1d8e7
Revises: d4e5f6a7b8c9
Create Date: 2026-05-26 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a9f3b2c1d8e7"
down_revision: Union[str, None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "company_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("airline_name", sa.String(length=200), nullable=False, server_default="AeroHub"),
        sa.Column("logo_path", sa.String(length=512), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # Insert the singleton row
    op.execute("INSERT INTO company_settings (id, airline_name) VALUES (1, 'AeroHub')")


def downgrade() -> None:
    op.drop_table("company_settings")
