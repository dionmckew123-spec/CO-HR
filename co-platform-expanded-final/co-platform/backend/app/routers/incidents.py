"""Endpoints for creating and listing incidents (disciplinary/support)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from .. import models, schemas
from ..dependencies import get_db, get_current_user

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post("/", response_model=schemas.IncidentOut)
def create_incident(
    incident_in: schemas.IncidentCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new incident reported by the current user."""
    incident = models.Incident(
        user_id=current_user.id,
        date=incident_in.date,
        description=incident_in.description,
        severity=incident_in.severity,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@router.get("/", response_model=List[schemas.IncidentOut])
def list_incidents(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all incidents reported by the current user."""
    return db.query(models.Incident).filter(models.Incident.user_id == current_user.id).all()