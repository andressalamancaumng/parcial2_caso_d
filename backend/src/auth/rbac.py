from fastapi import Header, HTTPException, status

from src.auth.auth_service import decode_access_token, is_token_blacklisted


def get_current_payload(authorization: str = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado."
        )

    token = authorization.replace("Bearer ", "")

    payload = decode_access_token(token)

    jti = payload.get("jti")

    if is_token_blacklisted(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado."
        )

    return payload


def verify_role(*allowed_roles):
    def dependency(authorization: str = Header(None)) -> dict:
        payload = get_current_payload(authorization)

        role = payload.get("role")

        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para realizar esta acción."
            )

        return payload

    return dependency