"""Endpoints for recording and viewing training modules for users.

This router exposes endpoints for users to mark completion of training modules and
list their training history. In a more advanced system, supervisors could assign
modules and verify completion. Here we allow users to record their own training.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_db, get_current_user

router = APIRouter(prefix="/training", tags=["training"])


@router.post("/", response_model=schemas.TrainingStatusOut)
def create_training(
    training_in: schemas.TrainingStatusCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a training status record.

    Only allow users to create training records for themselves in this simple
    implementation. They can specify module name and completion status/date.
    """
    if training_in.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot record training for another user",
        )
    record = models.TrainingStatus(
        user_id=current_user.id,
        module_name=training_in.module_name,
        completed=training_in.completed,
        completion_date=training_in.completion_date,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/", response_model=List[schemas.TrainingStatusOut])
def list_training(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List training status entries for the current user."""
    return db.query(models.TrainingStatus).filter(models.TrainingStatus.user_id == current_user.id).all()