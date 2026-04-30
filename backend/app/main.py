from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.jobs.scheduler import shutdown_scheduler, start_scheduler

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def create_storage_root() -> None:
    Path(settings.storage_root).mkdir(parents=True, exist_ok=True)


@app.on_event("startup")
def boot_scheduler() -> None:
    start_scheduler()


@app.on_event("shutdown")
def stop_scheduler() -> None:
    shutdown_scheduler()


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(api_router, prefix=settings.api_v1_prefix)
