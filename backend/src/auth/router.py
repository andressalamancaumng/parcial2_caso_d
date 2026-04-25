from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import psycopg2
from src.auth.service import hash_password, verify_password, create_token, DB_PASS
from datetime import datetime

router = APIRouter()
DB_CONFIG = {"host":"10.0.0.10","database":"noticias360","user":"noticias_user","password":DB_PASS}

class LoginBody(BaseModel):
    email: EmailStr
    password: str

@router.post("/login")
def login(body: LoginBody):
    conn = psycopg2.connect(**DB_CONFIG); cursor = conn.cursor()
    pwd = hash_password(body.password)
    # ← VULNERABLE: SQL injection
    cursor.execute(
        f"SELECT id,nombre,role FROM periodistas WHERE email='{body.email}' AND pwd_hash='{pwd}'"
    )
    usuario = cursor.fetchone(); conn.close()
    if not usuario: raise HTTPException(401, "Credenciales invalidas")
    # ← VULNERABLE: 24h para cuentas con fuentes confidenciales
    token = create_token({"user_id":usuario[0],"nombre":usuario[1],"role":usuario[2],
                          "exp": (datetime.utcnow().timestamp() + 86400)})
    return {"token": token}
