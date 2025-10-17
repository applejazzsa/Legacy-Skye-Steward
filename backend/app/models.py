from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# --- Existing tables (kept) ---
class Handover(Base):
    __tablename__ = "handovers"

    id = Column(Integer, primary_key=True, index=True)
    outlet = Column(String(100), nullable=False)
    date = Column(DateTime, nullable=False)
    shift = Column(String(10), nullable=False)          # AM / PM
    period = Column(String(20), nullable=False)         # BREAKFAST/LUNCH/DINNER
    bookings = Column(Integer, default=0)
    walk_ins = Column(Integer, default=0)
    covers = Column(Integer, default=0)
    food_revenue = Column(Float, default=0.0)
    beverage_revenue = Column(Float, default=0.0)
    top_sales = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class GuestNote(Base):
    __tablename__ = "guest_notes"

    id = Column(Integer, primary_key=True, index=True)
    guest_name = Column(String(120), nullable=False)
    note = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

# --- NEW: incidents ---
class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    area = Column(String(50), nullable=True)            # e.g., Restaurant, Spa
    owner = Column(String(100), nullable=True)

    status = Column(String(20), nullable=False, default="OPEN")     # OPEN/CLOSED
    severity = Column(String(20), nullable=False, default="MEDIUM") # LOW/MEDIUM/HIGH

    due_date = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
