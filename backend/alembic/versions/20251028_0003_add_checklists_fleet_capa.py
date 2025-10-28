"""
feat(db): add checklists, fleet, capa tables

Revision ID: 20251028_0003
Revises: 20251028_0002
Create Date: 2025-10-28
"""

from alembic import op
import sqlalchemy as sa


revision = '20251028_0003'
down_revision = '20251028_0002'
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return name in insp.get_table_names()


def upgrade() -> None:
    # Checklist templates
    if not _has_table('checklist_templates'):
        op.create_table(
            'checklist_templates',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('tenant_id', sa.String(length=64), nullable=False, index=True),
            sa.Column('name', sa.String(length=160), nullable=False),
            sa.Column('schema_json', sa.String(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
        )
        try:
            op.create_index('ix_checklist_template_tenant', 'checklist_templates', ['tenant_id', 'created_at'])
        except Exception:
            pass

    # Checklist responses
    if not _has_table('checklist_responses'):
        op.create_table(
            'checklist_responses',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('tenant_id', sa.String(length=64), nullable=False, index=True),
            sa.Column('template_id', sa.Integer(), nullable=False, index=True),
            sa.Column('filled_by', sa.String(length=120), nullable=True),
            sa.Column('location', sa.String(length=160), nullable=True),
            sa.Column('answers_json', sa.String(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
        )
        try:
            op.create_index('ix_checklist_response_tenant', 'checklist_responses', ['tenant_id', 'created_at'])
        except Exception:
            pass

    # Vehicles
    if not _has_table('vehicles'):
        op.create_table(
            'vehicles',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('tenant_id', sa.String(length=64), nullable=False, index=True),
            sa.Column('reg', sa.String(length=40), nullable=False, index=True),
            sa.Column('make', sa.String(length=80), nullable=False),
            sa.Column('model', sa.String(length=80), nullable=False),
            sa.Column('status', sa.String(length=20), nullable=False, server_default='AVAILABLE'),
        )
        try:
            op.create_index('ix_vehicle_tenant', 'vehicles', ['tenant_id', 'reg'])
        except Exception:
            pass

    # Vehicle bookings
    if not _has_table('vehicle_bookings'):
        op.create_table(
            'vehicle_bookings',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('tenant_id', sa.String(length=64), nullable=False, index=True),
            sa.Column('vehicle_id', sa.Integer(), nullable=False, index=True),
            sa.Column('booked_by', sa.String(length=120), nullable=False),
            sa.Column('start_at', sa.DateTime(), nullable=False, index=True),
            sa.Column('end_at', sa.DateTime(), nullable=False, index=True),
            sa.Column('purpose', sa.String(length=200), nullable=True),
        )
        try:
            op.create_index('ix_vehicle_booking_tenant', 'vehicle_bookings', ['tenant_id', 'start_at'])
        except Exception:
            pass

    # CAPA actions (for incidents)
    if not _has_table('capa_actions'):
        op.create_table(
            'capa_actions',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('tenant_id', sa.String(length=64), nullable=False, index=True),
            sa.Column('incident_id', sa.Integer(), nullable=False, index=True),
            sa.Column('title', sa.String(length=200), nullable=False),
            sa.Column('owner', sa.String(length=120), nullable=True),
            sa.Column('status', sa.String(length=20), nullable=False, server_default='OPEN'),
            sa.Column('due_date', sa.Date(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
        )
        try:
            op.create_index('ix_capa_tenant', 'capa_actions', ['tenant_id', 'created_at'])
        except Exception:
            pass


def downgrade() -> None:
    for t in ['capa_actions','vehicle_bookings','vehicles','checklist_responses','checklist_templates']:
        try:
            op.drop_table(t)
        except Exception:
            pass

