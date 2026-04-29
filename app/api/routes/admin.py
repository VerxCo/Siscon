from fastapi import APIRouter, Depends

from app.api.deps import require_roles

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/only")
def admin_only(current_user=Depends(require_roles("admin"))) -> dict:
    return {
        "message": "Acesso permitido",
        "user_id": current_user.user_id,
        "role": current_user.role,
    }
