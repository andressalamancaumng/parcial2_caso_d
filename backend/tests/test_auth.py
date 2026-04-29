import os
import jwt
import pytest

from src.auth.auth_service import (
    hash_password,
    verify_password,
    validate_password_complexity,
    create_access_token
)


def test_password_hash_uses_bcrypt():
    password = "Prueba123*"
    password_hash = hash_password(password)

    assert password != password_hash
    assert password_hash.startswith("$2b$") or password_hash.startswith("$2a$")
    assert verify_password(password, password_hash)


def test_password_complexity_rejects_weak_password():
    with pytest.raises(Exception):
        validate_password_complexity("12345678")


def test_password_complexity_accepts_strong_password():
    validate_password_complexity("Prueba123*")


def test_jwt_contains_required_claims(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "clave_test_segura_123")

    import src.auth.auth_service as auth_service
    auth_service.JWT_SECRET = os.getenv("JWT_SECRET")

    token = create_access_token(
        user_id=10,
        role="ROLE_EDITOR"
    )

    payload = jwt.decode(
        token,
        os.getenv("JWT_SECRET"),
        algorithms=["HS256"]
    )

    assert payload["sub"] == "10"
    assert payload["role"] == "ROLE_EDITOR"
    assert "exp" in payload
    assert "iat" in payload
    assert "jti" in payload