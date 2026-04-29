from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, EmailStr

from src.auth.auth_service import (
    authenticate_user,
    logout_user,
    register_user
)
from src.auth.rbac import get_current_payload


router = APIRouter()


class RegisterBody(BaseModel):
    nombre: str
    email: EmailStr
    password: str


class LoginBody(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
def register(body: RegisterBody):
    return register_user(
        nombre=body.nombre,
        email=body.email,
        password=body.password
    )


@router.post("/login")
def login(body: LoginBody, request: Request):
    return authenticate_user(
        email=body.email,
        password=body.password,
        request=request
    )


@router.post("/logout")
def logout(
    request: Request,
    payload=Depends(get_current_payload)
):
    return logout_user(payload, request)