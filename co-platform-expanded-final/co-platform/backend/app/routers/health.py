"""System health and readiness endpoints."""

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..services.health import build_health_report, readiness_check
from ..services.metrics import metrics_collector

router = APIRouter(prefix="", tags=["health"])


@router.get("/health")
def health(db: Session = Depends(get_db)) -> dict:
    return build_health_report(db)


@router.get("/ready")
def ready(db: Session = Depends(get_db)) -> dict:
    return readiness_check(db)


@router.get("/metrics", response_class=PlainTextResponse)
def metrics() -> PlainTextResponse:
    return PlainTextResponse(metrics_collector.render_prometheus(), media_type="text/plain")
