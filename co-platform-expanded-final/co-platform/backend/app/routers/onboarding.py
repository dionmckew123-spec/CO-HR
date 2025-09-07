"""Endpoints for onboarding agreement tracking."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_db, get_current_user

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.get("/status", response_model=schemas.OnboardingOut)
def get_status(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return the current user's onboarding status."""
    status_record = current_user.onboarding
    if not status_record:
        # Should never happen since onboarding is created with user
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Onboarding status not found")
    return schemas.OnboardingOut(**status_record.__dict__)


@router.post("/sign", response_model=schemas.OnboardingOut)
def sign_agreements(
    update: schemas.OnboardingUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the current user's onboarding agreement signatures.

    The body may include one or both of ``policy_signed`` and
    ``confidentiality_signed``. Only specified fields will be updated.
    """
    status_record = current_user.onboarding
    if not status_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Onboarding status not found")
    if update.policy_signed is not None:
        status_record.policy_signed = update.policy_signed
    if update.confidentiality_signed is not None:
        status_record.confidentiality_signed = update.confidentiality_signed
    db.add(status_record)
    db.commit()
    db.refresh(status_record)
    return schemas.OnboardingOut(**status_record.__dict__)