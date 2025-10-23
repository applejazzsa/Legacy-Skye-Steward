# app/tenant.py
import os
from fastapi import Header, HTTPException, Depends

# Allowed tenants from env (comma-separated). Defaults to "legacy".
ALLOWED = set((os.getenv("ALLOWED_TENANTS") or "legacy").split(","))
ALLOWED = {t.strip().lower() for t in ALLOWED if t.strip()}

async def require_tenant(x_tenant: str = Header(..., alias="X-Tenant")) -> str:
    """
    Primary dependency: validate the X-Tenant header against ALLOWED_TENANTS.
    Returns the normalized tenant string.
    """
    t = (x_tenant or "").strip().lower()
    if t not in ALLOWED:
        raise HTTPException(status_code=400, detail=f"tenant not allowed: {t}")
    return t

# ---- Backwards compatibility ----
# older modules import `get_tenant`; keep it as an alias to `require_tenant`
get_tenant = require_tenant

# convenience list you can attach to routers: dependencies=tenant_header_dependable
tenant_header_dependable = [Depends(require_tenant)]
