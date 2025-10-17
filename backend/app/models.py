from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Date, DateTime
from .db import Base

class Handover(Base):
    __tablename__ = "handovers"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    outlet = Column(String(120), nullable=False)
    shift = Column(String(10), nullable=False)  # AM/PM
    covers = Column(Integer, nullable=False, default=0)

class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True, index=True)
    outlet = Column(String(120), nullable=False)
    severity = Column(String(20), nullable=False)   # Low/Medium/High
    title = Column(String(200), nullable=False)
    status = Column(String(20), nullable=False, index=True)  # OPEN/IN_PROGRESS/CLOSED
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class SaleItem(Base):
    __tablename__ = "sale_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(160), nullable=False, index=True)
    qty = Column(Integer, nullable=False, default=0)
    # For simplicity we aggregate per day; you can extend with price/amount later.
    sold_on = Column(Date, nullable=False, index=True)
