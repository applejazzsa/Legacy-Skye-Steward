"""add revenue_entries table"""

from alembic import op
import sqlalchemy as sa

# --- REQUIRED Alembic identifiers ---
revision = "af3a7f443bc3"          # must match the filename prefix
down_revision = "7e9d678da555"      # your previous init revision id
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "revenue_entries",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("outlet", sa.String(length=120), nullable=False),
        sa.Column("category", sa.String(length=40), nullable=False),
        sa.Column("amount_cents", sa.BigInteger(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(), nullable=False),
        sa.Column("description", sa.String(length=200), nullable=True),
    )
    op.create_index(
        "ix_revenue_entries_occurred_at",
        "revenue_entries",
        ["occurred_at"],
    )


def downgrade():
    op.drop_index("ix_revenue_entries_occurred_at", table_name="revenue_entries")
    op.drop_table("revenue_entries")
