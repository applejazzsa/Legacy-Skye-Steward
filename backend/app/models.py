from __future__ import annotations

from sqlalchemy import Column, Integer, String, DateTime, Float, func
from sqlalchemy.types import JSON
from app.db import Base

class Handover(Base):
    __tablename__ = "handovers"

    id = Column(Integer, primary_key=True, index=True)
    outlet = Column(String, nullable=False)
    date = Column(DateTime(timezone=False), nullable=False, index=True)
    shift = Column(String, nullable=False)
    period = Column(String, nullable=False)

    bookings = Column(Integer, nullable=False, default=0)
    walk_ins = Column(Integer, nullable=False, default=0)
    covers = Column(Integer, nullable=False, default=0)
    food_revenue = Column(Float, nullable=False, default=0.0)
    beverage_revenue = Column(Float, nullable=False, default=0.0)

    # stored as JSON array (SQLAlchemy maps to TEXT on SQLite; OK)
    top_sales = Column(JSON, nullable=False, default=list)

    created_at = Column(DateTime(timezone=False), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now(), nullable=False)

class GuestNote(Base):
    __tablename__ = "guest_notes"

    id = Column(Integer, primary_key=True, index=True)
    guest_name = Column(String, nullable=False)
    note = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now(), nullable=False)
