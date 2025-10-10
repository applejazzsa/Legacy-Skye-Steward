# app/crud.py
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app import models, schemas

# ------------- Create -------------

def create_handover(db: Session, payload: schemas.HandoverCreate) -> models.Handover:
    data = payload.model_dump()
    obj = models.Handover(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

# ------------- Read -------------

def get_handover(db: Session, handover_id: int) -> Optional[models.Handover]:
    return db.get(models.Handover, handover_id)

def list_handovers(
    db: Session,
    outlet: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> List[models.Handover]:
    q = db.query(models.Handover)
    if outlet:
        q = q.filter(models.Handover.outlet == outlet)
    if start_date:
        try:
            sdt = datetime.fromisoformat(start_date)
            q = q.filter(models.Handover.date >= sdt)
        except Exception:
            pass
    if end_date:
        try:
            edt = datetime.fromisoformat(end_date)
            q = q.filter(models.Handover.date <= edt)
        except Exception:
            pass
    return q.order_by(models.Handover.date.desc()).offset(skip).limit(limit).all()

# ------------- Update -------------

def update_handover(db: Session, handover_id: int, payload: schemas.HandoverUpdate) -> Optional[models.Handover]:
    obj = db.get(models.Handover, handover_id)
    if not obj:
        return None
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

# ------------- Delete -------------

def delete_handover(db: Session, handover_id: int) -> bool:
    obj = db.get(models.Handover, handover_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True
