from __future__ import annotations
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Handover, GuestNote

def list_handovers(db: Session) -> List[Handover]:
    stmt = select(Handover).order_by(Handover.date.desc())
    return list(db.scalars(stmt).all())

def list_guest_notes(db: Session) -> List[GuestNote]:
    stmt = select(GuestNote).order_by(GuestNote.created_at.desc())
    return list(db.scalars(stmt).all())
