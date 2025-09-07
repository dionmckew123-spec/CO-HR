"""Endpoints for submitting and viewing appeals against incidents."""

from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_db, get_current_user

router = APIRouter(prefix="/appeals", tags=["appeals"])


@router.post("/", response_model=schemas.AppealOut)
def create_appeal(
    appeal_in: schemas.AppealCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new appeal for an incident by the current user."""
    # Verify incident exists and belongs to user
    incident = db.query(models.Incident).filter(models.Incident.id == appeal_in.incident_id).first()
    if incident is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    if incident.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot appeal incidents of other users")
    appeal = models.Appeal(
        user_id=current_user.id,
        incident_id=appeal_in.incident_id,
        reason=appeal_in.reason,
        status=models.AppealStatus.pending,
        created_at=date.today(),
    )
    db.add(appeal)
    db.commit()
    db.refresh(appeal)
    return appeal


@router.get("/", response_model=List[schemas.AppealOut])
def list_appeals(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all appeals submitted by the current user."""
    return db.query(models.Appeal).filter(models.Appeal.user_id == current_user.id).all()