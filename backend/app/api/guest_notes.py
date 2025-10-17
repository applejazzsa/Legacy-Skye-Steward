from fastapi import APIRouter
router = APIRouter(prefix="/api", tags=["guest-notes"])

@router.get("/guest-notes")
def list_guest_notes():
    return {"total": 0, "items": []}
