from fastapi import APIRouter, Header, HTTPException, Depends
import psycopg2
from src.auth.service import decode_token, DB_PASS

router = APIRouter()
DB_CONFIG = {"host":"10.0.0.10","database":"noticias360","user":"noticias_user","password":DB_PASS}

@router.post("/articulo")
def crear_articulo(data: dict, authorization: str = Header(None)):
    if not authorization: raise HTTPException(401, "No autorizado")
    payload = decode_token(authorization)
    
    # 1. VERIFICACIÓN DE ROL: Solo periodistas pueden crear
    if payload.get("rol") != "periodista":
        raise HTTPException(403, "Acceso denegado: Se requiere rol de periodista")

    titulo    = data.get("titulo","")
    contenido = data.get("contenido","")
    # 2. SEGURIDAD DE AUTOR: El ID viene del Token (JWT), no del body
    autor_id  = payload.get("sub") 

    conn = psycopg2.connect(**DB_CONFIG); cursor = conn.cursor()
    
    # 3. PREVENCIÓN SQL INJECTION: Uso de parámetros (%s)
    query = "INSERT INTO articulos (titulo, contenido, autor_id, estado) VALUES (%s, %s, %s, 'borrador')"
    cursor.execute(query, (titulo, contenido, autor_id))
    
    conn.commit(); conn.close()
    return {"mensaje":"Articulo creado"}

@router.get("/articulo/{articulo_id}")
def obtener_articulo(articulo_id: int, authorization: str = Header(None)):
    if not authorization: raise HTTPException(401, "No autorizado")
    decode_token(authorization)
    
    conn = psycopg2.connect(**DB_CONFIG); cursor = conn.cursor()
    # PREVENCIÓN SQL INJECTION
    cursor.execute("SELECT id, titulo, contenido, autor_id, estado FROM articulos WHERE id = %s", (articulo_id,))
    art = cursor.fetchone(); conn.close()
    
    if not art:
        # SEGURIDAD DE INFORMACIÓN: Error genérico sin nombres de tablas
        raise HTTPException(404, "El recurso solicitado no existe")
        
    return {"id":art[0],"titulo":art[1],"contenido":art[2],"autor_id":art[3],"estado":art[4]}

@router.post("/articulo/{articulo_id}/publicar")
def publicar_articulo(articulo_id: int, authorization: str = Header(None)):
    if not authorization: raise HTTPException(401, "No autorizado")
    payload = decode_token(authorization)
    
    # 4. VERIFICACIÓN DE ROL: Solo editores o admins pueden publicar
    if payload.get("rol") not in ["editor", "admin"]:
        raise HTTPException(403, "Acceso denegado: Permisos insuficientes para publicar")
        
    conn = psycopg2.connect(**DB_CONFIG); cursor = conn.cursor()
    # PREVENCIÓN SQL INJECTION
    cursor.execute("UPDATE articulos SET estado='publicado' WHERE id=%s", (articulo_id,))
    
    conn.commit(); conn.close()
    return {"mensaje": "Estado actualizado correctamente"}