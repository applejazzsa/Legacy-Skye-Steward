from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

# Import your routers
from .api import analytics
from .api import handover
from .api import incidents
from .api import copilot
from .api import checklists
from .api import fleet
from .api import capa
from .api import guest_notes
from .api import spa
from .api import digest
from .api import auth
from .deps import get_current_user, get_active_tenant
from .api import uploads
from .api import admin
from .api import rooms
from .api import events
from .api import targets
from .api import finance

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
app.include_router(auth.router)  # public auth routes

# Protected includes: require auth + tenant access
protected_deps = [Depends(get_current_user), Depends(get_active_tenant)]
app.include_router(analytics.router, dependencies=protected_deps)                    # already has prefix="/api/analytics"
app.include_router(handover.router,  prefix="/api/handover", dependencies=protected_deps)
app.include_router(incidents.router, prefix="/api/incidents", dependencies=protected_deps)
app.include_router(copilot.router, dependencies=protected_deps)
app.include_router(checklists.router, dependencies=protected_deps)
app.include_router(fleet.router, dependencies=protected_deps)
app.include_router(capa.router, dependencies=protected_deps)
app.include_router(guest_notes.router, dependencies=protected_deps)
app.include_router(spa.router, dependencies=protected_deps)
app.include_router(digest.router, dependencies=protected_deps)
app.include_router(uploads.router, dependencies=protected_deps)
app.include_router(admin.router, dependencies=protected_deps)
app.include_router(rooms.router, dependencies=protected_deps)
app.include_router(events.router, dependencies=protected_deps)
app.include_router(targets.router, dependencies=protected_deps)
app.include_router(finance.router, dependencies=protected_deps)

@app.get("/healthz")
def healthz():
    return {"ok": True}
