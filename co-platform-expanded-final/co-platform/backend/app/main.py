"""Entry point for the FastAPI application.

This module creates the FastAPI app, includes all routers, and sets up
middleware such as CORS. On startup it initialises the database
schema if necessary.
"""

import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
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
)


def create_app() -> FastAPI:
    app = FastAPI(title="CO HR & Support API", version="0.1.0")

    # Initialise database tables
    Base.metadata.create_all(bind=engine)

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
    app.include_router(dsar.router)
    app.include_router(retention.router)

    # Serve static HTML pages and assets from the ``static`` directory. This
    # allows a simple browser-based front‑end without requiring a separate
    # build step. Any path that does not match an API endpoint will fall
    # through to the static files handler.
    from fastapi.staticfiles import StaticFiles
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

    return app


app = create_app()