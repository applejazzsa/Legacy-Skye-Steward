from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from ..db import Base, engine, SessionLocal
from ..models import Handover, Incident, SaleItem, RevenueEntry

def seed_for_tenant(db: Session, tenant: str):
    if db.query(Handover).filter(Handover.tenant_id == tenant).count() == 0:
        db.add_all([
            Handover(date=date(2025, 10, 16), tenant_id=tenant, outlet="Cafe Grill",   shift="PM", covers=78),
            Handover(date=date(2025, 10, 16), tenant_id=tenant, outlet="Leopard Bar",  shift="PM", covers=54),
            Handover(date=date(2025, 10, 17), tenant_id=tenant, outlet="Azure Restaurant", shift="AM", covers=63),
        ])

    if db.query(Incident).filter(Incident.tenant_id == tenant).count() == 0:
        db.add_all([
            Incident(tenant_id=tenant, outlet="Cafe Grill", severity="Medium", title="Card machine offline", status="OPEN"),
            Incident(tenant_id=tenant, outlet="Azure", severity="High", title="Cold pass lamp failure", status="OPEN"),
            Incident(tenant_id=tenant, outlet="Spa", severity="Low", title="Missing oils in Room 2", status="IN_PROGRESS"),
        ])

    if db.query(SaleItem).filter(SaleItem.tenant_id == tenant).count() == 0:
        today = date.today()
        db.add_all([
            SaleItem(tenant_id=tenant, name="High Tea (Gazebo)", qty=126, sold_on=today - timedelta(days=1)),
            SaleItem(tenant_id=tenant, name="Dinner & Movie",    qty=89,  sold_on=today - timedelta(days=2)),
            SaleItem(tenant_id=tenant, name="Oyster Special",    qty=74,  sold_on=today - timedelta(days=3)),
        ])

    if db.query(RevenueEntry).filter(RevenueEntry.tenant_id == tenant).count() == 0:
        now = datetime.utcnow()
        db.add_all([
            RevenueEntry(tenant_id=tenant, outlet="Azure Restaurant",  category="Food",     amount_cents=78_500_00, occurred_at=now - timedelta(days=1), description="Dinner service"),
            RevenueEntry(tenant_id=tenant, outlet="Leopard Bar",       category="Beverage", amount_cents=32_000_00, occurred_at=now - timedelta(days=2), description="Cocktails & wine"),
            RevenueEntry(tenant_id=tenant, outlet="Cafe Grill",        category="Food",     amount_cents=15_900_00, occurred_at=now - timedelta(days=3), description="Lunch rush"),
            RevenueEntry(tenant_id=tenant, outlet="Azure Restaurant",  category="Beverage", amount_cents=5_200_00,  occurred_at=now - timedelta(days=3), description="Pairings"),
            RevenueEntry(tenant_id=tenant, outlet="Spa",               category="Other",    amount_cents=4_950_00,  occurred_at=now - timedelta(days=4), description="Tea add-on"),
        ])

def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # seed two tenants
        seed_for_tenant(db, "legacy")
        seed_for_tenant(db, "oceanview")
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    main()
