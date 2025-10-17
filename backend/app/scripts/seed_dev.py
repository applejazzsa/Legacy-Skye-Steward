from datetime import date, timedelta
from sqlalchemy.orm import Session
from ..db import Base, engine, SessionLocal
from ..models import Handover, Incident, SaleItem

def ensure_seed(db: Session):
    # if there is already data, don't duplicate
    if db.query(Handover).count() > 0:
        return

    # Handovers (match what you see on the dashboard)
    handovers = [
        Handover(id=5001, date=date(2025, 10, 16), outlet="Cafe Grill",   shift="PM", covers=78),
        Handover(id=5002, date=date(2025, 10, 16), outlet="Leopard Bar",  shift="PM", covers=54),
        Handover(id=5003, date=date(2025, 10, 17), outlet="Azure Restaurant", shift="AM", covers=63),
    ]

    # Incidents (OPEN/IN_PROGRESS so they count as "open")
    incidents = [
        Incident(id=101, outlet="Cafe Grill",  severity="Medium", title="Card machine offline",   status="OPEN"),
        Incident(id=102, outlet="Azure",       severity="High",   title="Cold pass lamp failure", status="OPEN"),
        Incident(id=103, outlet="Spa",         severity="Low",    title="Missing oils in Room 2", status="IN_PROGRESS"),
    ]

    # Sales (7-day window, top seller = High Tea (Gazebo) qty=126)
    today = date.today()
    sales = [
        SaleItem(name="High Tea (Gazebo)", qty=126, sold_on=today - timedelta(days=1)),
        SaleItem(name="Dinner & Movie",    qty=89,  sold_on=today - timedelta(days=2)),
        SaleItem(name="Oyster Special",    qty=74,  sold_on=today - timedelta(days=3)),
    ]

    db.add_all(handovers + incidents + sales)
    db.commit()

def main():
    # Create tables if missing
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ensure_seed(db)
    finally:
        db.close()

if __name__ == "__main__":
    main()
