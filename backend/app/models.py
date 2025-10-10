# app/models.py
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON
from sqlalchemy.orm import relationship
from app.db import Base

class Handover(Base):
    __tablename__ = "handovers"

    id = Column(Integer, primary_key=True, index=True)
    outlet = Column(String, index=True, nullable=False)
    date = Column(DateTime, index=True, nullable=False)
    shift = Column(String, nullable=True)     # e.g., "AM"/"PM"
    period = Column(String, nullable=True)    # e.g., "BREAKFAST"/"LUNCH"/"DINNER"
    bookings = Column(Integer, default=0)
    walk_ins = Column(Integer, default=0)
    covers = Column(Integer, default=0)
    food_revenue = Column(Float, default=0.0)
    beverage_revenue = Column(Float, default=0.0)
    # Store as JSON list in SQLite; analytics also supports comma-separated strings
    top_sales = Column(JSON, nullable=True)


class GuestNote(Base):
    __tablename__ = "guest_notes"

    id = Column(Integer, primary_key=True, index=True)
    outlet = Column(String, index=True, nullable=True)
    staff = Column(String, index=True, nullable=True)
    sentiment = Column(String, index=True, nullable=True)  # "positive", "neutral", "negative"
    date = Column(DateTime, index=True, nullable=False)


class TopSale(Base):
    __tablename__ = "top_sales"

    id = Column(Integer, primary_key=True, index=True)
    outlet = Column(String, index=True, nullable=True)
    date = Column(DateTime, index=True, nullable=False)
    item_name = Column(String, index=True, nullable=False)
    quantity = Column(Integer, default=0)
