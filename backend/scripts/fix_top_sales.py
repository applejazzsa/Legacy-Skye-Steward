from __future__ import annotations
import json
from sqlalchemy import select
from app.db import get_session
from app.models import Handover

def fix() -> None:
    with get_session() as db:
        rows = db.execute(select(Handover)).scalars().all()
        for row in rows:
            if isinstance(row.top_sales, str):
                try:
                    parsed = json.loads(row.top_sales)
                    row.top_sales = parsed if isinstance(parsed, list) else [str(parsed)]
                except Exception:
                    row.top_sales = [row.top_sales]
        db.commit()
        print(f"Fixed {len(rows)} handover rows (if any were stringified).")

if __name__ == "__main__":
    fix()
