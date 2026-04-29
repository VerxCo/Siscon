import uuid

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.auth import (
    build_authenticated_user,
    build_authenticated_user_from_profile,
)
from app.core.security import InvalidCredentialsError, parse_token_payload
from app.repositories.user_repository import get_app_profile_by_user_id

bearer_scheme = HTTPBearer(auto_error=False)


def _is_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def get_bearer_token(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token nao informado.",
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de autorizacao invalido.",
        )

    return credentials.credentials


def get_current_user(token: str = Depends(get_bearer_token)):
    try:
        payload = parse_token_payload(token)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido ou expirado.",
        ) from exc

    if _is_uuid(str(payload.subject)):
        profile = get_app_profile_by_user_id(str(payload.subject))

        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Perfil da aplicacao nao encontrado.",
            )

        if not profile.active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inativo.",
            )

        return build_authenticated_user_from_profile(profile)

    return build_authenticated_user(payload)


def require_roles(*roles: str):
    def dependency(current_user=Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Voce nao tem permissao para esta operacao.",
            )

        return current_user

    return dependency