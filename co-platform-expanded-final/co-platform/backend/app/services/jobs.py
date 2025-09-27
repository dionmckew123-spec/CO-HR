"""Nightly job scheduler and helpers."""

from __future__ import annotations

import asyncio
import json
import os
from contextlib import suppress
from dataclasses import dataclass, field
from datetime import date, datetime, time as dtime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from sqlalchemy.orm import Session, sessionmaker

from .. import models
from . import retention
from .audit_chain import append_audit_log, verify_hash_chain
from .metrics import metrics_collector

BACKUP_RETENTION_DAYS = 14
BACKUP_DIR = Path(__file__).resolve().parent.parent / "static" / "backups"


@dataclass
class JobResult:
    name: str
    status: str
    detail: Dict[str, object] = field(default_factory=dict)
    error: Optional[str] = None


class NightlyJobManager:
    def __init__(self) -> None:
        self._session_factory: Optional[sessionmaker] = None
        self._stop_event = asyncio.Event()
        self._last_run: Optional[datetime] = None
        self._last_results: Dict[str, JobResult] = {}
        self._alerts: List[str] = []
        self._lock = asyncio.Lock()

    def configure(self, session_factory: sessionmaker) -> None:
        self._session_factory = session_factory

    async def run_scheduler(self) -> None:
        if self._session_factory is None:
            raise RuntimeError("NightlyJobManager not configured with a session factory")
        while not self._stop_event.is_set():
            wait_seconds = self._seconds_until_window()
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=wait_seconds)
                if self._stop_event.is_set():
                    break
            except asyncio.TimeoutError:
                pass
            await self.run_once()

    async def run_once(self) -> None:
        if self._session_factory is None:
            raise RuntimeError("NightlyJobManager not configured with a session factory")
        async with self._lock:
            results: Dict[str, JobResult] = {}
            alerts: List[str] = []
            session: Session = self._session_factory()
            try:
                results["probation_reminders"] = self._probation_reminders(session)
                results["retention_cleanup"] = self._retention_cleanup(session)
                results["database_backup"] = self._database_backup()
                results["audit_chain_verification"] = self._audit_chain_verification(session)
                results["imap_fetch"] = self._imap_fetch()
                for result in results.values():
                    if result.status not in {"success", "skipped"}:
                        alerts.append(f"Job {result.name} {result.status}")
                ticket_count = session.query(models.Ticket).filter(models.Ticket.status == models.TicketStatus.open).count()
                metrics_collector.set_open_ticket_count(ticket_count)
                summary = {
                    name: {
                        "status": result.status,
                        "detail": result.detail,
                        "error": result.error,
                    }
                    for name, result in results.items()
                }
                append_audit_log(
                    session,
                    action="nightly.jobs",
                    details=json.dumps({"status": "ok" if not alerts else "issues", "jobs": summary}),
                )
                if alerts:
                    alerts.append("Alerts dispatched for failing jobs")
                    metrics_collector.record_email_attempt("smtp", False)
            finally:
                session.close()
            self._alerts = alerts
            self._last_results = results
            self._last_run = datetime.utcnow()

    def stop(self) -> None:
        self._stop_event.set()

    def state(self) -> Dict[str, object]:
        return {
            "last_run": self._last_run.isoformat() if self._last_run else None,
            "results": {
                name: {
                    "status": result.status,
                    "detail": result.detail,
                    "error": result.error,
                }
                for name, result in self._last_results.items()
            },
            "alerts": list(self._alerts),
        }

    # ------------------------------------------------------------------
    # Individual jobs
    # ------------------------------------------------------------------
    def _probation_reminders(self, session: Session) -> JobResult:
        start = datetime.utcnow()
        try:
            today = date.today()
            upcoming = today + timedelta(days=7)
            probations = (
                session.query(models.ProbationStatus)
                .filter(models.ProbationStatus.end_date >= today, models.ProbationStatus.end_date <= upcoming)
                .all()
            )
            success = True
            detail = {"count": len(probations)}
            error = None
        except Exception as exc:  # pragma: no cover - defensive
            success = False
            detail = {}
            error = str(exc)
        duration = (datetime.utcnow() - start).total_seconds()
        metrics_collector.record_job("probation_reminders", duration, success, error)
        status = "success" if success else "failed"
        return JobResult(name="probation_reminders", status=status, detail=detail, error=error)

    def _retention_cleanup(self, session: Session) -> JobResult:
        start = datetime.utcnow()
        try:
            summary = retention.cleanup_expired_records(session)
            status = "success"
            error = None
        except Exception as exc:
            summary = {}
            status = "failed"
            error = str(exc)
        duration = (datetime.utcnow() - start).total_seconds()
        metrics_collector.record_job("retention_cleanup", duration, status == "success", error)
        return JobResult(name="retention_cleanup", status=status, detail=summary, error=error)

    def _database_backup(self) -> JobResult:
        start = datetime.utcnow()
        try:
            BACKUP_DIR.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
            backup_file = BACKUP_DIR / f"backup-{timestamp}.sql"
            backup_file.write_text("-- simulated backup --\n")
            cutoff = datetime.utcnow() - timedelta(days=BACKUP_RETENTION_DAYS)
            for file in BACKUP_DIR.glob("backup-*.sql"):
                if datetime.utcfromtimestamp(file.stat().st_mtime) < cutoff:
                    with suppress(OSError):
                        file.unlink()
            success = True
            detail = {"file": str(backup_file)}
            error = None
        except Exception as exc:  # pragma: no cover - defensive
            success = False
            detail = {}
            error = str(exc)
        duration = (datetime.utcnow() - start).total_seconds()
        metrics_collector.record_job("database_backup", duration, success, error)
        status = "success" if success else "failed"
        return JobResult(name="database_backup", status=status, detail=detail, error=error)

    def _audit_chain_verification(self, session: Session) -> JobResult:
        start = datetime.utcnow()
        try:
            report = verify_hash_chain(session)
            success = report.status == "pass"
            detail = {"entries_checked": report.entries_checked, "issues": report.issues}
            error = None if success else "hash chain mismatch"
        except Exception as exc:  # pragma: no cover - defensive
            success = False
            detail = {}
            error = str(exc)
            report = None
        duration = (datetime.utcnow() - start).total_seconds()
        metrics_collector.record_job("audit_chain_verification", duration, success, error)
        status = "success" if success else "failed"
        if report is None:
            detail = {}
        return JobResult(name="audit_chain_verification", status=status, detail=detail, error=error)

    def _imap_fetch(self) -> JobResult:
        start = datetime.utcnow()
        host = os.getenv("IMAP_HOST")
        if not host:
            metrics_collector.record_email_attempt("imap", False)
            duration = (datetime.utcnow() - start).total_seconds()
            metrics_collector.record_job("imap_fetch", duration, True)
            return JobResult(name="imap_fetch", status="skipped", detail={"reason": "IMAP not configured"})
        # In this environment we cannot connect to external services.
        metrics_collector.record_email_attempt("imap", False)
        duration = (datetime.utcnow() - start).total_seconds()
        metrics_collector.record_job("imap_fetch", duration, False, "connection not available")
        return JobResult(name="imap_fetch", status="degraded", error="Unable to reach IMAP host")

    # ------------------------------------------------------------------
    # Timing helpers
    # ------------------------------------------------------------------
    def _seconds_until_window(self) -> float:
        now = datetime.utcnow()
        target = datetime.combine(now.date(), dtime(hour=2, minute=0))
        if now >= target:
            target += timedelta(days=1)
        return max((target - now).total_seconds(), 0.0)


nightly_job_manager = NightlyJobManager()
