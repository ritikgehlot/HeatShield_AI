"""FastAPI application assembly.

Serves the built React frontend (frontend/dist) when it exists; falls back to
the original static/ dashboard otherwise, so the app is never left with no UI
at all mid-migration. API routes are always mounted first so /api/* is never
shadowed by the static-file catch-all.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import log_startup_config, settings
from .db import SessionLocal, init_db
from .routers import cities, data, health, legacy, reports, simulations, wards
from .seed import seed_database
from .services import refresh_data_source_status

STATIC_DIR = Path(__file__).resolve().parent / "static"
FRONTEND_DIST_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(_: FastAPI):
    log_startup_config()
    init_db()
    with SessionLocal() as session:
        seed_database(session)
        refresh_data_source_status(session)
    yield


app = FastAPI(
    title="HeatShield AI API",
    version="2.0.0",
    description="Urban heat risk mapping, explainable scoring, and cooling-intervention decision support.",
    lifespan=lifespan,
)

allowed_origins = ["*"] if settings.app_env != "production" else [settings.frontend_url]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router_module in (health, cities, wards, data, simulations, reports, legacy):
    app.include_router(router_module.router)

# Static mount must come last so it never shadows /api/* routes.
if FRONTEND_DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST_DIR, html=True), name="frontend")
elif STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
