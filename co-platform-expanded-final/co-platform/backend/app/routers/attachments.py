"""Attachment management endpoints.

These endpoints allow users to associate file metadata with entities in the
system. The actual file upload mechanism is not implemented here; instead
the client must upload the file via an external mechanism (e.g. to a
static/uploads directory) and then create an ``Attachment`` record with the
file name and path. This separation simplifies file handling for the demo.
"""

from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_db, get_current_user
from ..security import has_permission

router = APIRouter(prefix="/attachments", tags=["attachments"])


@router.get("/", response_model=List[schemas.AttachmentOut])
def list_attachments(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """List all attachments. Requires clearance >= 3."""
    if not has_permission(current_user, "attachments.manage", db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    return db.query(models.Attachment).order_by(models.Attachment.id).all()


@router.post("/", response_model=schemas.AttachmentOut)
def create_attachment(
    att_in: schemas.AttachmentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Create an attachment record for an entity.

    ``uploaded_by`` is automatically set to the current user. The client should
    ensure that the file exists at ``file_path`` on the server.
    """
    # Require permission to create attachments; allows superuser bypass
    if not has_permission(current_user, "attachments.manage", db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    attachment = models.Attachment(
        entity_type=att_in.entity_type,
        entity_id=att_in.entity_id,
        file_name=att_in.file_name,
        file_path=att_in.file_path,
        uploaded_by=current_user.id,
        uploaded_at=date.today(),
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment