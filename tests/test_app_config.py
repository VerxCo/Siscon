import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app


class AppConfigTests(unittest.TestCase):
    def tearDown(self) -> None:
        get_settings.cache_clear()

    def test_settings_exposes_auth_mode_and_frontend_url(self) -> None:
        with patch.dict(
            os.environ,
            {
                "JWT_SECRET_KEY": "test-secret",
                "AUTH_MODE": "supabase",
                "FRONTEND_URL": "https://example.vercel.app",
            },
            clear=True,
        ):
            get_settings.cache_clear()
            settings = get_settings()

        assert settings.auth_mode == "supabase"
        assert settings.frontend_url == "https://example.vercel.app"

    def test_cors_allows_localhost_and_vercel_previews(self) -> None:
        client = TestClient(app)

        for origin in [
            "http://127.0.0.1:5173",
            "https://siscon-frontend-a792t09as-verxcos-projects.vercel.app",
        ]:
            response = client.options(
                "/auth/me",
                headers={
                    "Origin": origin,
                    "Access-Control-Request-Method": "GET",
                    "Access-Control-Request-Headers": "authorization",
                },
            )

            assert response.status_code == 200
            assert response.headers["access-control-allow-origin"] == origin


if __name__ == "__main__":
    unittest.main()
