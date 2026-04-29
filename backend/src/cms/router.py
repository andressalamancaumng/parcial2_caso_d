from fastapi import APIRouter, Depends, HTTPException

from src.auth.rbac import verify_role
from src.database import get_connection


router = APIRouter()


@router.post("/articulo")
def crear_articulo(
    data: dict,
    payload=Depends(
        verify_role("ROLE_PERIODISTA", "ROLE_EDITOR", "ROLE_ADMIN")
    )
):
    titulo = data.get("titulo", "").strip()
    contenido = data.get("contenido", "").strip()

    if not titulo or not contenido:
        raise HTTPException(
            status_code=400,
            detail="La solicitud contiene datos inválidos."
        )

    autor_id = int(payload["sub"])

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO articulos (titulo, contenido, autor_id, estado)
        VALUES (%s, %s, %s, %s)
        """,
        (titulo, contenido, autor_id, "borrador")
    )

    conn.commit()
    conn.close()

    return {
        "mensaje": "Artículo creado correctamente."
    }


@router.get("/articulo/{articulo_id}")
def obtener_articulo(
    articulo_id: int,
    payload=Depends(
        verify_role("ROLE_PERIODISTA", "ROLE_EDITOR", "ROLE_ADMIN")
    )
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, titulo, contenido, autor_id, estado
        FROM articulos
        WHERE id = %s
        """,
        (articulo_id,)
    )

    articulo = cursor.fetchone()
    conn.close()

    if not articulo:
        raise HTTPException(
            status_code=404,
            detail="Recurso no encontrado."
        )

    return {
        "id": articulo[0],
        "titulo": articulo[1],
        "contenido": articulo[2],
        "autor_id": articulo[3],
        "estado": articulo[4]
    }


@router.post("/articulo/{articulo_id}/publicar")
def publicar_articulo(
    articulo_id: int,
    payload=Depends(
        verify_role("ROLE_EDITOR", "ROLE_ADMIN")
    )
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE articulos
        SET estado = %s
        WHERE id = %s
        """,
        ("publicado", articulo_id)
    )

    conn.commit()
    conn.close()

    return {
        "mensaje": "Artículo publicado correctamente."
    }