from dataclasses import dataclass


@dataclass(slots=True)
class User:
    id: int
    nome: str
    email: str
    senha_hash: str
    role: str
    ativo: bool = True


@dataclass(slots=True)
class AppUserProfile:
    user_id: str
    email: str | None
    full_name: str | None
    role: str
    active: bool = True
