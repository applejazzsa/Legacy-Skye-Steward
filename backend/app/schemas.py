from __future__ import annotations

# feat(auth): pydantic schemas (minimal for responses)

from pydantic import BaseModel
from typing import List, Optional


class TenantLink(BaseModel):
    id: int
    name: str
    slug: str
    role: str


class UserOut(BaseModel):
    id: int
    email: str
    tenants: List[TenantLink]


