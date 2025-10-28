from __future__ import annotations

# feat(seed): create demo tenant, users, and products; auto-create auth tables if missing

from sqlalchemy.orm import Session
from sqlalchemy import text
from ..db import SessionLocal, engine
from ..models import Tenant, User, UserTenant, Product
from ..security import hash_password

DDL = """
CREATE TABLE IF NOT EXISTS tenants (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'ZAR',
    created_at DATETIME
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_tenants_slug ON tenants(slug);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users(email);

CREATE TABLE IF NOT EXISTS user_tenants (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    tenant_id INTEGER NOT NULL,
    role TEXT NOT NULL DEFAULT 'staff',
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_user_tenant ON user_tenants(user_id, tenant_id);
CREATE INDEX IF NOT EXISTS ix_user_tenant_user ON user_tenants(user_id);
CREATE INDEX IF NOT EXISTS ix_user_tenant_tenant ON user_tenants(tenant_id);
"""

def ensure_auth_tables():
    with engine.begin() as conn:
        for stmt in DDL.split(";"):
            s = stmt.strip()
            if s:
                conn.execute(text(s))

def run():
    ensure_auth_tables()

    db: Session = SessionLocal()
    try:
        t = db.query(Tenant).filter(Tenant.slug == "legacy").first()
        if not t:
            t = Tenant(name="Legacy Skye", slug="legacy", currency="ZAR")
            db.add(t)
            db.commit(); db.refresh(t)

        def ensure_user(email: str, password: str, role: str):
            u = db.query(User).filter(User.email == email).first()
            if not u:
                u = User(email=email, password_hash=hash_password(password), is_active=1)
                db.add(u); db.commit(); db.refresh(u)
            ut = db.query(UserTenant).filter(UserTenant.user_id == u.id, UserTenant.tenant_id == t.id).first()
            if not ut:
                ut = UserTenant(user_id=u.id, tenant_id=t.id, role=role)
                db.add(ut); db.commit()

        ensure_user("owner@example.com", "password123", "owner")
        ensure_user("manager@example.com", "password123", "manager")
        ensure_user("staff@example.com", "password123", "staff")

        if db.query(Product).filter(Product.tenant_id == t.id).count() == 0:
            db.add_all([
                Product(tenant_id=t.id, name="Margherita", category="Food"),
                Product(tenant_id=t.id, name="IPA", category="Beverage"),
                Product(tenant_id=t.id, name="Ribeye", category="Food"),
            ])
            db.commit()

        print("seed_auth_demo: done")
    finally:
        db.close()

if __name__ == "__main__":
    run()