from __future__ import annotations

import os
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Handover, Incident, RevenueEntry
from ..tenant import get_tenant

router = APIRouter(prefix="/api/copilot", tags=["copilot"])


def _collect_context(db: Session, tenant: str, date_from: Optional[date], date_to: Optional[date]) -> Dict[str, Any]:
    q_hand = db.query(Handover).filter(Handover.tenant_id == tenant)
    if date_from:
        q_hand = q_hand.filter(Handover.date >= date_from)
    if date_to:
        q_hand = q_hand.filter(Handover.date <= date_to)
    handovers = q_hand.order_by(Handover.date.desc()).limit(20).all()

    q_inc = db.query(Incident).filter(Incident.tenant_id == tenant)
    inc = q_inc.order_by(Incident.created_at.desc()).limit(20).all()

    q_rev = db.query(RevenueEntry).filter(RevenueEntry.tenant_id == tenant)
    if date_from:
        q_rev = q_rev.filter(RevenueEntry.occurred_at >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        q_rev = q_rev.filter(RevenueEntry.occurred_at <= datetime.combine(date_to, datetime.max.time()))
    rev = q_rev.order_by(RevenueEntry.occurred_at.desc()).limit(100).all()

    total_cents = sum(getattr(r, "amount_cents", 0) or 0 for r in rev)
    return {
        "handovers": [
            {"date": str(getattr(h, "date", "")), "outlet": getattr(h, "outlet", ""), "shift": getattr(h, "shift", ""),
             "covers": getattr(h, "covers", 0)}
            for h in handovers
        ],
        "incidents": [
            {"title": i.title, "severity": i.severity, "status": i.status, "created_at": i.created_at.isoformat()}
            for i in inc
        ],
        "revenue_summary": {"total_r": round(total_cents / 100.0, 2)},
    }


@router.get("/summary")
def copilot_summary(
    db: Session = Depends(get_db),
    tenant: str = Depends(get_tenant),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
):
    """Return a concise English summary of the last period.

    If OPENAI_API_KEY is present, we attempt to generate a summary using the
    Chat Completions API. If missing or any error occurs, we fall back to a
    deterministic rule-based summary that highlights: total revenue estimate,
    incident counts by severity, and most recent handover details.
    """
    ctx = _collect_context(db, tenant, date_from, date_to)

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            import requests

            system = (
                "You are Steward Copilot. Summarize hospitality operations with actionable bullets. "
                "Tone: concise, operational, and helpful. Suggest 2-3 next actions."
            )
            user = str(ctx)
            r = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    "temperature": 0.2,
                    "max_tokens": 250,
                },
                timeout=20,
            )
            r.raise_for_status()
            data = r.json()
            text = data["choices"][0]["message"]["content"].strip()
            return {"summary": text, "source": "openai"}
        except Exception as e:
            # fall through to rule based below
            pass

    # Fallback: simple rule-based summary
    inc = ctx.get("incidents", [])
    sev_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for i in inc:
        sev_counts[i.get("severity", "").upper()] = sev_counts.get(i.get("severity", "").upper(), 0) + 1
    hov = ctx.get("handovers", [])
    last = hov[0] if hov else {}
    total_r = ctx.get("revenue_summary", {}).get("total_r", 0)
    summary = (
        f"Estimated revenue R {total_r:,.0f}. Incidents — High: {sev_counts.get('HIGH',0)}, "
        f"Medium: {sev_counts.get('MEDIUM',0)}, Low: {sev_counts.get('LOW',0)}. "
        f"Last handover: {last.get('date','n/a')} {last.get('shift','')} at {last.get('outlet','')}, "
        f"covers: {last.get('covers','0')}. Actions: review HIGH incidents; confirm stock; verify morning prep."
    )
    return {"summary": summary, "source": "rule"}

