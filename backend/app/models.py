from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, BigInteger, Index, ForeignKey, Numeric, Text, Float
from sqlalchemy.orm import relationship
from .db import Base

TENANT_LEN = 64  # easy for slugs like 'legacy', 'azure', etc.

class Handover(Base):
    __tablename__ = "handovers"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(TENANT_LEN), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    outlet = Column(String(120), nullable=False)
    shift = Column(String(10), nullable=False)  # AM/PM
    covers = Column(Integer, nullable=False, default=0)

class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(TENANT_LEN), nullable=False, index=True)
    outlet = Column(String(120), nullable=False)
    severity = Column(String(20), nullable=False)   # Low/Medium/High
    title = Column(String(200), nullable=False)
    status = Column(String(20), nullable=False, index=True)  # OPEN/IN_PROGRESS/CLOSED
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class SaleItem(Base):
    __tablename__ = "sale_items"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(TENANT_LEN), nullable=False, index=True)
    name = Column(String(160), nullable=False, index=True)
    qty = Column(Integer, nullable=False, default=0)
    sold_on = Column(Date, nullable=False, index=True)
    # extended columns used by uploads & analytics
    sale_id = Column(Integer, nullable=True, index=True)
    product_id = Column(Integer, nullable=True, index=True)
    category = Column(String(40), nullable=True)
    unit_price = Column(Float, nullable=True)
    revenue = Column(Float, nullable=True)

class RevenueEntry(Base):
    __tablename__ = "revenue_entries"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(TENANT_LEN), nullable=False, index=True)
    outlet = Column(String(120), nullable=False)
    category = Column(String(40), nullable=False)         # Food/Beverage/Other
    amount_cents = Column(BigInteger, nullable=False)
    occurred_at = Column(DateTime, nullable=False, index=True, default=datetime.utcnow)
    description = Column(String(200), nullable=True)

# Helpful composite indexes (optional; SQLite will accept them)
Index("ix_handovers_tenant_date", Handover.tenant_id, Handover.date)
Index("ix_incidents_tenant_status", Incident.tenant_id, Incident.status)
Index("ix_sales_tenant_date", SaleItem.tenant_id, SaleItem.sold_on)
Index("ix_revenue_tenant_date", RevenueEntry.tenant_id, RevenueEntry.occurred_at)

# ---- Steward 2.0 additions ----

class ChecklistTemplate(Base):
    __tablename__ = "checklist_templates"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(TENANT_LEN), nullable=False, index=True)
    name = Column(String(160), nullable=False)
    # JSON stored as text to keep SQLite simple; API returns/accepts JSON
    schema_json = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class ChecklistResponse(Base):
    __tablename__ = "checklist_responses"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(TENANT_LEN), nullable=False, index=True)
    template_id = Column(Integer, nullable=False, index=True)
    filled_by = Column(String(120), nullable=True)
    location = Column(String(160), nullable=True)
    # Answers payload (JSON-as-text)
    answers_json = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(TENANT_LEN), nullable=False, index=True)
    reg = Column(String(40), nullable=False, index=True)
    make = Column(String(80), nullable=False)
    model = Column(String(80), nullable=False)
    status = Column(String(20), nullable=False, default="AVAILABLE")  # AVAILABLE/OUT/SERVICE

class VehicleBooking(Base):
    __tablename__ = "vehicle_bookings"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(TENANT_LEN), nullable=False, index=True)
    vehicle_id = Column(Integer, nullable=False, index=True)
    booked_by = Column(String(120), nullable=False)
    start_at = Column(DateTime, nullable=False, index=True)
    end_at = Column(DateTime, nullable=False, index=True)
    purpose = Column(String(200), nullable=True)

class CapaAction(Base):
    __tablename__ = "capa_actions"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(TENANT_LEN), nullable=False, index=True)
    incident_id = Column(Integer, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    owner = Column(String(120), nullable=True)
    status = Column(String(20), nullable=False, default="OPEN")  # OPEN/DONE
    due_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

Index("ix_checklist_template_tenant", ChecklistTemplate.tenant_id, ChecklistTemplate.created_at)
Index("ix_checklist_response_tenant", ChecklistResponse.tenant_id, ChecklistResponse.created_at)
Index("ix_vehicle_tenant", Vehicle.tenant_id, Vehicle.reg)
Index("ix_vehicle_booking_tenant", VehicleBooking.tenant_id, VehicleBooking.start_at)
Index("ix_capa_tenant", CapaAction.tenant_id, CapaAction.created_at)

# -----------------------------
# Core Multi-tenant Auth Models (M1)
# -----------------------------

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(160), nullable=False)
    slug = Column(String(80), unique=True, nullable=False, index=True)
    currency = Column(String(8), nullable=False, default="ZAR")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    password_hash = Column(String(200), nullable=False)
    is_active = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class UserTenant(Base):
    __tablename__ = "user_tenants"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False, default="staff")  # owner|manager|staff

    user = relationship("User")
    tenant = relationship("Tenant")

Index("ix_user_tenant_unique", UserTenant.user_id, UserTenant.tenant_id, unique=True)


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(160), nullable=False)
    category = Column(String(40), nullable=False)  # Food|Beverage
    sku = Column(String(80), nullable=True, index=True)
    is_active = Column(Integer, nullable=False, default=1)


class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    total = Column(Numeric(12, 2), nullable=False, default=0)
    source = Column(String(20), nullable=False, default="manual")  # upload|api|manual
    external_ref = Column(String(120), nullable=True)


class Upload(Base):
    __tablename__ = "uploads"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    filename = Column(String(260), nullable=False)
    status = Column(String(20), nullable=False, default="queued")  # queued|processing|done|failed
    rows_total = Column(Integer, nullable=False, default=0)
    rows_ok = Column(Integer, nullable=False, default=0)
    rows_failed = Column(Integer, nullable=False, default=0)
    error_log = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)

Index("ix_upload_tenant_created", Upload.tenant_id, Upload.created_at)
