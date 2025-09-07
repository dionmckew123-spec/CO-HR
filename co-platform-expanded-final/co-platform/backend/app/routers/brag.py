"""Endpoints for submitting and viewing BRAG entries."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date

from .. import models, schemas
from ..dependencies import get_db, get_current_user

router = APIRouter(prefix="/brag", tags=["brag"])


@router.post("/", response_model=schemas.BragOut)
def create_brag(
    entry_in: schemas.BragCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new BRAG entry for the current user."""
    entry = models.BragEntry(
        user_id=current_user.id,
        date=entry_in.date,
        behaviour=entry_in.behaviour,
        relationships=entry_in.relationships,
        attitude=entry_in.attitude,
        growth=entry_in.growth,
        notes=entry_in.notes,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/", response_model=List[schemas.BragOut])
def list_brag(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all BRAG entries for the current user."""
    return db.query(models.BragEntry).filter(models.BragEntry.user_id == current_user.id).all()