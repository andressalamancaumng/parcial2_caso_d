from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr
import psycopg2
import logging
from datetime import datetime, timedelta
import uuid  # Para el JTI
from src.auth.service import verify_password, create_token, DB_PASS

# Configuración de auditoría
logging.basicConfig(filename='auditoria_auth.log', level=logging.INFO)

router = APIRouter()
DB_CONFIG = {"host":"10.0.0.10","database":"noticias360","user":"noticias_user","password":DB_PASS}

class LoginBody(BaseModel):
    email: EmailStr
    password: str

@router.post("/login")
def login(body: LoginBody, request: Request):
    conn = psycopg2.connect(**DB_CONFIG); cursor = conn.cursor()
    
    # 1. PREVENCIÓN SQL INJECTION: Buscamos solo por email de forma segura
    query = "SELECT id, nombre, role, pwd_hash FROM periodistas WHERE email = %s"
    cursor.execute(query, (body.email,))
    usuario = cursor.fetchone()
    conn.close()

    # 2. PREVENCIÓN DE TIMING ATTACKS: Siempre ejecutamos verify_password
    # Aunque el usuario no exista, comparamos contra un hash falso para que el tiempo sea constante
    hash_a_comparar = usuario[3] if usuario else "$2b$12$EjemploDeHashFalsoParaEngañarAtacantes"
    password_valido = verify_password(body.password, hash_a_comparar)

    if not usuario or not password_valido:
        # LOG DE AUDITORÍA: Intento fallido (Punto 2.1)
        logging.warning(f"[{datetime.utcnow()}] LOGIN FALLIDO | IP: {request.client.host} | Email: {body.email}")
        raise HTTPException(401, "Credenciales inválidas") # Mensaje genérico

    # 3. JWT SEGURO (Claims del Punto 2.1)
    ahora = datetime.utcnow()
    payload = {
        "sub": str(usuario[0]),          # ID del usuario (no el email)
        "role": usuario[2],               # Rol del usuario
        "exp": ahora + timedelta(hours=1), # Máximo 1 hora (No 24h)
        "iat": ahora,                     # Tiempo de emisión
        "jti": str(uuid.uuid4())          # ID único del token para lista negra
    }
    
    token = create_token(payload)
    
    # LOG DE AUDITORÍA: Éxito
    logging.info(f"[{ahora}] LOGIN EXITOSO | IP: {request.client.host} | UserID: {usuario[0]}")
    
    return {"token": token}