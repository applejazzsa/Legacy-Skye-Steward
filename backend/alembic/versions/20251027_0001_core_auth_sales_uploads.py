"""
feat(db): add core auth, sales, uploads tables

Revision ID: 20251027_0001
Revises: 
Create Date: 2025-10-27
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251027_0001'
down_revision = '9b1a_add_tenant'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tenants
    op.create_table(
        'tenants',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=160), nullable=False),
        sa.Column('slug', sa.String(length=80), nullable=False),
        sa.Column('currency', sa.String(length=8), nullable=False, server_default='ZAR'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_tenants_slug', 'tenants', ['slug'], unique=True)

    # Users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(length=200), nullable=False),
        sa.Column('password_hash', sa.String(length=200), nullable=False),
        sa.Column('is_active', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # UserTenant
    op.create_table(
        'user_tenants',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False, server_default='staff'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_user_tenant_user', 'user_tenants', ['user_id'])
    op.create_index('ix_user_tenant_tenant', 'user_tenants', ['tenant_id'])
    op.create_unique_constraint('ix_user_tenant_unique', 'user_tenants', ['user_id', 'tenant_id'])

    # Products
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=160), nullable=False),
        sa.Column('category', sa.String(length=40), nullable=False),
        sa.Column('sku', sa.String(length=80), nullable=True),
        sa.Column('is_active', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_products_tenant', 'products', ['tenant_id'])

    # Sales
    op.create_table(
        'sales',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('total', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('source', sa.String(length=20), nullable=False, server_default='manual'),
        sa.Column('external_ref', sa.String(length=120), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_sales_tenant_date', 'sales', ['tenant_id', 'date'])

    # Uploads
    op.create_table(
        'uploads',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('filename', sa.String(length=260), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='queued'),
        sa.Column('rows_total', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rows_ok', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rows_failed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_log', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_upload_tenant_created', 'uploads', ['tenant_id', 'created_at'])


def downgrade() -> None:
    op.drop_table('uploads')
    op.drop_table('sales')
    op.drop_table('products')
    op.drop_constraint('ix_user_tenant_unique', 'user_tenants', type_='unique')
    op.drop_table('user_tenants')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
    op.drop_index('ix_tenants_slug', table_name='tenants')
    op.drop_table('tenants')
