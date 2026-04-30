from contextlib import contextmanager

import psycopg

from app.core.errors import DatabaseError
from app.core.config import get_settings


@contextmanager
def get_db_connection():
    settings = get_settings()

    if not settings.database_url:
        raise RuntimeError("DATABASE_URL nao configurada.")

    try:
        with psycopg.connect(settings.database_url) as connection:
            yield connection
    except psycopg.Error as exc:
        raise DatabaseError("Falha ao acessar o banco de dados.") from exc
