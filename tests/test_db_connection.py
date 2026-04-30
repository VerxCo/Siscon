import os
import unittest
from unittest.mock import patch

import psycopg

from app.core.config import get_settings
from app.core.errors import DatabaseError
from app.db.connection import get_db_connection


class DatabaseConnectionTests(unittest.TestCase):
    def setUp(self) -> None:
        get_settings.cache_clear()
        self.env_patch = patch.dict(
            os.environ,
            {"DATABASE_URL": "postgresql://example", "JWT_SECRET_KEY": "test-secret"},
            clear=True,
        )
        self.env_patch.start()

    def tearDown(self) -> None:
        self.env_patch.stop()
        get_settings.cache_clear()

    def test_database_errors_are_wrapped(self) -> None:
        with patch("app.db.connection.psycopg.connect", side_effect=psycopg.Error("boom")):
            with self.assertRaises(DatabaseError):
                with get_db_connection():
                    pass


if __name__ == "__main__":
    unittest.main()
