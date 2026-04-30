import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.security import create_access_token
from app.main import app


class VinculoRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        get_settings.cache_clear()
        self.env_patch = patch.dict(
            os.environ,
            {"JWT_SECRET_KEY": "test-secret", "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": "60"},
            clear=True,
        )
        self.env_patch.start()
        self.client = TestClient(app)
        self.headers = {
            "Authorization": f"Bearer {create_access_token(subject='1', role='admin')}"
        }

    def tearDown(self) -> None:
        self.env_patch.stop()
        get_settings.cache_clear()

    def test_openapi_exposes_delete_route(self) -> None:
        schema = app.openapi()
        assert "delete" in schema["paths"]["/vinculos/{vinculo_id}"]

    def test_delete_vinculo_route_returns_repository_payload(self) -> None:
        payload = {
            "message": "Vinculo removido com sucesso.",
            "vinculo": {"id": 5, "convenio_id": 1, "consignataria_id": 2, "ativo": True},
        }

        with patch("app.api.routes.vinculos.delete_vinculo", return_value=payload):
            response = self.client.delete("/vinculos/5", headers=self.headers)

        assert response.status_code == 200
        assert response.json() == payload


if __name__ == "__main__":
    unittest.main()
