from __future__ import annotations

# feat(auth): login/logout/me with JWT cookie (and bearer for dev)

from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import User, UserTenant, Tenant
from ..security import verify_password, create_access_token
from ..deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _user_payload(db: Session, user: User) -> Dict[str, Any]:
    links = (
        db.query(UserTenant, Tenant)
        .join(Tenant, Tenant.id == UserTenant.tenant_id)
        .filter(UserTenant.user_id == user.id)
        .all()
    )
    tenants = [
        {"id": t.id, "name": t.name, "slug": t.slug, "role": ut.role}
        for ut, t in links
    ]
    return {"id": user.id, "email": user.email, "tenants": tenants}


@router.post("/login")
def login(payload: Dict[str, Any], response: Response, db: Session = Depends(get_db)):
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""
    user = db.query(User).filter(User.email == email, User.is_active == 1).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    # HTTP-only cookie for prod; dev can use bearer
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="none",
        path="/",
    )
    return {"user": _user_payload(db, user), "token": token}


@router.post("/logout", status_code=204)
def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    return Response(status_code=204)


@router.get("/me")
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _user_payload(db, user)
