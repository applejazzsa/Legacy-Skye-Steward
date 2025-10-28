# backend/app/api/analytics.py

from datetime import date
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, literal, or_
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import SaleItem, RevenueEntry
from sqlalchemy import text
from ..db import engine
from ..deps import get_active_tenant

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

# --- simple name-based classification (no category field required) ---
_BEVERAGE_HINTS = {
    "beer", "lager", "ipa", "stout", "ale", "cider",
    "wine", "merlot", "cab", "cabernet", "pinot", "chardonnay",
    "cocktail", "margarita", "mojito", "martini", "negroni",
    "soda", "cola", "sprite", "pop",
    "coffee", "latte", "cappuccino", "americano", "espresso",
    "tea", "matcha", "chai",
    "juice", "water", "sparkling", "lemonade"
}

def _is_beverage(name: Optional[str]) -> bool:
    if not name:
        return False
    n = name.lower()
    return any(h in n for h in _BEVERAGE_HINTS)

def _amount_expr():
    """
    Returns a SQLAlchemy column/expression for 'revenue' on a SaleItem.
    Tries these in order:
      0) explicit revenue column
      1) qty * <unit price> if any of: unit_price, unitprice, rate, price
      2) a total-like column if any of: amount, total, total_amount, total_price, line_total, subtotal
      3) literal(0.0) as last resort (prevents crashes on unknown schemas)
    """
    # prefer explicit revenue field if present
    if hasattr(SaleItem, "revenue"):
        return func.coalesce(getattr(SaleItem, "revenue"), 0)
    # candidates for unit price (multiply by qty)
    for unit_col in ("unit_price", "unitprice", "rate", "price"):
        if hasattr(SaleItem, unit_col):
            return func.coalesce(getattr(SaleItem, "qty"), 0) * func.coalesce(getattr(SaleItem, unit_col), 0)

    # candidates that already represent a line total
    for total_col in ("amount", "total", "total_amount", "total_price", "line_total", "subtotal"):
        if hasattr(SaleItem, total_col):
            return func.coalesce(getattr(SaleItem, total_col), 0)

    # last resort: zero (keeps endpoints alive even if schema is different)
    return literal(0.0)


@router.get("/kpi-summary")
def kpi_summary(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    target: float = Query(10_000),
    db: Session = Depends(get_db),
    tenant = Depends(get_active_tenant),
):
    """
    Returns aggregate revenue totals and a food/beverage split.
    No reliance on a 'category' column; uses name heuristics.
    """
    amount = _amount_expr()

    q = db.query(
        SaleItem.name.label("name"),
        amount.label("amount"),
    )

    # multi-tenant guard: try both legacy slug and numeric id casting
    q = q.filter(or_(SaleItem.tenant_id == str(getattr(tenant, 'slug', '') or ''), SaleItem.tenant_id == str(getattr(tenant, 'id', ''))))
    if date_from:
        q = q.filter(SaleItem.sold_on >= date_from)
    if date_to:
        q = q.filter(SaleItem.sold_on <= date_to)

    total = 0.0
    food = 0.0
    beverage = 0.0

    for name, amt in q.all():
        val = float(amt or 0.0)
        total += val
        if _is_beverage(name):
            beverage += val
        else:
            food += val

    progress = (total / float(target)) if target else 0.0

    return {
        "target": float(target),
        "total": float(total),
        "food": float(food),
        "beverage": float(beverage),
        "progress": float(progress),
    }


@router.get("/revenue-trend")
def revenue_trend(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    tenant = Depends(get_active_tenant),
):
    """
    Daily revenue totals grouped by sold_on date.
    """
    amount = _amount_expr()

    q = db.query(
        func.date(SaleItem.sold_on).label("d"),
        func.sum(amount).label("t"),
    )

    q = q.filter(or_(SaleItem.tenant_id == str(getattr(tenant, 'slug', '') or ''), SaleItem.tenant_id == str(getattr(tenant, 'id', ''))))
    if date_from:
        q = q.filter(SaleItem.sold_on >= date_from)
    if date_to:
        q = q.filter(SaleItem.sold_on <= date_to)

    q = q.group_by(func.date(SaleItem.sold_on)).order_by(func.date(SaleItem.sold_on))

    rows = q.all()
    return [{"date": str(d), "total": float(t or 0.0)} for d, t in rows]


@router.get("/top-items")
def top_items(
    limit: int = Query(5, ge=1, le=50),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    tenant = Depends(get_active_tenant),
):
    """
    Top selling items by revenue within an optional date range.
    """
    amount = _amount_expr()

    q = db.query(
        SaleItem.name.label("name"),
        func.sum(func.coalesce(getattr(SaleItem, "qty"), 0)).label("units"),
        func.sum(amount).label("revenue"),
    )

    q = q.filter(or_(SaleItem.tenant_id == str(getattr(tenant, 'slug', '') or ''), SaleItem.tenant_id == str(getattr(tenant, 'id', ''))))
    if date_from:
        q = q.filter(SaleItem.sold_on >= date_from)
    if date_to:
        q = q.filter(SaleItem.sold_on <= date_to)

    q = (
        q.group_by(SaleItem.name)
         .order_by(func.sum(amount).desc())
         .limit(limit)
    )

    rows = q.all()
    return [
        {
            "name": name or "",
            "units_sold": int(units or 0),
            "revenue": float(rev or 0.0),
        }
        for name, units, rev in rows
    ]


