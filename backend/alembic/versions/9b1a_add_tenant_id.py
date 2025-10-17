"""add tenant_id to tables (idempotent for SQLite)"""

from alembic import op
import sqlalchemy as sa

# Make sure these two match your environment
revision = "9b1a_add_tenant"
down_revision = "af3a7f443bc3"
branch_labels = None
depends_on = None


def _has_column(bind, table_name: str, column_name: str) -> bool:
    insp = sa.inspect(bind)
    cols = [c["name"] for c in insp.get_columns(table_name)]
    return column_name in cols


def _ensure_tenant_on_table(bind, table: str, index_name: str):
    # 1) Add column if missing
    if not _has_column(bind, table, "tenant_id"):
        op.add_column(table, sa.Column("tenant_id", sa.String(length=64), nullable=True))

    # 2) Fill NULLs with default tenant
    op.execute(f"UPDATE {table} SET tenant_id = 'legacy' WHERE tenant_id IS NULL")

    # 3) Create index if missing and set NOT NULL (batch works on SQLite)
    try:
        with op.batch_alter_table(table) as batch:
            # Index creation is safe to attempt; SQLite will raise if duplicate
            try:
                batch.create_index(index_name, ["tenant_id"])
            except Exception:
                pass
            batch.alter_column("tenant_id", existing_type=sa.String(length=64), nullable=False)
    except Exception:
        # As a fallback, just ignore index/nullable enforcement issues on SQLite
        pass


def upgrade():
    bind = op.get_bind()
    _ensure_tenant_on_table(bind, "handovers", "ix_handovers_tenant_id")
    _ensure_tenant_on_table(bind, "incidents", "ix_incidents_tenant_id")
    _ensure_tenant_on_table(bind, "sale_items", "ix_sale_items_tenant_id")
    _ensure_tenant_on_table(bind, "revenue_entries", "ix_revenue_entries_tenant_id")


def downgrade():
    # Best-effort simple downgrade (no data migration)
    try:
        with op.batch_alter_table("revenue_entries") as batch:
            try:
                batch.drop_index("ix_revenue_entries_tenant_id")
            except Exception:
                pass
            if _has_column(op.get_bind(), "revenue_entries", "tenant_id"):
                batch.drop_column("tenant_id")
    except Exception:
        pass

    try:
        with op.batch_alter_table("sale_items") as batch:
            try:
                batch.drop_index("ix_sale_items_tenant_id")
            except Exception:
                pass
            if _has_column(op.get_bind(), "sale_items", "tenant_id"):
                batch.drop_column("tenant_id")
    except Exception:
        pass

    try:
        with op.batch_alter_table("incidents") as batch:
            try:
                batch.drop_index("ix_incidents_tenant_id")
            except Exception:
                pass
            if _has_column(op.get_bind(), "incidents", "tenant_id"):
                batch.drop_column("tenant_id")
    except Exception:
        pass

    try:
        with op.batch_alter_table("handovers") as batch:
            try:
                batch.drop_index("ix_handovers_tenant_id")
            except Exception:
                pass
            if _has_column(op.get_bind(), "handovers", "tenant_id"):
                batch.drop_column("tenant_id")
    except Exception:
        pass
