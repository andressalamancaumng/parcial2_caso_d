from fastapi import APIRouter, Header, HTTPException, Depends, Request
from .schemas import ArticuloCreate
import html
import logging
from datetime import datetime
import psycopg2
from src.auth.service import decode_token, DB_PASS

# Configuración del log para auditoría (Punto 1.3.c)
logging.basicConfig(
    filename='auditoria_seguridad.log', 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

router = APIRouter()
DB_CONFIG = {"host":"10.0.0.10","database":"noticias360","user":"noticias_user","password":DB_PASS}

@router.post("/articulo")
def crear_articulo(data: ArticuloCreate, request: Request, authorization: str = Header(None)):
    # 1. AUTENTICACIÓN
    if not authorization: 
        raise HTTPException(401, "No autorizado")
    
    try:
        payload = decode_token(authorization)
        
        # 2. VERIFICACIÓN DE ROL: Solo periodistas pueden crear (Punto 1.3.a)
        if payload.get("rol") != "periodista":
            raise HTTPException(403, "Acceso denegado: Se requiere rol de periodista")

        # 3. SANITIZACIÓN: Prevención XSS (Punto 1.3.b)
        # Usamos los datos validados por Pydantic (data.titulo, data.contenido)
        titulo_seguro = html.escape(data.titulo)
        contenido_seguro = html.escape(data.contenido)
        
        # SEGURIDAD DE AUTOR: El ID viene del Token (JWT)
        autor_id = payload.get("sub") 

        # 4. PERSISTENCIA SEGURA
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # PREVENCIÓN SQL INJECTION: Uso de parámetros (%s)
        query = "INSERT INTO articulos (titulo, contenido, autor_id, estado) VALUES (%s, %s, %s, 'borrador')"
        cursor.execute(query, (titulo_seguro, contenido_seguro, autor_id))
        
        conn.commit()
        conn.close()
        
        return {"mensaje": "Articulo creado"}

    except HTTPException as http_ex:
        # Re-lanzamos errores de FastAPI (401, 403) para que lleguen al cliente
        raise http_ex
    except Exception as e:
        # 5. MANEJO DE ERRORES Y AUDITORÍA (Punto 1.3.c)
        cliente_ip = request.client.host
        # Registramos el intento fallido con IP, timestamp y endpoint
        logging.warning(f"INTENTO FALLIDO | IP: {cliente_ip} | Endpoint: /articulo | Error: {str(e)}")
        
        # Retornamos error genérico HTTP 400 sin revelar detalles del sistema
        raise HTTPException(status_code=400, detail="Los datos enviados no son válidos o el servidor no pudo procesarlos.")

# ... El resto de tus rutas (obtener_articulo, publicar_articulo) están bien con el %s que ya traen.