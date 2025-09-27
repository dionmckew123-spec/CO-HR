"""Retention management helpers."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Dict, Iterable, Tuple

from sqlalchemy.orm import Session

from .. import models

DEFAULT_RETENTION_YEARS = 4


def _cutoff(retention_years: int) -> date:
    return date.today() - timedelta(days=retention_years * 365)


def _extension_lookup(db: Session) -> Dict[Tuple[str, int], models.RetentionExtension]:
    extensions = db.query(models.RetentionExtension).all()
    return {(ext.entity_type, ext.entity_id): ext for ext in extensions}


def _is_extended(obj, entity_type: str, extensions: Dict[Tuple[str, int], models.RetentionExtension]) -> bool:
    if not hasattr(obj, "id"):
        return False
    extension = extensions.get((entity_type, obj.id))
    return bool(extension and extension.extended_until >= date.today())


def _anonymise(obj, fields: Iterable[str]) -> bool:
    changed = False
    for field in fields:
        if hasattr(obj, field):
            setattr(obj, field, "[ANONYMIZED]")
            changed = True
    return changed


def cleanup_expired_records(
    db: Session,
    retention_years: int = DEFAULT_RETENTION_YEARS,
) -> Dict[str, Dict[str, int]]:
    """Remove or anonymise data older than the configured retention window."""

    cutoff = _cutoff(retention_years)
    extensions = _extension_lookup(db)
    results: Dict[str, Dict[str, int]] = {}

    def process(query, model_name: str, date_field: str, anonymise_fields: Iterable[str] | None = None) -> None:
        anonymise_fields = anonymise_fields or []
        table = getattr(models, model_name)
        field = getattr(table, date_field)
        expired = query.filter(field < cutoff).all()
        anonymised = 0
        deleted = 0
        for obj in expired:
            if getattr(obj, "legal_hold", False) or _is_extended(obj, model_name, extensions):
                continue
            if anonymise_fields and _anonymise(obj, anonymise_fields):
                anonymised += 1
            else:
                db.delete(obj)
                deleted += 1
        if anonymised or deleted:
            results[model_name] = {"anonymised": anonymised, "deleted": deleted}

    process(db.query(models.LeaveRequest), "LeaveRequest", "end_date", ["reason"])
    process(db.query(models.Incident), "Incident", "date", ["description"])
    process(db.query(models.Appeal), "Appeal", "created_at", ["reason"])
    process(db.query(models.BragEntry), "BragEntry", "date", ["notes"])
    process(db.query(models.ProbationStatus), "ProbationStatus", "end_date", ["notes"])
    # Only completed training records have a completion date worth checking
    completed_training = db.query(models.TrainingStatus).filter(
        models.TrainingStatus.completed == True,
        models.TrainingStatus.completion_date < cutoff,
    ).all()
    anonymised_training = 0
    deleted_training = 0
    for record in completed_training:
        if getattr(record, "legal_hold", False) or _is_extended(record, "TrainingStatus", extensions):
            continue
        if _anonymise(record, ["module_name"]):
            anonymised_training += 1
        else:
            db.delete(record)
            deleted_training += 1
    if anonymised_training or deleted_training:
        results["TrainingStatus"] = {"anonymised": anonymised_training, "deleted": deleted_training}

    process(db.query(models.Offboarding), "Offboarding", "date", [])
    process(db.query(models.Attachment), "Attachment", "uploaded_at", ["file_name", "file_path"])
    process(db.query(models.AuditLog), "AuditLog", "timestamp", ["details"])

    db.commit()
    return results


def upsert_extension(
    db: Session,
    *,
    entity_type: str,
    entity_id: int,
    extended_until: date,
    reason: str | None,
) -> models.RetentionExtension:
    record = (
        db.query(models.RetentionExtension)
        .filter(
            models.RetentionExtension.entity_type == entity_type,
            models.RetentionExtension.entity_id == entity_id,
        )
        .one_or_none()
    )
    if record is None:
        record = models.RetentionExtension(
            entity_type=entity_type,
            entity_id=entity_id,
            extended_until=extended_until,
            reason=reason,
        )
        db.add(record)
    else:
        record.extended_until = extended_until
        record.reason = reason
    db.commit()
    db.refresh(record)
    return record


def delete_extension(db: Session, extension_id: int) -> None:
    record = db.query(models.RetentionExtension).filter(models.RetentionExtension.id == extension_id).one_or_none()
    if record:
        db.delete(record)
        db.commit()