@router.get("/hotel-kpis")
def hotel_kpis(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    tenant = Depends(get_active_tenant),
) -> Dict[str, Any]:
    """
    Returns Occupancy%, ADR, RevPAR derived from room_bookings and rooms.
    Uses room_bookings.amount as room revenue; counts a booking as 1 room-night per 24h slice approximation based on start_at for simplicity.
    """
    where = ["tenant_id = :t"]
    params: Dict[str, Any] = {"t": str(getattr(tenant, 'slug', '') or getattr(tenant, 'id'))}
    if date_from:
        where.append("date(start_at) >= :df"); params["df"] = str(date_from)
    if date_to:
        where.append("date(start_at) <= :dt"); params["dt"] = str(date_to)
    sql_rooms = "SELECT COUNT(*) AS c FROM rooms WHERE tenant_id=:t"
    sql_book = f"SELECT COUNT(*) AS n, COALESCE(SUM(amount),0) AS rev FROM room_bookings WHERE {' AND '.join(where)}"
    with engine.begin() as conn:
        total_rooms = conn.execute(text(sql_rooms), {"t": params["t"]}).scalar() or 0
        row = conn.execute(text(sql_book), params).mappings().first() or {"n": 0, "rev": 0}
    rooms_sold = int(row["n"] or 0)
    room_rev = float(row["rev"] or 0.0)
    occ = (rooms_sold / total_rooms * 100.0) if total_rooms else 0.0
    adr = (room_rev / rooms_sold) if rooms_sold else 0.0
    revpar = (occ / 100.0) * adr
    return {
        "rooms_total": int(total_rooms),
        "rooms_sold": int(rooms_sold),
        "room_revenue": float(room_rev),
        "occupancy": float(occ),
        "adr": float(adr),
        "revpar": float(revpar),
    }


@router.get("/dept-split")
def dept_split(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    tenant = Depends(get_active_tenant),
) -> List[Dict[str, Any]]:
    """
    Department split: Rooms, F&B, Spa, Conference.
    Rooms from room_bookings.amount; F&B from SaleItem revenue heuristic; others 0 for now.
    """
    tslug = str(getattr(tenant, 'slug', '') or getattr(tenant, 'id'))
    # Rooms
    where = ["tenant_id = :t"]; params: Dict[str, Any] = {"t": tslug}
    if date_from: where.append("date(start_at) >= :df"); params["df"] = str(date_from)
    if date_to: where.append("date(start_at) <= :dt"); params["dt"] = str(date_to)
    with engine.begin() as conn:
        rooms_sum = conn.execute(text(f"SELECT COALESCE(SUM(amount),0) FROM room_bookings WHERE {' AND '.join(where)}"), params).scalar() or 0.0
    # F&B from SaleItem
    amount = _amount_expr()
    db = next(get_db())  # type: ignore
    try:
        q = db.query(func.sum(amount))
        q = q.filter(or_(SaleItem.tenant_id == tslug, SaleItem.tenant_id == str(getattr(tenant,'id',''))))
        if date_from: q = q.filter(SaleItem.sold_on >= date_from)
        if date_to: q = q.filter(SaleItem.sold_on <= date_to)
        fnb = float(q.scalar() or 0.0)
    finally:
        db.close()
    # Spa from spa_visits if an amount-like column exists
    with engine.begin() as conn:
        spa_cols = {r[1] for r in conn.execute(text("PRAGMA table_info(spa_visits)"))} if conn else set()
        spa_sum = 0.0
        if "amount" in spa_cols:
            where_s = ["tenant_id = :t"]; p2 = {"t": tslug}
            if date_from: where_s.append("date(when_ts) >= :df"); p2["df"] = str(date_from)
            if date_to: where_s.append("date(when_ts) <= :dt"); p2["dt"] = str(date_to)
            try:
                spa_sum = float(conn.execute(text(f"SELECT COALESCE(SUM(amount),0) FROM spa_visits WHERE {' AND '.join(where_s)}"), p2).scalar() or 0.0)
            except Exception:
                spa_sum = 0.0
    # Conference from revenue_entries where category='Conference'
    with engine.begin() as conn:
        conf = float(conn.execute(text("SELECT COALESCE(SUM(amount_cents)/100.0,0) FROM revenue_entries WHERE tenant_id=:t AND lower(category)='conference'"), {"t": tslug}).scalar() or 0.0)
    return [
        {"label": "Rooms", "value": float(rooms_sum)},
        {"label": "F&B", "value": float(fnb)},
        {"label": "Spa", "value": float(spa_sum)},
        {"label": "Conference", "value": float(conf)},
    ]
