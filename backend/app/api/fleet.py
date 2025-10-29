from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Vehicle, VehicleBooking
from ..tenant import get_tenant
from ..deps import require_role

router = APIRouter(prefix="/api/fleet", tags=["fleet"])


def serialize(obj) -> Dict[str, Any]:
    return {c: getattr(obj, c) for c in obj.__table__.columns.keys()}


@router.get("/vehicles", response_model=list[dict])
def list_vehicles(db: Session = Depends(get_db), tenant: str = Depends(get_tenant)):
    rows = (
        db.query(Vehicle)
        .filter(Vehicle.tenant_id == tenant)
        .order_by(Vehicle.reg)
        .all()
    )
    return [serialize(x) for x in rows]


@router.post("/vehicles", response_model=dict)
def create_vehicle(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    tenant: str = Depends(get_tenant),
    _role_ok: bool = Depends(require_role("manager")),
):
    reg = (payload.get("reg") or "").strip().upper()
    make = (payload.get("make") or "").strip()
    model = (payload.get("model") or "").strip()
    if not reg or not make or not model:
        raise HTTPException(status_code=400, detail="reg, make, model required")
    # ensure unique reg per tenant
    exists = db.query(Vehicle).filter(Vehicle.tenant_id == tenant, Vehicle.reg == reg).first()
    if exists:
        raise HTTPException(status_code=400, detail="vehicle already exists")
    row = Vehicle(tenant_id=tenant, reg=reg, make=make, model=model, status="AVAILABLE")
    db.add(row)
    db.commit()
    db.refresh(row)
    return serialize(row)


@router.patch("/vehicles/{vehicle_id}", response_model=dict)
def update_vehicle(
    vehicle_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    tenant: str = Depends(get_tenant),
    _role_ok: bool = Depends(require_role("manager")),
):
    row = db.query(Vehicle).filter(Vehicle.id == vehicle_id, Vehicle.tenant_id == tenant).first()
    if not row:
        raise HTTPException(status_code=404, detail="vehicle not found")
    if "reg" in payload and payload["reg"]:
        row.reg = str(payload["reg"]).strip().upper()
    if "make" in payload and payload["make"] is not None:
        row.make = str(payload["make"]).strip()
    if "model" in payload and payload["model"] is not None:
        row.model = str(payload["model"]).strip()
    if "status" in payload and payload["status"]:
        row.status = str(payload["status"]).strip().upper()
    db.add(row)
    db.commit()
    db.refresh(row)
    return serialize(row)


@router.post("/bookings", response_model=dict)
def create_booking(payload: Dict[str, Any], db: Session = Depends(get_db), tenant: str = Depends(get_tenant)):
    vehicle_id = int(payload.get("vehicle_id") or 0)
    if not vehicle_id:
        raise HTTPException(status_code=400, detail="vehicle_id required")
    start_at = datetime.fromisoformat(payload.get("start_at"))
    end_at = datetime.fromisoformat(payload.get("end_at"))
    # prevent overlaps for the same vehicle
    overlap = (
        db.query(VehicleBooking)
        .filter(
            VehicleBooking.tenant_id == tenant,
            VehicleBooking.vehicle_id == vehicle_id,
            VehicleBooking.start_at < end_at,
            VehicleBooking.end_at > start_at,
        )
        .first()
    )
    if overlap:
        raise HTTPException(status_code=400, detail="overlapping booking exists")
    row = VehicleBooking(
        tenant_id=tenant,
        vehicle_id=vehicle_id,
        booked_by=payload.get("booked_by") or "Unknown",
        start_at=start_at,
        end_at=end_at,
        purpose=payload.get("purpose"),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return serialize(row)


@router.get("/bookings", response_model=list[dict])
def list_bookings(
    db: Session = Depends(get_db),
    tenant: str = Depends(get_tenant),
    limit: int = Query(50, ge=1, le=500),
    vehicle_id: Optional[int] = Query(default=None),
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
):
    q = db.query(VehicleBooking).filter(VehicleBooking.tenant_id == tenant)
    if vehicle_id:
        q = q.filter(VehicleBooking.vehicle_id == vehicle_id)
    if date_from:
        q = q.filter(VehicleBooking.start_at >= date_from)
    if date_to:
        q = q.filter(VehicleBooking.start_at <= date_to)
    rows = q.order_by(VehicleBooking.start_at.desc()).limit(limit).all()
    return [serialize(x) for x in rows]
