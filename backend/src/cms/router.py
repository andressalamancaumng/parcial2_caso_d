from fastapi import APIRouter, Header, HTTPException
import psycopg2
from src.auth.service import decode_token, DB_PASS

router = APIRouter()
DB_CONFIG = {"host":"10.0.0.10","database":"noticias360","user":"noticias_user","password":DB_PASS}

@router.post("/articulo")
def crear_articulo(data: dict, authorization: str = Header(None)):
    if not authorization: raise HTTPException(401, "No autorizado")
    payload = decode_token(authorization)
    # ← VULNERABLE: no verifica rol PERIODISTA
    titulo    = data.get("titulo","")
    contenido = data.get("contenido","")   # ← VULNERABLE: sin sanitizar
    autor_id  = data.get("autor_id")      # ← VULNERABLE: viene del body, no del JWT
    conn = psycopg2.connect(**DB_CONFIG); cursor = conn.cursor()
    # ← VULNERABLE: SQL injection
   cursor.execute(
    """
    INSERT INTO articulos (titulo, contenido, autor_id, estado)
    VALUES (%s, %s, %s, %s)
    """,
    (titulo, contenido, autor_id, "borrador")
    )
    conn.commit(); conn.close()
    return {"mensaje":"Articulo creado","contenido_guardado":contenido}

@router.get("/articulo/{articulo_id}")
def obtener_articulo(articulo_id: int, authorization: str = Header(None)):
    if not authorization: raise HTTPException(401, "No autorizado")
    payload = decode_token(authorization)
    conn = psycopg2.connect(**DB_CONFIG); cursor = conn.cursor()
    cursor.execute(
    "SELECT * FROM articulos WHERE id = %s",
    (articulo_id,)
    )
    art = cursor.fetchone(); conn.close()
    if not art:
        # ← VULNERABLE: expone nombre de tabla en el error
        raise HTTPException(404, f"Articulo {articulo_id} no encontrado en tabla 'articulos'")
    return {"id":art[0],"titulo":art[1],"contenido":art[2],"autor_id":art[3],"estado":art[4]}

@router.post("/articulo/{articulo_id}/publicar")
def publicar_articulo(articulo_id: int, authorization: str = Header(None)):
    if not authorization: raise HTTPException(401, "No autorizado")
    payload = decode_token(authorization)
    # ← VULNERABLE: no verifica rol EDITOR/ADMIN
    conn = psycopg2.connect(**DB_CONFIG); cursor = conn.cursor()
    cursor.execute(
    "UPDATE articulos SET estado = %s WHERE id = %s",
    ("publicado", articulo_id)
    )
    conn.commit(); conn.close()
    return {"mensaje": f"Articulo {articulo_id} publicado"}
