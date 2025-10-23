"""init schema (handovers, incidents, sale_items)"""

from alembic import op
import sqlalchemy as sa

# --- REQUIRED Alembic identifiers ---
revision = "7e9d678da555"   # must match the hash in the filename
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # handovers
    op.create_table(
        "handovers",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("outlet", sa.String(length=120), nullable=False),
        sa.Column("shift", sa.String(length=10), nullable=False),
        sa.Column("covers", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_handovers_id", "handovers", ["id"])
    op.create_index("ix_handovers_date", "handovers", ["date"])

    # incidents
    op.create_table(
        "incidents",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("outlet", sa.String(length=120), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_incidents_id", "incidents", ["id"])
    op.create_index("ix_incidents_status", "incidents", ["status"])
    op.create_index("ix_incidents_created_at", "incidents", ["created_at"])

    # sale_items
    op.create_table(
        "sale_items",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sold_on", sa.Date(), nullable=False),
    )
    op.create_index("ix_sale_items_id", "sale_items", ["id"])
    op.create_index("ix_sale_items_name", "sale_items", ["name"])
    op.create_index("ix_sale_items_sold_on", "sale_items", ["sold_on"])


def downgrade():
    op.drop_index("ix_sale_items_sold_on", table_name="sale_items")
    op.drop_index("ix_sale_items_name", table_name="sale_items")
    op.drop_index("ix_sale_items_id", table_name="sale_items")
    op.drop_table("sale_items")

    op.drop_index("ix_incidents_created_at", table_name="incidents")
    op.drop_index("ix_incidents_status", table_name="incidents")
    op.drop_index("ix_incidents_id", table_name="incidents")
    op.drop_table("incidents")

    op.drop_index("ix_handovers_date", table_name="handovers")
    op.drop_index("ix_handovers_id", table_name="handovers")
    op.drop_table("handovers")
