from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.consignatarias import router as consignatarias_router
from app.api.routes.convenios import router as convenios_router
from app.api.routes.vinculos import router as vinculos_router
from app.core.errors import DatabaseError

app = FastAPI(title="Siscon API")


@app.exception_handler(DatabaseError)
def database_error_handler(_: Request, exc: DatabaseError):
    return JSONResponse(
        status_code=503,
        content={"detail": str(exc)},
    )

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(consignatarias_router)
app.include_router(convenios_router)
app.include_router(vinculos_router)


@app.get("/")
def root() -> dict:
    return {"message": "Siscon API online"}
