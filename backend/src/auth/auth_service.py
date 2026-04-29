import hashlib
import logging
import re
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from fastapi import HTTPException, Request, status
from passlib.context import CryptContext
from psycopg2.extras import RealDictCursor

from src.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES
from src.database import get_connection


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)

PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$"
)

DUMMY_PASSWORD_HASH = pwd_context.hash("FakePassword123*")

logging.basicConfig(
    filename="audit.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _require_jwt_secret() -> str:
    if not JWT_SECRET:
        raise RuntimeError("JWT_SECRET no está configurado en variables de entorno.")
    return JWT_SECRET


def _email_key(email: str) -> str:
    normalized = email.strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _masked_user_id(user_id) -> str:
    if user_id is None:
        return "unknown"

    value = str(user_id)
    return f"***{value[-2:]}" if len(value) > 2 else "***"


def audit_auth_event(request: Request | None, user_id, result: str) -> None:
    client_ip = "unknown"

    if request is not None and request.client is not None:
        client_ip = request.client.host

    logging.info(
        "AUTH_EVENT ip=%s user_id=%s result=%s",
        client_ip,
        _masked_user_id(user_id),
        result
    )


def ensure_auth_tables() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS token_blacklist (
            jti VARCHAR(128) PRIMARY KEY,
            user_id INTEGER,
            expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_attempts (
            email_hash VARCHAR(128) PRIMARY KEY,
            failed_count INTEGER NOT NULL DEFAULT 0,
            locked_until TIMESTAMP WITH TIME ZONE,
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        )
    """)

    conn.commit()
    conn.close()


def validate_password_complexity(password: str) -> None:
    if not PASSWORD_REGEX.match(password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña no cumple los requisitos mínimos de seguridad."
        )


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(user_id: int, role: str) -> str:
    secret = _require_jwt_secret()
    now = _now_utc()

    expire_minutes = min(JWT_EXPIRE_MINUTES, 60)

    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expire_minutes)).timestamp()),
        "jti": str(uuid4())
    }

    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    secret = _require_jwt_secret()

    try:
        return jwt.decode(token, secret, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado."
        )


def is_token_blacklisted(jti: str | None) -> bool:
    if not jti:
        return True

    ensure_auth_tables()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 1
        FROM token_blacklist
        WHERE jti = %s
          AND expires_at > NOW()
        """,
        (jti,)
    )

    exists = cursor.fetchone() is not None
    conn.close()

    return exists


def blacklist_token(jti: str, user_id: int, expires_at_timestamp: int) -> None:
    ensure_auth_tables()

    expires_at = datetime.fromtimestamp(
        expires_at_timestamp,
        tz=timezone.utc
    )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO token_blacklist (jti, user_id, expires_at)
        VALUES (%s, %s, %s)
        ON CONFLICT (jti) DO NOTHING
        """,
        (jti, user_id, expires_at)
    )

    conn.commit()
    conn.close()


def _is_login_locked(email: str) -> bool:
    ensure_auth_tables()

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute(
        """
        SELECT locked_until
        FROM login_attempts
        WHERE email_hash = %s
        """,
        (_email_key(email),)
    )

    row = cursor.fetchone()
    conn.close()

    if not row or not row["locked_until"]:
        return False

    locked_until = row["locked_until"]

    if locked_until.tzinfo is None:
        locked_until = locked_until.replace(tzinfo=timezone.utc)

    return locked_until > _now_utc()


def _record_failed_login(email: str) -> None:
    ensure_auth_tables()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO login_attempts (email_hash, failed_count, locked_until, updated_at)
        VALUES (%s, 1, NULL, NOW())
        ON CONFLICT (email_hash)
        DO UPDATE SET
            failed_count = login_attempts.failed_count + 1,
            locked_until = CASE
                WHEN login_attempts.failed_count + 1 >= 5
                THEN NOW() + INTERVAL '15 minutes'
                ELSE login_attempts.locked_until
            END,
            updated_at = NOW()
        """,
        (_email_key(email),)
    )

    conn.commit()
    conn.close()


def _reset_failed_logins(email: str) -> None:
    ensure_auth_tables()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM login_attempts
        WHERE email_hash = %s
        """,
        (_email_key(email),)
    )

    conn.commit()
    conn.close()


def register_user(nombre: str, email: str, password: str, role: str = "ROLE_SUSCRIPTOR") -> dict:
    validate_password_complexity(password)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM periodistas
        WHERE email = %s
        """,
        (email,)
    )

    exists = cursor.fetchone()

    if exists:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fue posible completar el registro."
        )

    password_hash = hash_password(password)

    cursor.execute(
        """
        INSERT INTO periodistas (nombre, email, pwd_hash, role)
        VALUES (%s, %s, %s, %s)
        """,
        (nombre, email, password_hash, role)
    )

    conn.commit()
    conn.close()

    return {
        "mensaje": "Registro procesado correctamente."
    }


def authenticate_user(email: str, password: str, request: Request | None = None) -> dict:
    ensure_auth_tables()

    if _is_login_locked(email):
        audit_auth_event(request, None, "LOGIN_BLOCKED")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas o acceso temporalmente no disponible."
        )

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute(
        """
        SELECT id, nombre, role, pwd_hash
        FROM periodistas
        WHERE email = %s
        """,
        (email,)
    )

    user = cursor.fetchone()
    conn.close()

    password_hash = user["pwd_hash"] if user else DUMMY_PASSWORD_HASH
    valid_password = verify_password(password, password_hash)

    if not user or not valid_password:
        _record_failed_login(email)
        audit_auth_event(request, user["id"] if user else None, "LOGIN_FAILED")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas."
        )

    _reset_failed_logins(email)

    token = create_access_token(
        user_id=user["id"],
        role=user["role"]
    )

    audit_auth_event(request, user["id"], "LOGIN_SUCCESS")

    return {
        "access_token": token,
        "token_type": "bearer"
    }


def logout_user(payload: dict, request: Request | None = None) -> dict:
    jti = payload.get("jti")
    user_id = int(payload.get("sub"))
    exp = int(payload.get("exp"))

    blacklist_token(jti, user_id, exp)
    audit_auth_event(request, user_id, "LOGOUT_SUCCESS")

    return {
        "mensaje": "Sesión cerrada correctamente."
    }