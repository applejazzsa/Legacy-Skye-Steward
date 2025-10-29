from __future__ import annotations

from datetime import date, datetime, timedelta
import random
from typing import Dict, Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Product, Sale, SaleItem, Vehicle, VehicleBooking
from ..deps import get_active_tenant, require_role

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/seed-all", dependencies=[Depends(require_role("manager"))])
def seed_all(
    days: int = Query(60, ge=1, le=365),
    db: Session = Depends(get_db),
    tenant = Depends(get_active_tenant),
) -> Dict[str, Any]:
    random.seed(42)
    start = date.today() - timedelta(days=days - 1)

    catalog = [
        ("Margherita", "Food", 120.0),
        ("Ribeye", "Food", 240.0),
        ("Truffle Pasta", "Food", 190.0),
        ("Sea Bass", "Food", 220.0),
        ("IPA", "Beverage", 58.0),
        ("Coke", "Beverage", 28.0),
        ("Merlot", "Beverage", 95.0),
    ]

    # upsert products
    name_to_id: Dict[str, int] = {}
    for name, cat, _price in catalog:
        p = db.query(Product).filter(Product.tenant_id == tenant.id, Product.name == name).first()
        if not p:
            p = Product(tenant_id=tenant.id, name=name, category=cat)
            db.add(p)
            db.flush()
        name_to_id[name] = p.id

    total_rows = 0
    for i in range(days):
        d = start + timedelta(days=i)
        for name, cat, price in catalog:
            qty = max(0, int(random.gauss(40 if cat == "Food" else 25, 10)))
            if qty == 0:
                continue
            sale = Sale(tenant_id=tenant.id, date=d, total=0.0, source="seed")
            db.add(sale)
            db.flush()
            revenue = float(qty * price)
            item = SaleItem(
                tenant_id=tenant.id,
                sale_id=sale.id,
                product_id=name_to_id.get(name),
                name=name,
                category=cat,
                qty=qty,
                unit_price=price,
                revenue=revenue,
                sold_on=d,
            )
            sale.total = revenue
            db.add(item)
            total_rows += 1
        if i % 7 == 0:
            db.commit()
    db.commit()
    # Seed some vehicles
    vehicles = [
        ("CA 123-456", "Toyota", "Quantum"),
        ("CA 789-012", "VW", "Caravelle"),
        ("CA 345-678", "Hyundai", "H1"),
    ]
    for reg, make, model in vehicles:
        if not db.query(Vehicle).filter(Vehicle.tenant_id == tenant.id, Vehicle.reg == reg).first():
            db.add(Vehicle(tenant_id=tenant.id, reg=reg, make=make, model=model, status="AVAILABLE"))
    db.commit()

    # Seed a couple of bookings in the last week
    today = date.today()
    vrows = db.query(Vehicle).filter(Vehicle.tenant_id == tenant.id).all()
    for vi, v in enumerate(vrows[:2]):
        s = datetime.combine(today - timedelta(days=2 - vi), datetime.min.time()).replace(hour=9)
        e = s + timedelta(hours=2)
        if not db.query(VehicleBooking).filter(
            VehicleBooking.tenant_id == tenant.id,
            VehicleBooking.vehicle_id == v.id,
            VehicleBooking.start_at == s,
        ).first():
            db.add(VehicleBooking(tenant_id=tenant.id, vehicle_id=v.id, booked_by="Seeder", start_at=s, end_at=e, purpose="Shuttle"))
    db.commit()

    return {"ok": True, "rows": total_rows, "days": days, "vehicles": len(vrows)}
