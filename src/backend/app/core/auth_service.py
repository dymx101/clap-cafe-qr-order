# backend/app/core/auth_service.py
"""
Authentication service: JWT generation/verification, password hashing,
and the FastAPI dependency for protecting admin routes.
"""
import hashlib
import hmac
import json
import secrets
import time
import uuid
from base64 import urlsafe_b64decode, urlsafe_b64encode
from datetime import datetime
from typing import Optional

from app.config import settings
from app.database import get_db
from app.models.admin_user import AdminUser
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------------------------------------------------------
# Password hashing — uses PBKDF2-HMAC-SHA256 (stdlib, no extra dependency)
# ---------------------------------------------------------------------------
_HASH_ITERATIONS = 260_000  # OWASP 2023 recommendation
_SALT_LENGTH = 32


def hash_password(password: str) -> str:
    """Return a storable hash string: salt$iterations$hash (hex encoded)."""
    salt = secrets.token_hex(_SALT_LENGTH)
    dk = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), _HASH_ITERATIONS
    )
    return f"{salt}${_HASH_ITERATIONS}${dk.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify *password* against a hash produced by hash_password()."""
    try:
        salt, iterations_str, hash_hex = stored_hash.split("$")
        iterations = int(iterations_str)
    except (ValueError, AttributeError):
        return False
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations)
    return hmac.compare_digest(dk.hex(), hash_hex)


# ---------------------------------------------------------------------------
# Minimal JWT implementation (HS256) — avoids adding PyJWT dependency
# ---------------------------------------------------------------------------
_JWT_ALGORITHM = "HS256"
_JWT_EXPIRY_SECONDS = 60 * 60 * 24  # 24 hours


def _b64url_encode(data: bytes) -> str:
    return urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    padding = 4 - len(s) % 4
    return urlsafe_b64decode(s + "=" * padding)


def _sign(msg: str, secret: str) -> str:
    sig = hmac.new(secret.encode(), msg.encode(), hashlib.sha256).digest()
    return _b64url_encode(sig)


def create_access_token(
    user_id: str,
    email: str,
    role: str,
    expires_seconds: int = _JWT_EXPIRY_SECONDS,
) -> str:
    """Create a signed JWT access token."""
    header = _b64url_encode(json.dumps({"alg": _JWT_ALGORITHM, "typ": "JWT"}).encode())
    payload = _b64url_encode(
        json.dumps(
            {
                "sub": user_id,
                "email": email,
                "role": role,
                "exp": int(time.time()) + expires_seconds,
                "iat": int(time.time()),
            }
        ).encode()
    )
    msg = f"{header}.{payload}"
    signature = _sign(msg, settings.ADMIN_JWT_SECRET)
    return f"{msg}.{signature}"


def decode_access_token(token: str) -> dict:
    """Decode and verify a JWT. Raises HTTPException on failure."""
    try:
        header_b64, payload_b64, signature = token.split(".")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Malformed token"
        )

    # Verify signature
    msg = f"{header_b64}.{payload_b64}"
    expected_sig = _sign(msg, settings.ADMIN_JWT_SECRET)
    if not hmac.compare_digest(signature, expected_sig):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token signature"
        )

    # Decode payload
    payload = json.loads(_b64url_decode(payload_b64))

    # Check expiry
    if payload.get("exp", 0) < time.time():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )

    return payload


# ---------------------------------------------------------------------------
# FastAPI dependencies for route protection
# ---------------------------------------------------------------------------
_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_admin(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> AdminUser:
    """Dependency: extract and validate the admin user from the Bearer token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )

    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user ID in token"
        )

    result = await db.execute(select(AdminUser).where(AdminUser.id == uid))
    admin = result.scalar_one_or_none()
    if not admin or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin user not found or inactive",
        )

    return admin


def require_role(required_role: str):
    """Dependency factory: restrict access to a specific admin role."""

    async def _check(admin: AdminUser = Depends(get_current_admin)):
        if admin.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role '{required_role}'. Your role: '{admin.role}'",
            )
        return admin

    return _check
