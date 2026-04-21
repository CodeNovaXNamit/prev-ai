"""Add memory metadata and chat log flags.

Revision ID: 20260421_0005
Revises: 20260418_0004
Create Date: 2026-04-21 01:45:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260421_0005"
down_revision = "20260418_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("chat_messages", sa.Column("is_system_log", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.alter_column("chat_messages", "is_system_log", server_default=None)

    op.add_column("user_memories", sa.Column("importance", sa.Integer(), nullable=False, server_default="3"))
    op.add_column("user_memories", sa.Column("is_archived", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.alter_column("user_memories", "importance", server_default=None)
    op.alter_column("user_memories", "is_archived", server_default=None)


def downgrade() -> None:
    op.drop_column("user_memories", "is_archived")
    op.drop_column("user_memories", "importance")
    op.drop_column("chat_messages", "is_system_log")
