"""DSAR (Data Subject Access Request) endpoints.

This router provides an endpoint for exporting all data associated
with a specific user. This feature supports compliance with data
protection regulations such as UK GDPR by enabling staff or
administrators to retrieve a comprehensive record of personal data.

The exported payload includes the user's profile, onboarding status,
leave requests, tickets, incidents, appeals, brag entries, probation
records, training records, offboarding records and attachments. It is
returned as a JSON object without any nested Pydantic models to
simplify consumption by external tools.

Only the user themselves (matching ``user_id``) or administrators
(clearance >= 5) may export data. Attempting to retrieve another
user's data without sufficient clearance will result in a 403 error.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, Dict

from .. import models
from ..dependencies import get_db, get_current_user
from ..security import has_permission

router = APIRouter(prefix="/dsar", tags=["dsar"])


@router.get("/{user_id}")
def export_user_data(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Export all data associated with ``user_id``.

    Only the user themselves or an administrator (clearance >= 5)
    may perform this operation. The response contains a dictionary
    keyed by entity type with lists of serialised records. Date
    fields are converted to ISO strings.
    """
    # Authorization: allow self or users with the privacy.dsar permission
    if current_user.id != user_id:
        # Using has_permission ensures superusers bypass the check
        if not has_permission(current_user, "privacy.dsar", db):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    # Fetch user and ensure existence
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # Collect data into plain dicts
    def to_dict(obj: Any) -> Dict[str, Any]:
        result = {}
        for column in obj.__table__.columns:
            value = getattr(obj, column.name)
            # Convert dates to ISO strings for JSON serialization
            if hasattr(value, "isoformat"):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result
    export: Dict[str, Any] = {
        "user": to_dict(user),
        "onboarding": to_dict(user.onboarding) if user.onboarding else None,
        "leaves": [to_dict(l) for l in user.leaves],
        "tickets": [to_dict(t) for t in user.tickets],
        "incidents": [to_dict(i) for i in db.query(models.Incident).filter(models.Incident.user_id == user_id).all()],
        "appeals": [to_dict(a) for a in db.query(models.Appeal).filter(models.Appeal.user_id == user_id).all()],
        "brag_entries": [to_dict(b) for b in db.query(models.BragEntry).filter(models.BragEntry.user_id == user_id).all()],
        "probations": [to_dict(p) for p in db.query(models.ProbationStatus).filter(models.ProbationStatus.user_id == user_id).all()],
        "training": [to_dict(t) for t in db.query(models.TrainingStatus).filter(models.TrainingStatus.user_id == user_id).all()],
        "offboarding": [to_dict(o) for o in db.query(models.Offboarding).filter(models.Offboarding.user_id == user_id).all()],
        "attachments": [to_dict(att) for att in db.query(models.Attachment).filter(models.Attachment.uploaded_by == user_id).all()],
    }
    return export