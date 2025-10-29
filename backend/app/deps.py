from __future__ import annotations

# feat(auth): dependencies for current user, tenant access and RBAC

from typing import Optional

from fastapi import Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session

from .db import get_db
from .models import User, UserTenant, Tenant
from .security import decode_token


def _get_token_from_request(request: Request) -> Optional[str]:
    # Prefer Authorization header
    auth = request.headers.get("Authorization") or ""
    if auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip()
    # Fallback to cookie
    token = request.cookies.get("access_token")
    return token


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = _get_token_from_request(request)
    payload = decode_token(token) if token else None
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = int(payload["sub"])  # issued by login
    user = db.query(User).filter(User.id == user_id, User.is_active == 1).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user


def get_active_tenant(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
) -> Tenant:
    # Accept either header or query string
    tid_param = x_tenant_id or request.query_params.get("tenant")
    if not tid_param:
        raise HTTPException(status_code=400, detail="tenant missing")
    # Support either numeric id or slug
    tenant = None
    if tid_param.isdigit():
        tenant = db.query(Tenant).filter(Tenant.id == int(tid_param)).first()
    if not tenant:
        tenant = db.query(Tenant).filter(Tenant.slug == tid_param).first()
    if not tenant:
        raise HTTPException(status_code=400, detail="tenant not found")

    # Verify membership
    membership = db.query(UserTenant).filter(UserTenant.user_id == current_user.id, UserTenant.tenant_id == tenant.id).first()
    if not membership:
        raise HTTPException(status_code=403, detail="no access to tenant")
    request.state.role = membership.role
    request.state.tenant_id = tenant.id
    request.state.tenant_slug = tenant.slug
    return tenant


_ROLE_RANK = {"staff": 1, "manager": 2, "owner": 3}


def require_role(min_role: str):
    def _dep(request: Request):
        role = getattr(request.state, "role", None)
        if not role or _ROLE_RANK.get(role, 0) < _ROLE_RANK.get(min_role, 0):
            raise HTTPException(status_code=403, detail="insufficient role")
        return True
    return _dep

