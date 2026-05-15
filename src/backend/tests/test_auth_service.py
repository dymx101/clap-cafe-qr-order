# backend/tests/test_auth_service.py
"""
Test harness for the authentication service.
Tests password hashing, JWT generation/verification, and edge cases.
These tests are pure unit tests — no database required.
"""
import time

import pytest
from app.core.auth_service import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from fastapi import HTTPException


class TestPasswordHashing:
    """Verify PBKDF2 password hashing and verification."""

    def test_hash_and_verify_success(self):
        password = "test-password-123!"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("correct-password")
        assert verify_password("wrong-password", hashed) is False

    def test_hash_is_unique_per_call(self):
        """Each call should produce a different salt, so hashes differ."""
        h1 = hash_password("same-password")
        h2 = hash_password("same-password")
        assert h1 != h2

    def test_hash_format(self):
        """Hash string should be salt$iterations$hash_hex."""
        hashed = hash_password("test")
        parts = hashed.split("$")
        assert len(parts) == 3
        assert parts[1].isdigit()

    def test_verify_with_corrupted_hash(self):
        assert verify_password("test", "not-a-valid-hash") is False
        assert verify_password("test", "") is False


class TestJWT:
    """Verify JWT creation and decoding."""

    def test_create_and_decode(self):
        token = create_access_token(
            user_id="test-uuid",
            email="admin@clapcafe.sg",
            role="manager",
            expires_seconds=3600,
        )
        payload = decode_access_token(token)
        assert payload["sub"] == "test-uuid"
        assert payload["email"] == "admin@clapcafe.sg"
        assert payload["role"] == "manager"

    def test_expired_token_raises(self):
        token = create_access_token(
            user_id="test-uuid",
            email="admin@clapcafe.sg",
            role="manager",
            expires_seconds=-1,  # already expired
        )
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)
        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()

    def test_tampered_token_raises(self):
        token = create_access_token(
            user_id="test-uuid",
            email="admin@clapcafe.sg",
            role="manager",
        )
        # Tamper with the payload
        parts = token.split(".")
        parts[1] = parts[1] + "x"
        tampered = ".".join(parts)
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(tampered)
        assert exc_info.value.status_code == 401

    def test_malformed_token_raises(self):
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token("not.a.valid.jwt.token")
        assert exc_info.value.status_code == 401

    def test_missing_parts_raises(self):
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token("onlyonepart")
        assert exc_info.value.status_code == 401
