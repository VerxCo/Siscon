from app.core.auth import AuthenticatedUser
from app.core.security import create_access_token, verify_password
from app.models.user import User


class AuthenticationError(Exception):
    pass


def authenticate_user(user: User | None, plain_password: str) -> AuthenticatedUser:
    if user is None:
        raise AuthenticationError("Usuario nao encontrado.")

    if not user.ativo:
        raise AuthenticationError("Usuario inativo.")

    if not verify_password(plain_password, user.senha_hash):
        raise AuthenticationError("Senha invalida.")

    return AuthenticatedUser(
        user_id=str(user.id),
        role=user.role,
        is_active=user.ativo,
    )


def issue_token_for_user(user: User) -> str:
    return create_access_token(
        subject=str(user.id),
        role=user.role,
    )
