import os
import jwt
import uuid
import psycopg2
import logging
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import HTTPException

# Claves de entorno (Requisito 2.1)
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key-umng-2026")
DB_PASS = os.getenv("DB_PASS", "noticias_db_pass")
DB_CONFIG = {"host":"10.0.0.10","database":"noticias360","user":"noticias_user","password":DB_PASS}

# Bcrypt con costo 12 (Requisito 2.1)
pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12)

def is_jti_blacklisted(jti: str) -> bool:
    """Verifica en BD si el token fue invalidado (Logout)"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    # Buscamos el ID único del token en la tabla de lista negra
    cursor.execute("SELECT 1 FROM token_blacklist WHERE jti = %s", (jti,))
    blacklisted = cursor.fetchone() is not None
    conn.close()
    return blacklisted

def check_login_block(email: str):
    """Verifica si el usuario está bloqueado por intentos fallidos (Requisito 2.1)"""
    conn = psycopg2.connect(**DB_CONFIG); cursor = conn.cursor()
    cursor.execute("SELECT intentos, ultima_falla FROM login_attempts WHERE email = %s", (email,))
    registro = cursor.fetchone()
    conn.close()

    if registro:
        intentos, ultima_falla = registro
        # Si tiene 5 fallos y han pasado menos de 15 minutos, bloquear
        if intentos >= 5 and (datetime.utcnow() - ultima_falla).seconds < 900:
            raise HTTPException(403, "Cuenta bloqueada temporalmente por seguridad")

def decode_token(token: str) -> dict:
    """Valida firma, expiración y lista negra (Requisito 2.2)"""
    try:
        token_clean = token.replace("Bearer ", "")
        payload = jwt.decode(token_clean, JWT_SECRET, algorithms=["HS256"])
        
        # VERIFICACIÓN DE JTI (Logout / Lista negra)
        if is_jti_blacklisted(payload.get("jti")):
            raise HTTPException(status_code=401, detail="Sesión cerrada o token inválido")
            
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token ha expirado")
    except Exception:
        raise HTTPException(status_code=401, detail="Token no válido")