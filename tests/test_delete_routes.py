import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.security import create_access_token
from app.main import app


class DeleteRouteTests(unittest.TestCase):
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

    def test_openapi_exposes_delete_routes(self) -> None:
        schema = app.openapi()

        assert "delete" in schema["paths"]["/consignatarias/{consignataria_id}"]
        assert "delete" in schema["paths"]["/convenios/{convenio_id}"]

    def test_delete_consignataria_route_returns_repository_payload(self) -> None:
        payload = {
            "message": "Consignataria removida com sucesso.",
            "consignataria": {"id": 10, "nome": "Teste", "ativo": True},
            "vinculos_removidos": 3,
            "convenios_removidos": 1,
        }

        with patch("app.api.routes.consignatarias.delete_consignataria", return_value=payload):
            response = self.client.delete("/consignatarias/10", headers=self.headers)

        assert response.status_code == 200
        assert response.json() == payload

    def test_delete_convenio_route_returns_repository_payload(self) -> None:
        payload = {
            "message": "Convenio removido com sucesso.",
            "convenio": {"id": 7, "nome": "Conv", "nome_normalizado": "conv", "ativo": True},
            "vinculos_removidos": 2,
        }

        with patch("app.api.routes.convenios.delete_convenio", return_value=payload):
            response = self.client.delete("/convenios/7", headers=self.headers)

        assert response.status_code == 200
        assert response.json() == payload


if __name__ == "__main__":
    unittest.main()
