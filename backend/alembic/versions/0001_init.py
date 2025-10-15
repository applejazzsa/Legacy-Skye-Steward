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
        "handovers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("outlet", sa.String(), nullable=False),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("shift", sa.String(), nullable=False),
        sa.Column("period", sa.String(), nullable=False),
        sa.Column("bookings", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("walk_ins", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("covers", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("food_revenue", sa.Float(), nullable=False, server_default="0"),
        sa.Column("beverage_revenue", sa.Float(), nullable=False, server_default="0"),
        sa.Column("top_sales", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("(datetime('now'))")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("(datetime('now'))")),
    )

    op.create_table(
        "guest_notes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("guest_name", sa.String(), nullable=False),
        sa.Column("note", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("(datetime('now'))")),
    )

def downgrade() -> None:
    op.drop_table("guest_notes")
    op.drop_table("handovers")
