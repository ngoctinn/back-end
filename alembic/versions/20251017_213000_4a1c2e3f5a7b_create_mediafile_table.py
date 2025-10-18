"""Tạo bảng mediafile.

Revision ID: 20251017_213000_4a1c2e3f5a7b
Revises: 20251017_132322_9c3dceef9942
Create Date: 2025-10-17 21:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlmodel import SQLModel

# revision identifiers, used by Alembic.
revision: str = "20251017_213000_4a1c2e3f5a7b"
down_revision: Union[str, None] = "9c3dceef9942"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Tạo bảng mediafile với các ràng buộc và index."""
    op.create_table(
        "mediafile",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("public_url", sa.String(length=1000), nullable=False),
        sa.Column("file_type", sa.String(length=100), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=True),
        sa.Column("related_entity_id", sa.Integer(), nullable=True),
        sa.Column("related_entity_type", sa.String(length=50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("file_path"),
    )

    # Tạo index
    op.create_index("ix_mediafile_file_path", "mediafile", ["file_path"])
    op.create_index(
        "ix_mediafile_related_entity_id",
        "mediafile",
        ["related_entity_id"],
    )
    op.create_index(
        "ix_mediafile_related_entity_type",
        "mediafile",
        ["related_entity_type"],
    )


def downgrade() -> None:
    """Xóa bảng mediafile."""
    op.drop_index("ix_mediafile_related_entity_type", table_name="mediafile")
    op.drop_index("ix_mediafile_related_entity_id", table_name="mediafile")
    op.drop_index("ix_mediafile_file_path", table_name="mediafile")
    op.drop_table("mediafile")
