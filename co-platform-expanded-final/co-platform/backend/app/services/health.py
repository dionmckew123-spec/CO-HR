"""Health reporting helpers."""

from __future__ import annotations

from typing import Dict, List

from sqlalchemy import text
from sqlalchemy.orm import Session

from .audit_chain import verify_hash_chain
from .jobs import nightly_job_manager
from .metrics import metrics_collector


def build_health_report(db: Session) -> Dict[str, object]:
    issues: List[str] = []
    components: Dict[str, Dict[str, object]] = {}

    # Database health
    try:
        db.execute(text("SELECT 1"))
        components["database"] = {"status": "ok"}
    except Exception as exc:  # pragma: no cover - defensive
        components["database"] = {"status": "error", "detail": str(exc)}
        issues.append("Database connection unavailable")

    # Audit chain
    try:
        report = verify_hash_chain(db)
        status = "ok" if report.status == "pass" else "degraded"
        components["audit_chain"] = {
            "status": status,
            "chain_status": report.status,
            "entries_checked": report.entries_checked,
            "issues": report.issues,
        }
        if report.status != "pass":
            issues.append("Audit hash chain verification failed")
    except Exception as exc:  # pragma: no cover - defensive
        components["audit_chain"] = {"status": "error", "detail": str(exc)}
        issues.append("Audit verification error")

    # Nightly jobs
    job_state = nightly_job_manager.state()
    job_results = job_state.get("results", {})
    if not job_state.get("last_run"):
        components["nightly_jobs"] = {"status": "degraded", "detail": "No runs recorded"}
        issues.append("Nightly jobs have not executed yet")
    else:
        degraded = [name for name, info in job_results.items() if info["status"] not in {"success", "skipped"}]
        components["nightly_jobs"] = {
            "status": "ok" if not degraded else "degraded",
            "last_run": job_state["last_run"],
            "alerts": job_state.get("alerts", []),
            "degraded_jobs": degraded,
        }
        if degraded:
            issues.extend([f"Nightly job {name} reported {job_results[name]['status']}" for name in degraded])
        if job_state.get("alerts"):
            issues.extend(job_state["alerts"])

    # Email services from metrics snapshot
    snapshot = metrics_collector.snapshot()
    imap = snapshot["imap"]
    smtp = snapshot["smtp"]
    email_status = "ok"
    email_detail: Dict[str, object] = {"imap": imap, "smtp": smtp}
    if imap["fail"] and not imap["success"]:
        email_status = "degraded"
        issues.append("IMAP fetch failures detected")
    if smtp["fail"] and not smtp["success"]:
        email_status = "degraded"
        issues.append("SMTP delivery failures detected")
    components["email"] = {"status": email_status, **email_detail}

    overall_status = "ok" if not issues else "degraded"
    return {"status": overall_status, "components": components, "issues": issues, "metrics": snapshot}


def readiness_check(db: Session) -> Dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as exc:  # pragma: no cover - defensive
        return {"status": "error", "detail": str(exc)}
