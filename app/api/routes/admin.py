from fastapi import APIRouter, Security

from app.api.deps import authorize

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/only")
def admin_only(current_user=Security(authorize("admin"))) -> dict:
    return {
        "message": "Acesso permitido",
        "user_id": current_user.user_id,
        "role": current_user.role,
    }
