"""Add structured ground-truth tables and project tagging on notes.

Revision ID: 20260418_0004
Revises: 20260417_0003
Create Date: 2026-04-18 15:20:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260418_0004"
down_revision = "20260417_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("notes", sa.Column("project_id", sa.String(length=64), nullable=True))
    op.create_index("ix_notes_project_id", "notes", ["project_id"], unique=False)

    op.create_table(
        "user_profile",
        sa.Column("attribute", sa.String(length=64), primary_key=True),
        sa.Column("value_encrypted", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "project_registry",
        sa.Column("project_id", sa.String(length=64), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("team_members_encrypted", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_project_registry_name", "project_registry", ["name"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_project_registry_name", table_name="project_registry")
    op.drop_table("project_registry")
    op.drop_table("user_profile")
    op.drop_index("ix_notes_project_id", table_name="notes")
    op.drop_column("notes", "project_id")
