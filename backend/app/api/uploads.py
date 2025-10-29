from __future__ import annotations

import csv
import io
import json
import os
import uuid
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.background import BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

from ..db import get_db, SessionLocal
from ..models import Upload, Product, Sale, SaleItem
from ..deps import get_active_tenant, require_role

router = APIRouter(prefix="/api/uploads", tags=["uploads"])


def _env_upload_dir() -> str:
    d = os.getenv("UPLOAD_DIR", os.path.join(os.getcwd(), "data", "uploads"))
    os.makedirs(d, exist_ok=True)
    return d


def _parse_date(s: str) -> Optional[date]:
    try:
        return datetime.strptime(s.strip(), "%Y-%m-%d").date()
    except Exception:
        return None


def _to_float(s: Any) -> Optional[float]:
    try:
        v = float(str(s).strip())
        if v < 0:
            return None
        return v
    except Exception:
        return None


def _to_int(s: Any) -> Optional[int]:
    try:
        v = int(float(str(s).strip()))
        if v < 0:
            return None
        return v
    except Exception:
        return None


@router.get("/template/sales.csv", response_class=PlainTextResponse)
def template_sales_csv() -> str:
    return (
        "date,name,category,qty,unit_price\n"
        "2025-10-01,Margherita,Food,3,120\n"
        "2025-10-01,IPA,Beverage,2,58\n"
    )


@router.get("", response_model=Dict[str, Any], dependencies=[Depends(require_role("manager"))])
def list_uploads(db: Session = Depends(get_db), tenant = Depends(get_active_tenant), cursor: Optional[int] = None, limit: int = 20):
    try:
        q = db.query(Upload).filter(Upload.tenant_id == tenant.id).order_by(Upload.created_at.desc())
        items = q.limit(limit).all()
    except OperationalError:
        # Table might not exist if migrations haven't been applied yet; return empty list instead of 500
        items = []
    def _s(u: Upload) -> Dict[str, Any]:
        return {
            "id": u.id,
            "filename": u.filename,
            "status": u.status,
            "rows_total": u.rows_total,
            "rows_ok": u.rows_ok,
            "rows_failed": u.rows_failed,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "completed_at": u.completed_at.isoformat() if u.completed_at else None,
        }
    return {"items": [_s(x) for x in items]}


@router.get("/{upload_id}", response_model=Dict[str, Any], dependencies=[Depends(require_role("manager"))])
def get_upload(upload_id: int, db: Session = Depends(get_db), tenant = Depends(get_active_tenant)):
    try:
        u = db.query(Upload).filter(Upload.id == upload_id, Upload.tenant_id == tenant.id).first()
    except OperationalError:
        raise HTTPException(status_code=404, detail="upload not found")
    if not u:
        raise HTTPException(status_code=404, detail="upload not found")
    out: Dict[str, Any] = {
        "id": u.id, "filename": u.filename, "status": u.status,
        "rows_total": u.rows_total, "rows_ok": u.rows_ok, "rows_failed": u.rows_failed,
        "created_at": u.created_at.isoformat() if u.created_at else None,
        "completed_at": u.completed_at.isoformat() if u.completed_at else None,
    }
    if u.error_log:
        out["error_log"] = u.error_log
    return out


def _process_csv_stream(db: Session, tenant_id: int, file_bytes: bytes, mapping: Dict[str, str]) -> Tuple[int, int, List[str]]:
    reader = csv.DictReader(io.StringIO(file_bytes.decode("utf-8", errors="ignore")))
    required = ["date", "name", "category", "qty", "unit_price"]
    errors: List[str] = []
    ok = 0
    total = 0
    for row in reader:
        total += 1
        # map fields
        def g(key: str) -> str:
            src = mapping.get(key) or key
            return str(row.get(src, "")).strip()

        d = _parse_date(g("date"))
        name = g("name")
        category = g("category")
        qty = _to_int(g("qty"))
        unit_price = _to_float(g("unit_price"))
        sku = g("sku") if mapping.get("sku") else None
        external_ref = g("external_ref") if mapping.get("external_ref") else None

        if not (d and name and category in ("Food", "Beverage") and qty is not None and unit_price is not None):
            if len(errors) < 100:
                errors.append(f"Row {total}: invalid fields")
            continue

        # upsert product
        prod = None
        if sku:
            prod = db.query(Product).filter(Product.tenant_id == tenant_id, Product.sku == sku).first()
        if not prod:
            prod = db.query(Product).filter(Product.tenant_id == tenant_id, Product.name == name).first()
        if not prod:
            prod = Product(tenant_id=tenant_id, name=name, category=category, sku=sku)
            db.add(prod)
            db.flush()
        else:
            # keep latest category if provided
            if category and prod.category != category:
                prod.category = category

        sale = Sale(tenant_id=tenant_id, date=d, total=0, source="upload", external_ref=external_ref)
        db.add(sale)
        db.flush()

        revenue = float(qty * unit_price)
        item = SaleItem(
            tenant_id=tenant_id,
            sale_id=sale.id,
            product_id=prod.id if getattr(prod, "id", None) else None,
            name=name,
            category=category,
            qty=qty,
            unit_price=unit_price,
            revenue=revenue,
            sold_on=d,
        )
        db.add(item)
        sale.total = revenue
        ok += 1
        if total % 500 == 0:
            db.commit()
    db.commit()
    return total, ok, errors


def _process_upload(upload_id: int, tenant_id: int, file_path: str, mapping: Dict[str, str]) -> None:
    db = SessionLocal()
    try:
        u = db.query(Upload).filter(Upload.id == upload_id, Upload.tenant_id == tenant_id).first()
        if not u:
            return
        u.status = "processing"
        db.commit()
        with open(file_path, "rb") as f:
            content = f.read()
        total, ok, errors = _process_csv_stream(db, tenant_id, content, mapping)
        u.rows_total = total
        u.rows_ok = ok
        u.rows_failed = total - ok
        u.status = "done" if errors == [] else "failed"
        u.error_log = json.dumps(errors)
        u.completed_at = datetime.utcnow()
        db.commit()
    except Exception as e:
        try:
            u = db.query(Upload).filter(Upload.id == upload_id).first()
            if u:
                u.status = "failed"
                u.error_log = json.dumps([f"fatal: {e}"])
                u.completed_at = datetime.utcnow()
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


@router.post("/sales", response_model=Dict[str, Any], dependencies=[Depends(require_role("manager"))])
async def upload_sales(
    background: BackgroundTasks,
    file: UploadFile = File(...),
    mapping: str = Form("{}"),
    db: Session = Depends(get_db),
    tenant = Depends(get_active_tenant),
):
    try:
        mapping_obj = json.loads(mapping or "{}")
        if not isinstance(mapping_obj, dict):
            raise ValueError("mapping must be JSON object")
    except Exception:
        raise HTTPException(status_code=400, detail="invalid mapping json")

    filename = file.filename or f"upload_{uuid.uuid4().hex}.csv"
    upload_dir = _env_upload_dir()
    tenant_dir = os.path.join(upload_dir, str(tenant.id))
    os.makedirs(tenant_dir, exist_ok=True)
    dest_path = os.path.join(tenant_dir, filename)
    raw = await file.read()
    with open(dest_path, "wb") as out:
        out.write(raw)

    u = Upload(tenant_id=tenant.id, user_id=None, filename=filename, status="queued", rows_total=0, rows_ok=0, rows_failed=0, created_at=datetime.utcnow())
    db.add(u)
    db.commit()
    db.refresh(u)

    # background processing
    background.add_task(_process_upload, u.id, tenant.id, dest_path, mapping_obj)
    return {"upload_id": u.id}
