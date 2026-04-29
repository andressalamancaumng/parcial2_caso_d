"""
Módulo de compatibilidad para autenticación.

La lógica segura se centralizó en auth_service.py:
- bcrypt con costo 12
- JWT con sub, role, exp, iat y jti
- JWT_SECRET desde variable de entorno
- blacklist por jti
- bloqueo por intentos fallidos
"""

from src.auth.auth_service import (
    authenticate_user,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password
)