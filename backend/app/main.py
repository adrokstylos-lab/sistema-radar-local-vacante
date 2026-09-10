"""Punto de entrada de la API (FastAPI).

Ejecutar en desarrollo:
    uvicorn backend.app.main:app --reload
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings
from backend.app.api.businesses import router as businesses_router
from backend.app.api.health import router as health_router
from backend.app.api.jobs import router as jobs_router
from backend.app.api.stats import router as stats_router
from backend.app.api.zones import router as zones_router
from backend.app.core.logging import get_logger

logger = get_logger("radar")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("API iniciada")
    yield
    logger.info("API detenida")


app = FastAPI(
    title="Radar Local de Negocios y Vacantes",
    version="0.1.0",
    lifespan=lifespan,
)

if settings.cors_origins_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

app.include_router(health_router)
app.include_router(businesses_router)
app.include_router(jobs_router)
app.include_router(zones_router)
app.include_router(stats_router)

# Dashboard compilado (Vite) servido por FastAPI. Se genera con:
#   cd frontend && npm install && npm run build   ->  frontend/dist/
_DIST = Path("frontend/dist")
if (_DIST / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=_DIST / "assets"), name="assets")


@app.get("/", include_in_schema=False)
def dashboard():
    index = _DIST / "index.html"
    if index.exists():
        return FileResponse(index)
    return JSONResponse(
        {"message": "Dashboard sin compilar. Ejecuta: cd frontend && npm install && npm run build"},
        status_code=503,
    )
