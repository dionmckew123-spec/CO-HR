"""Entry point for the FastAPI application."""

import asyncio
import os
import time
from contextlib import suppress

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import Base, SessionLocal, engine
from .routers import (
    auth,
    users,
    onboarding,
    leaves,
    tickets,
    incidents,
    appeals,
    brag,
    offboarding,
    probation,
    training,
    settings,
    webhooks,
    approvals,
    attachments,
    search,
    audit,
    dsar,
    retention,
    health,
)
from .services.jobs import nightly_job_manager
from .services.metrics import metrics_collector


def create_app() -> FastAPI:
    app = FastAPI(title="CO HR & Support API", version="0.1.0")

    # Initialise database tables
    Base.metadata.create_all(bind=engine)
    nightly_job_manager.configure(SessionLocal)

    # Configure CORS
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
    # Remove empty strings
    origins = [o for o in allowed_origins if o]
    if not origins:
        # Default to allowing Vite dev server
        origins = ["http://localhost:5173"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    # Include routers
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(onboarding.router)
    app.include_router(leaves.router)
    app.include_router(tickets.router)
    app.include_router(incidents.router)
    app.include_router(appeals.router)
    app.include_router(brag.router)
    app.include_router(offboarding.router)
    app.include_router(probation.router)
    app.include_router(training.router)
    app.include_router(settings.router)
    app.include_router(webhooks.router)
    app.include_router(approvals.router)
    app.include_router(attachments.router)
    app.include_router(search.router)
    app.include_router(audit.router)
    app.include_router(audit.legacy_router)
    app.include_router(dsar.router)
    app.include_router(retention.router)
    app.include_router(health.router)

    @app.middleware("http")
    async def record_metrics(request: Request, call_next):  # type: ignore[override]
        start = time.perf_counter()
        success = False
        try:
            response = await call_next(request)
            success = response.status_code < 500
            return response
        finally:
            duration = time.perf_counter() - start
            metrics_collector.record_request(request.url.path, duration, success)

    @app.on_event("startup")
    async def start_nightly_jobs() -> None:
        app.state.nightly_task = asyncio.create_task(nightly_job_manager.run_scheduler())

    @app.on_event("shutdown")
    async def stop_nightly_jobs() -> None:
        nightly_job_manager.stop()
        task = getattr(app.state, "nightly_task", None)
        if task:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

    # Serve static HTML pages and assets from the ``static`` directory. This
    # allows a simple browser-based front‑end without requiring a separate
    # build step. Any path that does not match an API endpoint will fall
    # through to the static files handler.
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

    return app


app = create_app()