from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import your routers
from .api import analytics
from .api import handover
from .api import incidents

app = FastAPI(title="Legacy Skye Steward API")

# CORS for the Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- IMPORTANT: give each router a non-empty include prefix ---
app.include_router(analytics.router)                    # already has prefix="/api/analytics"
app.include_router(handover.router,  prefix="/api/handover")
app.include_router(incidents.router, prefix="/api/incidents")

@app.get("/healthz")
def healthz():
    return {"ok": True}
