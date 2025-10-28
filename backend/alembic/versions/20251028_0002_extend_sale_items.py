"""
feat(db): extend sale_items with upload columns

Revision ID: 20251028_0002
Revises: 20251027_0001
Create Date: 2025-10-28
"""

from alembic import op
import sqlalchemy as sa


revision = '20251028_0002'
down_revision = '20251027_0001'
branch_labels = None
depends_on = None


def _has_column(table: str, col: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        cols = [c["name"] for c in insp.get_columns(table)]
    except Exception:
        cols = []
    return col in cols


def upgrade() -> None:
    # SQLite-safe batch alter
    with op.batch_alter_table('sale_items') as batch:
        if not _has_column('sale_items', 'sale_id'):
            batch.add_column(sa.Column('sale_id', sa.Integer(), nullable=True))
        if not _has_column('sale_items', 'product_id'):
            batch.add_column(sa.Column('product_id', sa.Integer(), nullable=True))
        if not _has_column('sale_items', 'category'):
            batch.add_column(sa.Column('category', sa.String(length=40), nullable=True))
        if not _has_column('sale_items', 'unit_price'):
            batch.add_column(sa.Column('unit_price', sa.Float(), nullable=True))
        if not _has_column('sale_items', 'revenue'):
            batch.add_column(sa.Column('revenue', sa.Float(), nullable=True))

    # indexes (best-effort)
    try:
        op.create_index('ix_sale_items_sale_id', 'sale_items', ['sale_id'])
    except Exception:
        pass
    try:
        op.create_index('ix_sale_items_product_id', 'sale_items', ['product_id'])
    except Exception:
        pass


def downgrade() -> None:
    try:
        with op.batch_alter_table('sale_items') as batch:
            if _has_column('sale_items', 'revenue'):
                batch.drop_column('revenue')
            if _has_column('sale_items', 'unit_price'):
                batch.drop_column('unit_price')
            if _has_column('sale_items', 'category'):
                batch.drop_column('category')
            if _has_column('sale_items', 'product_id'):
                batch.drop_column('product_id')
            if _has_column('sale_items', 'sale_id'):
                batch.drop_column('sale_id')
    except Exception:
        pass

