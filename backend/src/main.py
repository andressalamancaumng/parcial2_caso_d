from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.auth.router import router as auth_router
from src.cms.router import router as cms_router
from src.fuentes.router import router as fuentes_router

app = FastAPI(title="Noticias 360 API", version="1.0.0")
app.add_middleware(CORSMiddleware,
    allow_origins=["https://noticias360-grupoN.lab.umng.edu.co"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(cms_router, prefix="/api/cms", tags=["cms"])
app.include_router(fuentes_router, prefix="/api", tags=["fuentes"])
