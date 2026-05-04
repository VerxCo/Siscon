import base64
import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from functools import lru_cache

import httpx
import jwt

from app.core.config import get_settings

SUPABASE_JWKS_URL = (
    "https://lqlwgdhfvcnytfumjlpm.supabase.co/auth/v1/.well-known/jwks.json"
)
SUPABASE_ISSUER = "https://lqlwgdhfvcnytfumjlpm.supabase.co/auth/v1"


class InvalidCredentialsError(Exception):
    pass


class TokenExpiredError(InvalidCredentialsError):
    pass


@dataclass(slots=True)
class TokenPayload:
    subject: str
    role: str
    expires_at: datetime


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _sign(message: bytes, secret_key: str) -> str:
    signature = hmac.new(secret_key.encode("utf-8"), message, hashlib.sha256).digest()
    return _b64url_encode(signature)


def _json_dumps(payload: dict) -> bytes:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")


def get_password_hash(password: str) -> str:
    if not password:
        raise ValueError("Password cannot be empty.")

    salt = secrets.token_hex(16)
    iterations = 120_000
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    ).hex()
    return f"pbkdf2_sha256${iterations}${salt}${digest}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        algorithm, raw_iterations, salt, expected_digest = hashed_password.split("$", 3)
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    calculated_digest = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt.encode("utf-8"),
        int(raw_iterations),
    ).hex()
    return hmac.compare_digest(calculated_digest, expected_digest)


def create_access_token(subject: str, role: str, expires_delta: timedelta | None = None) -> str:
    settings = get_settings()
    if settings.jwt_algorithm != "HS256":
        raise ValueError("Only HS256 is supported.")

    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes)
    )

    header = {"alg": settings.jwt_algorithm, "typ": "JWT"}
    payload = {
        "sub": subject,
        "role": role,
        "exp": int(expire.timestamp()),
    }

    encoded_header = _b64url_encode(_json_dumps(header))
    encoded_payload = _b64url_encode(_json_dumps(payload))
    signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
    signature = _sign(signing_input, settings.jwt_secret_key)
    return f"{encoded_header}.{encoded_payload}.{signature}"


@lru_cache(maxsize=1)
def _fetch_supabase_jwks(jwks_url: str) -> dict:
    try:
        response = httpx.get(jwks_url, timeout=5.0)
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise InvalidCredentialsError("Unable to load Supabase JWKS.") from exc

    if not isinstance(data, dict):
        raise InvalidCredentialsError("Invalid Supabase JWKS payload.")

    keys = data.get("keys")
    if not isinstance(keys, list):
        raise InvalidCredentialsError("Invalid Supabase JWKS payload.")

    return data


def _get_supabase_public_key(token: str) -> object:
    try:
        header = jwt.get_unverified_header(token)
    except jwt.PyJWTError as exc:
        raise InvalidCredentialsError("Malformed token header.") from exc

    if header.get("alg") != "ES256":
        raise InvalidCredentialsError("Unexpected token algorithm.")

    kid = header.get("kid")
    if not kid:
        raise InvalidCredentialsError("Token without key id.")

    jwks = _fetch_supabase_jwks(SUPABASE_JWKS_URL)
    jwk = next((key for key in jwks["keys"] if key.get("kid") == kid), None)

    if jwk is None:
        _fetch_supabase_jwks.cache_clear()
        jwks = _fetch_supabase_jwks(SUPABASE_JWKS_URL)
        jwk = next((key for key in jwks["keys"] if key.get("kid") == kid), None)

    if jwk is None:
        raise InvalidCredentialsError("Supabase public key not found.")

    try:
        return jwt.PyJWK.from_dict(jwk).key
    except (TypeError, ValueError, jwt.PyJWTError) as exc:
        raise InvalidCredentialsError("Invalid Supabase public key.") from exc


def _decode_supabase_token(token: str) -> dict:
    public_key = _get_supabase_public_key(token)

    try:
        return jwt.decode(
            token,
            public_key,
            algorithms=["ES256"],
            issuer=SUPABASE_ISSUER,
            options={
                "verify_aud": False,
                "require": ["exp", "sub"],
            },
        )
    except jwt.ExpiredSignatureError as exc:
        raise TokenExpiredError("Token expired.") from exc
    except jwt.PyJWTError as exc:
        raise InvalidCredentialsError("Invalid Supabase token.") from exc


def _decode_local_token(token: str) -> dict:
    settings = get_settings()

    try:
        encoded_header, encoded_payload, encoded_signature = token.split(".")
    except ValueError as exc:
        raise InvalidCredentialsError("Malformed token.") from exc

    signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
    expected_signature = _sign(signing_input, settings.jwt_secret_key)

    if not hmac.compare_digest(encoded_signature, expected_signature):
        raise InvalidCredentialsError("Invalid token signature.")

    try:
        header = json.loads(_b64url_decode(encoded_header))
        payload = json.loads(_b64url_decode(encoded_payload))
    except (json.JSONDecodeError, ValueError) as exc:
        raise InvalidCredentialsError("Invalid token payload.") from exc

    if header.get("alg") != settings.jwt_algorithm:
        raise InvalidCredentialsError("Unexpected token algorithm.")

    exp = payload.get("exp")
    if not isinstance(exp, int):
        raise InvalidCredentialsError("Token without valid expiration.")

    now_timestamp = int(datetime.now(timezone.utc).timestamp())
    if exp < now_timestamp:
        raise TokenExpiredError("Token expired.")

    return payload


def decode_token(token: str) -> dict:
    settings = get_settings()
    if settings.auth_mode == "supabase":
        return _decode_supabase_token(token)
    return _decode_local_token(token)


def parse_token_payload(token: str) -> TokenPayload:
    payload = decode_token(token)
    return TokenPayload(
        subject=str(payload["sub"]),
        role=str(payload["role"]),
        expires_at=datetime.fromtimestamp(int(payload["exp"]), tz=timezone.utc),
    )
