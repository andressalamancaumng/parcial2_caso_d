import pytest
from pydantic import ValidationError

from src.validation import ArticlePayload


def test_article_payload_accepts_valid_data():
    payload = ArticlePayload(
        titulo="Titulo valido",
        contenido="Contenido valido del articulo."
    )

    assert payload.titulo == "Titulo valido"
    assert payload.contenido == "Contenido valido del articulo."


def test_article_payload_rejects_short_title():
    with pytest.raises(ValidationError):
        ArticlePayload(
            titulo="No",
            contenido="Contenido valido."
        )


def test_article_payload_rejects_empty_content():
    with pytest.raises(ValidationError):
        ArticlePayload(
            titulo="Titulo valido",
            contenido=""
        )


def test_article_payload_sanitizes_script_content():
    payload = ArticlePayload(
        titulo="Titulo valido",
        contenido="<script>alert('xss')</script>"
    )

    assert "<script>" not in payload.contenido
    assert "&lt;script&gt;" in payload.contenido