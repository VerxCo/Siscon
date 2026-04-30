import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def load_env_file(path: str = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("export "):
            line = line[len("export "):]

        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        os.environ.setdefault(key, value)


def _read_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "t", "yes", "y", "on"}


def _read_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


@dataclass(slots=True)
class Settings:
    app_name: str
    app_version: str
    debug: bool
    database_url: str | None
    jwt_secret_key: str
    jwt_algorithm: str
    jwt_access_token_expire_minutes: int
    admin_user_id: str | None
    first_admin_email: str | None
    first_admin_password: str | None
    auth_mode: str
    frontend_url: str | None

    @classmethod
    def from_env(cls) -> "Settings":
        load_env_file()

        return cls(
            auth_mode=os.getenv("AUTH_MODE", "dev"),
            frontend_url=os.getenv("FRONTEND_URL"),
            app_name=os.getenv("APP_NAME", "Siscon API"),
            app_version=os.getenv("APP_VERSION", "0.1.0"),
            debug=_read_bool("DEBUG", default=False),
            database_url=os.getenv("DATABASE_URL"),
            jwt_secret_key=os.getenv("JWT_SECRET_KEY", "dev-secret-change-me"),
            jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
            jwt_access_token_expire_minutes=_read_int("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 480),
            admin_user_id=os.getenv("ADMIN_USER_ID"),
            first_admin_email=os.getenv("FIRST_ADMIN_EMAIL"),
            first_admin_password=os.getenv("FIRST_ADMIN_PASSWORD"),
        )


@lru_cache
def get_settings() -> Settings:
    return Settings.from_env()