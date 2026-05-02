from pydantic import BaseModel, Field, validator
import re

class ArticuloCreate(BaseModel):
    # Validación de longitud y tipo (Punto 1.3.a)
    titulo: str = Field(..., min_length=5, max_length=100)
    contenido: str = Field(..., min_length=10, max_length=5000)

    # Validación con Regex para evitar caracteres de control o inyecciones básicas
    @validator('titulo')
    def titulo_seguro(cls, v):
        if not re.match(r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\-\.\?¿!¡]+$', v):
            raise ValueError('El título contiene caracteres no permitidos')
        return v