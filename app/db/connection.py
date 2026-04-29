from contextlib import contextmanager

import psycopg

from app.core.config import get_settings


@contextmanager
def get_db_connection():
    settings = get_settings()

    if not settings.database_url:
        raise RuntimeError("DATABASE_URL nao configurada.")

    with psycopg.connect(settings.database_url) as connection:
        yield connection
