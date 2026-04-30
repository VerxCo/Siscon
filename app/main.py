from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.consignatarias import router as consignatarias_router
from app.api.routes.convenios import router as convenios_router
from app.api.routes.vinculos import router as vinculos_router
from app.core.config import get_settings
from app.core.errors import DatabaseError

app = FastAPI(title="Siscon API")

settings = get_settings()

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
]

if settings.frontend_url:
    allowed_origins.append(settings.frontend_url.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"^https://([a-z0-9-]+\.)*vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)