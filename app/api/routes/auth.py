from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.api.schemas.auth import LoginRequest, LoginResponse
from app.repositories.user_repository import get_user_by_email
from app.services.auth_service import AuthenticationError, authenticate_user, issue_token_for_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    user = get_user_by_email(payload.email)

    try:
        authenticated_user = authenticate_user(user, payload.senha)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    token = issue_token_for_user(user)

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user_id=authenticated_user.user_id,
        nome=user.nome,
        role=authenticated_user.role,
    )


@router.get("/me")
def me(current_user=Depends(get_current_user)) -> dict:
    return {
        "user_id": current_user.user_id,
        "role": current_user.role,
        "is_active": current_user.is_active,
    }
