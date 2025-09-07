"""Endpoints for creating and listing probations for users.

This router allows staff or supervisors to record and view probation periods and outcomes
for a particular user. A probation has a start and end date and optional result and notes.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_db, get_current_user

router = APIRouter(prefix="/probations", tags=["probations"])


@router.post("/", response_model=schemas.ProbationOut)
def create_probation(
    probation_in: schemas.ProbationCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new probation record.

    In this simple implementation, any authenticated user can create a probation record
    for themselves. In a more complete system, only supervisors or HR roles would be
    permitted to create or update probations for employees.
    """
    # Only allow creating probation for the current user for now
    if probation_in.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create probation for another user",
        )
    record = models.ProbationStatus(
        user_id=current_user.id,
        start_date=probation_in.start_date,
        end_date=probation_in.end_date,
        result=probation_in.result,
        notes=probation_in.notes,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/", response_model=List[schemas.ProbationOut])
def list_probations(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all probation records for the current user."""
    return db.query(models.ProbationStatus).filter(models.ProbationStatus.user_id == current_user.id).all()