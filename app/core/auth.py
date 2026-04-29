from dataclasses import dataclass

from app.core.security import TokenPayload
from app.models.user import AppUserProfile


@dataclass(slots=True)
class AuthenticatedUser:
    user_id: str
    role: str
    is_active: bool = True
    email: str | None = None
    full_name: str | None = None


def ensure_role(user: AuthenticatedUser, *roles: str) -> AuthenticatedUser:
    if user.role not in roles:
        raise PermissionError("User does not have permission for this operation.")
    return user


def build_authenticated_user(payload: TokenPayload) -> AuthenticatedUser:
    return AuthenticatedUser(
        user_id=str(payload.subject),
        role=payload.role,
        is_active=True,
    )


def build_authenticated_user_from_profile(profile: AppUserProfile) -> AuthenticatedUser:
    return AuthenticatedUser(
        user_id=profile.user_id,
        role=profile.role,
        is_active=profile.active,
        email=profile.email,
        full_name=profile.full_name,
    )
