import uuid

from fastapi import Header, HTTPException, status

from app.core.auth import (
    build_authenticated_user,
    build_authenticated_user_from_profile,
)
from app.core.security import InvalidCredentialsError, parse_token_payload
from app.repositories.user_repository import get_app_profile_by_user_id


def _is_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def get_bearer_token(authorization: str | None = Header(default=None)) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token nao informado.",
        )

    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de autorizacao invalido.",
        )

    return parts[1]


def get_current_user(authorization: str | None = Header(default=None)):
    token = get_bearer_token(authorization)

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
    def dependency(authorization: str | None = Header(default=None)):
        current_user = get_current_user(authorization)

        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Voce nao tem permissao para esta operacao.",
            )

        return current_user

    return dependency
