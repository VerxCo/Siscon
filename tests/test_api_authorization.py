import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.security import create_access_token
from app.main import app


class AuthorizationTests(unittest.TestCase):
    def setUp(self) -> None:
        get_settings.cache_clear()
        self.env_patch = patch.dict(
            os.environ,
            {
                "JWT_SECRET_KEY": "test-secret",
                "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": "60",
                "ADMIN_USER_ID": "admin-123",
            },
            clear=True,
        )
        self.env_patch.start()
        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.env_patch.stop()
        get_settings.cache_clear()

    def test_admin_route_allows_configured_admin_user_id(self) -> None:
        token = create_access_token(subject="admin-123", role="viewer")

        response = self.client.get(
            "/admin/only",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.json()["user_id"] == "admin-123"
        assert response.json()["role"] == "viewer"

    def test_admin_route_blocks_unrelated_user(self) -> None:
        token = create_access_token(subject="other-user", role="viewer")

        response = self.client.get(
            "/admin/only",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403


if __name__ == "__main__":
    unittest.main()
