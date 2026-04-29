from fastapi import FastAPI

from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.consignatarias import router as consignatarias_router
from app.api.routes.convenios import router as convenios_router
from app.api.routes.vinculos import router as vinculos_router

app = FastAPI(title="Siscon API")

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(consignatarias_router)
app.include_router(convenios_router)
app.include_router(vinculos_router)


@app.get("/")
def root() -> dict:
    return {"message": "Siscon API online"}
