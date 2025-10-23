from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, BigInteger, Index
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
