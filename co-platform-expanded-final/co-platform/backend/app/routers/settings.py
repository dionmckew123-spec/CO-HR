"""Settings management endpoints.

This router provides endpoints for reading and updating organisation-wide
settings such as the company name and logo URL. These settings are stored in
the ``settings`` table and are intended to be configured during the initial
setup of the application.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from .. import models, schemas
from ..dependencies import get_db, get_current_user
from ..security import require_permission

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/", response_model=Optional[schemas.SettingsOut])
def read_settings(db: Session = Depends(get_db), current_user: models.User = Depends(require_permission("settings.view"))):
    """Return the current organisation settings, if any.

    Returns ``None`` if no settings record exists. Clients should handle
    this case by providing sensible defaults or prompting the user to
    configure settings.
    """
    settings = db.query(models.Settings).order_by(models.Settings.id).first()
    return settings


@router.post("/", response_model=schemas.SettingsOut)
def upsert_settings(
    settings_in: schemas.SettingsCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_permission("settings.edit")),
):
    """Create or update the organisation settings.

    Requires the caller to have the ``settings.edit`` permission (or
    superuser clearance). If a settings record already exists, its fields
    will be updated with values from ``settings_in``; otherwise, a new
    record is created.
    """
    settings = db.query(models.Settings).order_by(models.Settings.id).first()
    if settings is None:
        settings = models.Settings(**settings_in.dict())
        db.add(settings)
    else:
        for key, value in settings_in.dict(exclude_unset=True).items():
            setattr(settings, key, value)
    db.commit()
    db.refresh(settings)
    return settings