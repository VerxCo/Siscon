import os
import json
import unittest
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
from unittest.mock import patch

from fastapi.testclient import TestClient
from jwt.utils import base64url_decode, base64url_encode

from app.core.config import get_settings
from app.core.security import create_access_token
from app.models.user import AppUserProfile
from app.main import app


class _FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


_P256_P = int(
    "ffffffff00000001000000000000000000000000ffffffffffffffffffffffff", 16
)
_P256_A = (_P256_P - 3) % _P256_P
_P256_GX = int(
    "6b17d1f2e12c4247f8bce6e563a440f2"
    "77037d812deb33a0f4a13945d898c296",
    16,
)
_P256_GY = int(
    "4fe342e2fe1a7f9b8ee7eb4a7c0f9e16"
    "2bce33576b315ececbb6406837bf51f5",
    16,
)
_P256_N = int(
    "ffffffff00000000ffffffffffffffff"
    "bce6faada7179e84f3b9cac2fc632551",
    16,
)
_P256_G = (_P256_GX, _P256_GY)
_RFC_ES256_PRIVATE_D = int.from_bytes(
    base64url_decode("jpsQnnGQmL-YBIffH1136cspYG6-0iY7X1fCE9-E9LI"),
    "big",
)
_RFC_ES256_PUBLIC_X = "f83OJ3D2xF1Bg8vub9tLe1gHMzV76e8Tus9uPHvRVEU"
_RFC_ES256_PUBLIC_Y = "x_FEzRu9m36HLN_tue659LNpXW6pCyStikYjKIWI5a0"


def _int_to_bytes(value: int, length: int = 32) -> bytes:
    return value.to_bytes(length, "big")


def _point_add(
    point_a: tuple[int, int] | None,
    point_b: tuple[int, int] | None,
) -> tuple[int, int] | None:
    if point_a is None:
        return point_b
    if point_b is None:
        return point_a

    x1, y1 = point_a
    x2, y2 = point_b

    if x1 == x2 and (y1 + y2) % _P256_P == 0:
        return None

    if point_a == point_b:
        slope = ((3 * x1 * x1 + _P256_A) * pow(2 * y1, -1, _P256_P)) % _P256_P
    else:
        slope = ((y2 - y1) * pow(x2 - x1, -1, _P256_P)) % _P256_P

    x3 = (slope * slope - x1 - x2) % _P256_P
    y3 = (slope * (x1 - x3) - y1) % _P256_P
    return x3, y3


def _scalar_mult(k: int, point: tuple[int, int]) -> tuple[int, int] | None:
    result: tuple[int, int] | None = None
    addend = point

    while k:
        if k & 1:
            result = _point_add(result, addend)
        addend = _point_add(addend, addend)
        k >>= 1

    return result


def _rfc6979_nonce(private_key: int, message_hash: bytes) -> int:
    v = b"\x01" * 32
    k = b"\x00" * 32
    x = _int_to_bytes(private_key) + message_hash

    k = hmac.new(k, v + b"\x00" + x, hashlib.sha256).digest()
    v = hmac.new(k, v, hashlib.sha256).digest()
    k = hmac.new(k, v + b"\x01" + x, hashlib.sha256).digest()
    v = hmac.new(k, v, hashlib.sha256).digest()

    while True:
        t = b""
        while len(t) < 32:
            v = hmac.new(k, v, hashlib.sha256).digest()
            t += v

        candidate = int.from_bytes(t[:32], "big")
        if 1 <= candidate < _P256_N:
            return candidate

        k = hmac.new(k, v + b"\x00", hashlib.sha256).digest()
        v = hmac.new(k, v, hashlib.sha256).digest()


def _sign_es256(signing_input: bytes, private_key: int) -> bytes:
    digest = hashlib.sha256(signing_input).digest()
    z = int.from_bytes(digest, "big")

    while True:
        nonce = _rfc6979_nonce(private_key, digest)
        point = _scalar_mult(nonce, _P256_G)
        if point is None:
            continue

        r = point[0] % _P256_N
        if r == 0:
            continue

        s = (pow(nonce, -1, _P256_N) * (z + r * private_key)) % _P256_N
        if s == 0:
            continue

        if s > _P256_N // 2:
            s = _P256_N - s

        return _int_to_bytes(r) + _int_to_bytes(s)


def _build_es256_jwk(kid: str) -> dict:
    return {
        "kty": "EC",
        "crv": "P-256",
        "use": "sig",
        "alg": "ES256",
        "kid": kid,
        "x": _RFC_ES256_PUBLIC_X,
        "y": _RFC_ES256_PUBLIC_Y,
    }


def _build_es256_token(kid: str, user_id: str) -> str:
    header = {
        "alg": "ES256",
        "kid": kid,
        "typ": "JWT",
    }
    payload = {
        "sub": user_id,
        "role": "editor",
        "exp": int((datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp()),
        "iss": "https://lqlwgdhfvcnytfumjlpm.supabase.co/auth/v1",
    }

    encoded_header = base64url_encode(
        json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).decode("ascii")
    encoded_payload = base64url_encode(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).decode("ascii")
    signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
    signature = base64url_encode(_sign_es256(signing_input, _RFC_ES256_PRIVATE_D)).decode(
        "ascii"
    )
    return f"{encoded_header}.{encoded_payload}.{signature}"


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

    def test_auth_me_accepts_supabase_es256_token(self) -> None:
        kid = "supabase-test-kid"
        user_id = "6a2f7c1b-8f34-4cf3-9d7a-2f8eb1ad4e91"
        profile = AppUserProfile(
            user_id=user_id,
            email="user@example.com",
            full_name="Test User",
            role="editor",
            active=True,
        )
        jwk = _build_es256_jwk(kid)
        token = _build_es256_token(kid, user_id)

        with patch.dict(os.environ, {"AUTH_MODE": "supabase"}, clear=False):
            get_settings.cache_clear()
            with patch("app.core.security.httpx.get", return_value=_FakeResponse({"keys": [jwk]})):
                with patch("app.api.deps.get_app_profile_by_user_id", return_value=profile):
                    response = self.client.get(
                        "/auth/me",
                        headers={"Authorization": f"Bearer {token}"},
                    )

        assert response.status_code == 200
        assert response.json() == {
            "user_id": user_id,
            "role": "editor",
            "is_active": True,
        }


if __name__ == "__main__":
    unittest.main()
