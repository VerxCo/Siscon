import unittest
from fastapi.testclient import TestClient

from app.main import app


class SmokeTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_root(self):
        response = self.client.get("/")
        assert response.status_code == 200
        assert response.json()["message"] == "Siscon API online"

    def test_login_fake_admin(self):
        response = self.client.post(
            "/auth/login",
            json={"email": "admin@admin.com", "senha": "123456"},
        )
        assert response.status_code == 200
        assert response.json()["role"] == "admin"


if __name__ == "__main__":
    unittest.main()
