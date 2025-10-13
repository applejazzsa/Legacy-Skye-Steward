# Legacy Skye Steward Monorepo

End-to-end hospitality handover & analytics system featuring a FastAPI backend and a Next.js dashboard frontend. Follow the quick start below to get everything running locally on Windows PowerShell (with bash equivalents provided).

## Quick Start

1. **Backend (FastAPI + SQLite)**
   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate
   pip install -r requirements.txt
   copy .env.example .env
   alembic upgrade head
   python .\scripts\seed_demo.py
   python -m uvicorn app.main:app --reload --app-dir .
   ```

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   alembic upgrade head
   python ./scripts/seed_demo.py
   python -m uvicorn app.main:app --reload --app-dir .
   ```

2. **Frontend (Next.js Dashboard)**
   ```powershell
   cd frontend
   copy .env.local.example .env.local
   npm install
   npm run dev
   ```

   ```bash
   cd frontend
   cp .env.local.example .env.local
   npm install
   npm run dev
   ```

The API is available at http://127.0.0.1:8000 and the dashboard at http://localhost:3000.

## PowerShell Helpers

Set the API base and use the helper to post handovers quickly:

```powershell
$env:API_BASE = "http://127.0.0.1:8000"

function New-Handover {
  param(
    [string]$Outlet,[datetime]$Date,[string]$Shift,[string]$Period,
    [int]$Bookings,[int]$WalkIns,[int]$Covers,[double]$FoodRevenue,[double]$BeverageRevenue,[string[]]$TopSales
  )
  $dateIso = ($Date.ToUniversalTime()).ToString("s") + "Z"
  $payload = [ordered]@{
    outlet=$Outlet; date=$dateIso; shift=$Shift; period=$Period;
    bookings=$Bookings; walk_ins=$WalkIns; covers=$Covers;
    food_revenue=$FoodRevenue; beverage_revenue=$BeverageRevenue; top_sales=$TopSales
  } | ConvertTo-Json -Depth 5
  Invoke-RestMethod -Method POST -Uri "$env:API_BASE/api/handover" -Body $payload -ContentType "application/json"
}
```

Example usage:

```powershell
New-Handover -Outlet "Main Restaurant" -Date (Get-Date) -Shift "PM" -Period "DINNER" -Bookings 18 -WalkIns 6 -Covers 72 -FoodRevenue 5400 -BeverageRevenue 2100 -TopSales @("Chef's Special","Signature Cocktail")
```

## Verification Checklist

1. **Backend boots**
   - `alembic upgrade head` succeeds.
   - `python scripts/seed_demo.py` prints a success line.
   - `python -m uvicorn app.main:app --reload --app-dir .` serves at http://127.0.0.1:8000.
   - `GET /health` returns 200 with `{ "status": "healthy", ... }`.
2. **POST /api/handover works**
   - Using `New-Handover`, POST returns 200 and echoes fields.
   - `GET /api/handover` returns an array with at least the seeded records.
3. **Analytics endpoints**
   - `/api/analytics/top-items?limit=5` returns a non-empty list.
   - `/api/analytics/staff-praise?limit=5` returns a list (possibly empty if no guest notes yet).
   - `/api/analytics/kpi-summary?target=10000` returns the specified object with correct keys and numeric values.
4. **Frontend runs**
   - `npm install && npm run dev` compiles without Tailwind or casing errors.
   - Visiting http://localhost:3000 shows KPI cards, Top Items, Staff Praise, and a Recent Handovers table.
5. **Tests**
   - `pytest` in `/backend` passes all tests.

## Common Pitfalls

- **Windows path casing**: Use the same casing when opening folders (e.g. `C:\Dev\LegacySkyeSteward\...`). Changing casing mid-session can confuse the Node dev server.
- **Tailwind install**: If the frontend complains about missing Tailwind packages, run `npm i -D tailwindcss postcss autoprefixer`.
- **HTTP 422 errors**: Ensure request bodies contain valid JSON with ISO 8601 UTC dates (e.g. `2024-01-01T08:00:00Z`).
- **CORS issues**: Update `CORS_ORIGINS` in `backend/.env` if you serve the frontend from a different host/port.

Happy building!
