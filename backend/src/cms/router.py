from fastapi import APIRouter, Header, HTTPException, Request
from .schemas import ArticuloCreate
import html
import logging
from datetime import datetime
import psycopg2
from src.auth.service import decode_token, DB_PASS

# Configuración de auditoría (Punto 1.3.c)
logging.basicConfig(filename='auditoria_seguridad.log', level=logging.INFO)

router = APIRouter()
DB_CONFIG = {"host":"10.0.0.10","database":"noticias360","user":"noticias_user","password":DB_PASS}

@router.post("/articulo")
def crear_articulo(data: ArticuloCreate, request: Request, authorization: str = Header(None)):
    if not authorization: raise HTTPException(401, "No autorizado")
    
    try:
        payload = decode_token(authorization)
        
        # 1. VERIFICACIÓN DE ROL (Punto 1.3.a)
        if payload.get("rol") != "periodista":
            raise HTTPException(403, "Acceso denegado: Se requiere rol de periodista")

        # 2. SANITIZACIÓN XSS (Punto 1.3.b)
        titulo_seguro = html.escape(data.titulo)
        contenido_seguro = html.escape(data.contenido)
        
        # 3. SEGURIDAD DE AUTOR: El ID viene del Token (JWT)
        autor_id = payload.get("sub") 

        conn = psycopg2.connect(**DB_CONFIG); cursor = conn.cursor()
        
        # 4. PREVENCIÓN SQL INJECTION (Parámetros %s)
        query = "INSERT INTO articulos (titulo, contenido, autor_id, estado) VALUES (%s, %s, %s, 'borrador')"
        cursor.execute(query, (titulo_seguro, contenido_seguro, autor_id))
        
        conn.commit(); conn.close()
        return {"mensaje":"Articulo creado"}

    except Exception as e:
        # Auditoría: IP, fecha y error (Punto 1.3.c)
        logging.warning(f"[{datetime.now()}] Error en /articulo | IP: {request.client.host} | Detalle: {str(e)}")
        raise HTTPException(status_code=400, detail="Datos inválidos")

@router.get("/articulo/{articulo_id}")
def obtener_articulo(articulo_id: int, authorization: str = Header(None)):
    if not authorization: raise HTTPException(401, "No autorizado")
    decode_token(authorization)
    
    conn = psycopg2.connect(**DB_CONFIG); cursor = conn.cursor()
    # PREVENCIÓN SQL INJECTION
    cursor.execute("SELECT id, titulo, contenido, autor_id, estado FROM articulos WHERE id = %s", (articulo_id,))
    art = cursor.fetchone(); conn.close()
    
    if not art:
        # Mensaje seguro (Punto 1.3.c)
        raise HTTPException(404, "El recurso solicitado no existe")
        
    return {"id":art[0],"titulo":art[1],"contenido":art[2],"autor_id":art[3],"estado":art[4]}

@router.post("/articulo/{articulo_id}/publicar")
def publicar_articulo(articulo_id: int, authorization: str = Header(None)):
    if not authorization: raise HTTPException(401, "No autorizado")
    payload = decode_token(authorization)
    
    # VERIFICACIÓN DE ROL
    if payload.get("rol") not in ["editor", "admin"]:
        raise HTTPException(403, "Acceso denegado: Permisos insuficientes")
        
    conn = psycopg2.connect(**DB_CONFIG); cursor = conn.cursor()
    # PREVENCIÓN SQL INJECTION
    cursor.execute("UPDATE articulos SET estado='publicado' WHERE id=%s", (articulo_id,))
    
    conn.commit(); conn.close()
    return {"mensaje": "Estado actualizado correctamente"}