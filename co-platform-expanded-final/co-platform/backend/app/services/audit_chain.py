"""Helpers for managing the tamper-evident audit hash chain."""

from __future__ import annotations

import hashlib
import hmac
import os
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, List, Tuple

from sqlalchemy.orm import Session

from .. import models

GENESIS_PREV_HASH = hashlib.sha256(b"CO-HR-AUDIT-GENESIS").hexdigest()


@dataclass
class HashChainReport:
    status: str
    entries_checked: int
    issues: List[Dict[str, str]] = field(default_factory=list)


def _serialise_entry(log: models.AuditLog) -> str:
    parts = [
        log.timestamp.isoformat(),
        str(log.user_id or ""),
        log.action,
        str(log.entity_type or ""),
        str(log.entity_id or ""),
        log.details or "",
        log.prev_hash or "",
    ]
    return "|".join(parts)


def _compute_hash(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def append_audit_log(
    db: Session,
    *,
    action: str,
    user_id: int | None = None,
    entity_type: str | None = None,
    entity_id: int | None = None,
    details: str | None = None,
    timestamp: date | None = None,
) -> models.AuditLog:
    """Create a new ``AuditLog`` entry that extends the hash chain."""

    timestamp = timestamp or date.today()
    last_entry = db.query(models.AuditLog).order_by(models.AuditLog.id.desc()).first()
    prev_hash = last_entry.entry_hash if last_entry and last_entry.entry_hash else GENESIS_PREV_HASH
    retention_expires_at = timestamp + timedelta(days=365 * 4)

    log = models.AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        timestamp=timestamp,
        details=details,
        prev_hash=prev_hash,
        retention_expires_at=retention_expires_at,
        legal_hold=False,
    )
    payload = _serialise_entry(log)
    log.entry_hash = _compute_hash(payload)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def verify_hash_chain(db: Session) -> HashChainReport:
    """Verify that the stored audit log entries form a valid hash chain."""

    logs = db.query(models.AuditLog).order_by(models.AuditLog.id).all()
    prev_hash = GENESIS_PREV_HASH
    issues: List[Dict[str, str]] = []
    for log in logs:
        expected_prev = prev_hash
        if (log.prev_hash or GENESIS_PREV_HASH) != expected_prev:
            issues.append({
                "id": str(log.id),
                "issue": "prev_hash_mismatch",
            })
        payload = _serialise_entry(log)
        expected_hash = _compute_hash(payload)
        if not log.entry_hash or log.entry_hash != expected_hash:
            issues.append({
                "id": str(log.id),
                "issue": "entry_hash_mismatch",
            })
        prev_hash = log.entry_hash or expected_hash
    status = "pass" if not issues else "fail"
    return HashChainReport(status=status, entries_checked=len(logs), issues=issues)


def export_audit_logs(db: Session, fmt: str = "json") -> Tuple[str, str, str]:
    """Export audit logs as CSV or JSON with a detached HMAC signature."""

    logs = db.query(models.AuditLog).order_by(models.AuditLog.id).all()
    if fmt not in {"json", "csv"}:
        raise ValueError("format must be 'json' or 'csv'")

    if fmt == "json":
        import json

        payload = json.dumps([
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "timestamp": log.timestamp.isoformat(),
                "details": log.details,
                "prev_hash": log.prev_hash,
                "entry_hash": log.entry_hash,
            }
            for log in logs
        ])
        mime = "application/json"
    else:
        import csv
        from io import StringIO

        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow([
            "id",
            "user_id",
            "action",
            "entity_type",
            "entity_id",
            "timestamp",
            "details",
            "prev_hash",
            "entry_hash",
        ])
        for log in logs:
            writer.writerow([
                log.id,
                log.user_id,
                log.action,
                log.entity_type,
                log.entity_id,
                log.timestamp.isoformat(),
                log.details,
                log.prev_hash,
                log.entry_hash,
            ])
        payload = buffer.getvalue()
        mime = "text/csv"

    key = os.getenv("AUDIT_EXPORT_SIGNING_KEY", "co-hr-demo-key").encode("utf-8")
    signature = hmac.new(key, payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return payload, signature, mime
