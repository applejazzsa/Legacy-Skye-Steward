"""Initial database schema."""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "handover",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("outlet", sa.String(length=255), nullable=False),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("shift", sa.String(length=50), nullable=False),
        sa.Column("period", sa.String(length=50), nullable=True),
        sa.Column("bookings", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("walk_ins", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("covers", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("food_revenue", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("beverage_revenue", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("top_sales", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
    )
    op.create_index(op.f("ix_handover_date"), "handover", ["date"], unique=False)
    op.create_index(op.f("ix_handover_id"), "handover", ["id"], unique=False)
    op.create_index(op.f("ix_handover_outlet"), "handover", ["outlet"], unique=False)

    op.create_table(
        "guest_note",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("staff", sa.String(length=255), nullable=False),
        sa.Column("note", sa.String(length=500), nullable=False),
        sa.Column("outlet", sa.String(length=255), nullable=True),
    )
    op.create_index(op.f("ix_guest_note_date"), "guest_note", ["date"], unique=False)
    op.create_index(op.f("ix_guest_note_id"), "guest_note", ["id"], unique=False)
    op.create_index(op.f("ix_guest_note_outlet"), "guest_note", ["outlet"], unique=False)
    op.create_index(op.f("ix_guest_note_staff"), "guest_note", ["staff"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_guest_note_staff"), table_name="guest_note")
    op.drop_index(op.f("ix_guest_note_outlet"), table_name="guest_note")
    op.drop_index(op.f("ix_guest_note_id"), table_name="guest_note")
    op.drop_index(op.f("ix_guest_note_date"), table_name="guest_note")
    op.drop_table("guest_note")
    op.drop_index(op.f("ix_handover_outlet"), table_name="handover")
    op.drop_index(op.f("ix_handover_id"), table_name="handover")
    op.drop_index(op.f("ix_handover_date"), table_name="handover")
    op.drop_table("handover")
