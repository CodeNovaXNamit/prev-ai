"""Add encrypted chat memory table.

Revision ID: 20260417_0002
Revises: 20260417_0001
Create Date: 2026-04-17 23:10:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260417_0002"
down_revision = "20260417_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chat_messages",
        sa.Column("id", sa.String(length=32), primary_key=True),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("content_encrypted", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("chat_messages")
