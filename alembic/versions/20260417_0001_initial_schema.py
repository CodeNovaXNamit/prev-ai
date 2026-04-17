"""Initial encrypted productivity schema.

Revision ID: 20260417_0001
Revises:
Create Date: 2026-04-17 18:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260417_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tasks",
        sa.Column("id", sa.String(length=32), primary_key=True),
        sa.Column("title_encrypted", sa.Text(), nullable=False),
        sa.Column("description_encrypted", sa.Text(), nullable=False),
        sa.Column("due_date", sa.String(length=64), nullable=True),
        sa.Column("priority", sa.String(length=16), nullable=False, server_default="medium"),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "events",
        sa.Column("id", sa.String(length=32), primary_key=True),
        sa.Column("title_encrypted", sa.Text(), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("location_encrypted", sa.Text(), nullable=False),
        sa.Column("notes_encrypted", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "notes",
        sa.Column("id", sa.String(length=32), primary_key=True),
        sa.Column("title_encrypted", sa.Text(), nullable=False),
        sa.Column("note_text_encrypted", sa.Text(), nullable=False),
        sa.Column("summary_encrypted", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "behavior_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("feature", sa.String(length=32), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("detail_encrypted", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("behavior_events")
    op.drop_table("notes")
    op.drop_table("events")
    op.drop_table("tasks")
