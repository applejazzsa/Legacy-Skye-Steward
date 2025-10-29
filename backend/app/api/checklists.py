from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ChecklistTemplate, ChecklistResponse
from ..tenant import get_tenant

router = APIRouter(prefix="/api/checklists", tags=["checklists"])


def _serialize(obj) -> Dict[str, Any]:
    out = {c: getattr(obj, c) for c in obj.__table__.columns.keys()}
    # decode JSON text fields for client convenience
    if "schema_json" in out and isinstance(out["schema_json"], str):
        try:
            out["schema"] = json.loads(out.pop("schema_json"))
        except Exception:
            out["schema"] = {}
    if "answers_json" in out and isinstance(out["answers_json"], str):
        try:
            out["answers"] = json.loads(out.pop("answers_json"))
        except Exception:
            out["answers"] = {}
    return out


@router.get("/templates", response_model=list[dict])
def list_templates(db: Session = Depends(get_db), tenant: str = Depends(get_tenant)):
    rows = (
        db.query(ChecklistTemplate)
        .filter(ChecklistTemplate.tenant_id == tenant)
        .order_by(ChecklistTemplate.created_at.desc())
        .limit(50)
        .all()
    )
    return [_serialize(x) for x in rows]


@router.post("/templates", response_model=dict)
def create_template(payload: Dict[str, Any], db: Session = Depends(get_db), tenant: str = Depends(get_tenant)):
    name = payload.get("name") or "Untitled"
    schema = payload.get("schema") or {}
    row = ChecklistTemplate(tenant_id=tenant, name=name, schema_json=json.dumps(schema))
    db.add(row)
    db.commit()
    db.refresh(row)
    return _serialize(row)


@router.post("/responses", response_model=dict)
def submit_response(payload: Dict[str, Any], db: Session = Depends(get_db), tenant: str = Depends(get_tenant)):
    template_id = int(payload.get("template_id") or 0)
    if not template_id:
        raise HTTPException(status_code=400, detail="template_id required")
    answers = payload.get("answers") or {}
    row = ChecklistResponse(
        tenant_id=tenant,
        template_id=template_id,
        filled_by=payload.get("filled_by"),
        location=payload.get("location"),
        answers_json=json.dumps(answers),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _serialize(row)

