# backend/app/api/analytics.py

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, literal
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import SaleItem

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
      1) qty * <unit price> if any of: unit_price, unitprice, rate, price
      2) a total-like column if any of: amount, total, total_amount, total_price, line_total, subtotal
      3) literal(0.0) as last resort (prevents crashes on unknown schemas)
    """
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
):
    """
    Daily revenue totals grouped by sold_on date.
    """
    amount = _amount_expr()

    q = db.query(
        func.date(SaleItem.sold_on).label("d"),
        func.sum(amount).label("t"),
    )

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
