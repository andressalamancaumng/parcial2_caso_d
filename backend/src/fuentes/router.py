from fastapi import APIRouter, Header, HTTPException, Query
import psycopg2
from src.auth.service import decode_token, cifrar_fuente, descifrar_fuente, DB_PASS

router = APIRouter()
DB_CONFIG = {"host":"10.0.0.10","database":"noticias360","user":"noticias_user","password":DB_PASS}

@router.post("/fuentes")
def guardar_fuente(data: dict, authorization: str = Header(None)):
    if not authorization: raise HTTPException(401, "No autorizado")
    payload = decode_token(authorization)
    # ← VULNERABLE: base64 como "cifrado"
    nombre_c = cifrar_fuente(data.get("nombre",""))
    contacto_c = cifrar_fuente(data.get("contacto",""))
    descripcion_c = cifrar_fuente(data.get("descripcion",""))
    conn = psycopg2.connect(**DB_CONFIG); cursor = conn.cursor()
    cursor.execute("INSERT INTO fuentes (periodista_id,nombre,contacto,descripcion) VALUES (%s,%s,%s,%s)",
        (payload["user_id"], nombre_c, contacto_c, descripcion_c))
    conn.commit(); conn.close()
    return {"mensaje": "Fuente guardada"}

@router.get("/fuentes")
def obtener_fuentes(periodista_id: int = Query(0), authorization: str = Header(None)):
    if not authorization: raise HTTPException(401, "No autorizado")
    payload = decode_token(authorization)
    conn = psycopg2.connect(**DB_CONFIG); cursor = conn.cursor()
    # ← VULNERABLE: admin ve TODAS las fuentes en claro
    if payload.get("role") == "ADMIN":
        cursor.execute("SELECT * FROM fuentes")
    else:
        # ← VULNERABLE: IDOR — no verifica periodista_id == user_id del JWT
        cursor.execute("SELECT * FROM fuentes WHERE periodista_id=%s", (periodista_id,))
    fuentes = cursor.fetchall(); conn.close()
    # ← VULNERABLE: descifra y retorna en claro
    return [{"id":f[0],"nombre":descifrar_fuente(f[2]),
             "contacto":descifrar_fuente(f[3]),"descripcion":descifrar_fuente(f[4])} for f in fuentes]
