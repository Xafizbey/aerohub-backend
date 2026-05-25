"""playlist: remove owner_id, add banner_path

Revision ID: a1b2c3d4e5f6
Revises: f1a2b3c4d5e6
Create Date: 2026-05-25

"""
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, tuple] = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Remove owner foreign key and column
    op.drop_index("ix_playlists_owner_id", table_name="playlists", if_exists=True)
    op.drop_constraint("playlists_owner_id_fkey", "playlists", type_="foreignkey")
    op.drop_column("playlists", "owner_id")

    # Add banner image path
    op.add_column("playlists", sa.Column("banner_path", sa.String(512), nullable=True))


def downgrade() -> None:
    op.drop_column("playlists", "banner_path")

    op.add_column("playlists", sa.Column(
        "owner_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=True
    ))
    op.create_foreign_key(
        "playlists_owner_id_fkey", "playlists", "users",
        ["owner_id"], ["id"], ondelete="CASCADE",
    )
    op.create_index("ix_playlists_owner_id", "playlists", ["owner_id"])
