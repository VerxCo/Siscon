import os
import unittest
from datetime import timedelta
from unittest.mock import patch

from app.core.auth import build_authenticated_user, ensure_role
from app.core.config import get_settings
from app.core.security import (
    InvalidCredentialsError,
    TokenExpiredError,
    create_access_token,
    get_password_hash,
    parse_token_payload,
    verify_password,
)


class SecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        get_settings.cache_clear()
        self.env_patch = patch.dict(
            os.environ,
            {"JWT_SECRET_KEY": "test-secret", "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": "60"},
            clear=True,
        )
        self.env_patch.start()

    def tearDown(self) -> None:
        self.env_patch.stop()
        get_settings.cache_clear()

    def test_password_hash_and_verify(self) -> None:
        password_hash = get_password_hash("senha-forte")
        assert password_hash != "senha-forte"
        assert verify_password("senha-forte", password_hash) is True
        assert verify_password("senha-errada", password_hash) is False

    def test_create_and_parse_access_token(self) -> None:
        token = create_access_token(subject="42", role="admin")
        payload = parse_token_payload(token)
        user = build_authenticated_user(payload)

        assert payload.subject == "42"
        assert payload.role == "admin"
        assert user.user_id == "42"
        assert user.role == "admin"

    def test_expired_token_raises_specific_error(self) -> None:
        token = create_access_token(
            subject="7",
            role="viewer",
            expires_delta=timedelta(seconds=-5),
        )
        with self.assertRaises(TokenExpiredError):
            parse_token_payload(token)

    def test_invalid_signature_raises_error(self) -> None:
        token = create_access_token(subject="10", role="editor")
        tampered = token[:-1] + ("a" if token[-1] != "a" else "b")
        with self.assertRaises(InvalidCredentialsError):
            parse_token_payload(tampered)

    def test_ensure_role_allows_expected_profile(self) -> None:
        token = create_access_token(subject="1", role="editor")
        user = build_authenticated_user(parse_token_payload(token))
        allowed = ensure_role(user, "admin", "editor")
        assert allowed.role == "editor"

    def test_ensure_role_blocks_unexpected_profile(self) -> None:
        token = create_access_token(subject="1", role="viewer")
        user = build_authenticated_user(parse_token_payload(token))
        with self.assertRaises(PermissionError):
            ensure_role(user, "admin", "editor")


if __name__ == "__main__":
    unittest.main()
