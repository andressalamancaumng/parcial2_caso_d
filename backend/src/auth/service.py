"""Auth service Noticias 360 — CON VULNERABILIDADES INTENCIONALES"""
import hashlib, jwt, base64
from datetime import datetime

# ← VULNERABLE: todo hardcodeado
JWT_SECRET = "noticias360secret"
ENCRYPTION_KEY = "AES_KEY_noticias_2024_fixed"
DB_PASS = "noticias_db_pass"

def hash_password(password: str) -> str:
    # ← VULNERABLE: SHA256 sin sal
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain: str, hashed: str) -> bool:
    return hashlib.sha256(plain.encode()).hexdigest() == hashed

def create_token(data: dict) -> str:
    # ← VULNERABLE: sin exp ni jti; 24h para periodistas es demasiado
    return jwt.encode(data.copy(), JWT_SECRET, algorithm="HS256")

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token.replace("Bearer ",""), JWT_SECRET, algorithms=["HS256"])
    except Exception as e:
        raise ValueError(str(e))

# ← VULNERABLE: base64 no es cifrado
def cifrar_fuente(texto: str) -> str:
    return base64.b64encode(texto.encode()).decode()

def descifrar_fuente(texto_cifrado: str) -> str:
    return base64.b64decode(texto_cifrado).decode()
