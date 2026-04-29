import html

from pydantic import BaseModel, constr, validator


class ArticlePayload(BaseModel):
    titulo: constr(strip_whitespace=True, min_length=3, max_length=120)
    contenido: constr(strip_whitespace=True, min_length=1, max_length=5000)

    @validator("titulo", "contenido")
    def sanitize_text(cls, value: str) -> str:
        return html.escape(value, quote=True)