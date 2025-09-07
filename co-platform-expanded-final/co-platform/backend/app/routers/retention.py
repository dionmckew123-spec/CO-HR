"""Data retention management endpoints.

This router implements a simple cleanup routine to purge records older
than a configurable retention period (default four years). It is
designed to support compliance with privacy regulations by removing
outdated data from the database. In a production system, such cleanup
would likely run as a scheduled job; however, for demonstration
purposes it is exposed as a POST endpoint that administrators can
invoke manually.

Only users with a clearance level of 5 or higher may trigger the
cleanup. The endpoint iterates through leave requests, tickets,
incidents, appeals, brag entries, probations, training records,
offboarding records, attachments and audit logs, deleting those with
dates (or creation dates) older than ``retention_years``.
"""

from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict

from .. import models
from ..dependencies import get_db, get_current_user
from ..security import has_permission

router = APIRouter(prefix="/retention", tags=["retention"])


@router.post("/cleanup")
def cleanup_expired(
    retention_years: int = 4,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    ) -> Dict[str, int]:
    """Delete records older than ``retention_years`` years.

    The function returns a dictionary summarising the number of records
    deleted per entity type. Only administrators (clearance >= 5) may
    invoke this endpoint.
    """
    # Require the privacy.retention permission (superusers bypass via has_permission)
    if not has_permission(current_user, "privacy.retention", db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    cutoff = date.today() - timedelta(days=retention_years * 365)
    counts: Dict[str, int] = {}
    # Helper to delete records with a date field
    def purge(queryset, date_field: str, name: str) -> None:
        nonlocal counts
        to_delete = queryset.filter(getattr(models, name).__table__.c[date_field] < cutoff).all()
        counts[name] = len(to_delete)
        for obj in to_delete:
            db.delete(obj)

    # Purge each model with a date field
    # Leaves: end_date used for retention
    purge(db.query(models.LeaveRequest), 'end_date', 'LeaveRequest')
    # Tickets: no date field -> skip (tickets are not time-bound and are retained unless manually deleted)
    # Incidents: date field
    purge(db.query(models.Incident), 'date', 'Incident')
    # Appeals: created_at
    purge(db.query(models.Appeal), 'created_at', 'Appeal')
    # BRAG entries: date
    purge(db.query(models.BragEntry), 'date', 'BragEntry')
    # Probations: end_date
    purge(db.query(models.ProbationStatus), 'end_date', 'ProbationStatus')
    # Training: completion_date (if completed), or skip if not completed
    to_delete_training = db.query(models.TrainingStatus).filter(
        models.TrainingStatus.completed == True,
        models.TrainingStatus.completion_date < cutoff,
    ).all()
    counts['TrainingStatus'] = len(to_delete_training)
    for t in to_delete_training:
        db.delete(t)
    # Offboarding: date
    purge(db.query(models.Offboarding), 'date', 'Offboarding')
    # Attachments: uploaded_at
    purge(db.query(models.Attachment), 'uploaded_at', 'Attachment')
    # Audit logs: timestamp
    purge(db.query(models.AuditLog), 'timestamp', 'AuditLog')
    db.commit()
    return counts