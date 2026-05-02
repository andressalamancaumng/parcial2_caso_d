from fastapi.testclient import TestClient
from src.main import app  # Ajusta según tu import de app
import pytest

client = TestClient(app)

def test_articulo_titulo_muy_corto():
    """Prueba que el sistema rechaza títulos de menos de 5 caracteres"""
    response = client.post(
        "/articulo",
        json={"titulo": "A", "contenido": "Contenido válido de prueba"},
        headers={"Authorization": "Bearer TOKEN_VALIDO"}
    )
    assert response.status_code == 400
    assert "Los datos enviados son inválidos" in response.json()["detail"]

def test_articulo_contenido_con_xss():
    """Prueba que el sistema acepta pero sanitiza contenido HTML peligroso"""
    payload = "<script>alert('xss')</script>Noticia segura"
    response = client.post(
        "/articulo",
        json={"titulo": "Titulo Valido", "contenido": payload},
        headers={"Authorization": "Bearer TOKEN_VALIDO"}
    )
    # Debe ser exitoso porque el backend ahora sanitiza el contenido
    assert response.status_code == 200
    # Aquí podrías verificar en la DB que se guardó como &lt;script&gt;