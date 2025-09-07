"""Endpoints for recording and viewing offboarding tasks."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_db, get_current_user

router = APIRouter(prefix="/offboarding", tags=["offboarding"])


@router.post("/", response_model=schemas.OffboardingOut)
def create_offboarding(
    off_in: schemas.OffboardingCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Record offboarding tasks for the current user."""
    record = models.Offboarding(
        user_id=current_user.id,
        date=off_in.date,
        assets_returned=off_in.assets_returned,
        knowledge_transferred=off_in.knowledge_transferred,
        access_restricted=off_in.access_restricted,
        completed=off_in.completed,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/", response_model=List[schemas.OffboardingOut])
def list_offboarding(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List offboarding records for the current user."""
    return db.query(models.Offboarding).filter(models.Offboarding.user_id == current_user.id).all()