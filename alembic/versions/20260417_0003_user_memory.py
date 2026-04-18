"""Add encrypted remembered facts table.

Revision ID: 20260417_0003
Revises: 20260417_0002
Create Date: 2026-04-17 23:35:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260417_0003"
down_revision = "20260417_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_memories",
        sa.Column("id", sa.String(length=32), primary_key=True),
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("value_encrypted", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_user_memories_key", "user_memories", ["key"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_user_memories_key", table_name="user_memories")
    op.drop_table("user_memories")
