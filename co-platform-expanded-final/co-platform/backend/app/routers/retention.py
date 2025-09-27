"""Data retention management endpoints."""

from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_current_user, get_db
from ..security import has_permission
from ..services import retention as retention_service

router = APIRouter(prefix="/retention", tags=["retention"])


@router.post("/cleanup", response_model=Dict[str, Dict[str, int]])
def cleanup_expired(
    retention_years: int = retention_service.DEFAULT_RETENTION_YEARS,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> Dict[str, Dict[str, int]]:
    if not has_permission(current_user, "privacy.retention", db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    return retention_service.cleanup_expired_records(db, retention_years=retention_years)


@router.get("/extensions", response_model=List[schemas.RetentionExtensionOut])
def list_extensions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> List[schemas.RetentionExtensionOut]:
    if not has_permission(current_user, "privacy.retention", db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    return db.query(models.RetentionExtension).order_by(models.RetentionExtension.extended_until.desc()).all()


@router.post("/extensions", response_model=schemas.RetentionExtensionOut)
def create_extension(
    payload: schemas.RetentionExtensionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.RetentionExtensionOut:
    if not has_permission(current_user, "privacy.retention", db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    record = retention_service.upsert_extension(
        db,
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        extended_until=payload.extended_until,
        reason=payload.reason,
    )
    return record


@router.delete("/extensions/{extension_id}", status_code=204)
def delete_extension(
    extension_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> None:
    if not has_permission(current_user, "privacy.retention", db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    retention_service.delete_extension(db, extension_id)
