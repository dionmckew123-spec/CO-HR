"""Approval management endpoints.

This router provides a minimal interface for managing approval records.
When a user submits a request requiring approval (e.g. leave request, ticket
escalation), an ``Approval`` record should be created via these endpoints. The
approval process may involve multiple stages; only the basic creation and
status update operations are implemented here. Further logic (such as
triggering notifications or enforcing multi-step chains) must be built
around these endpoints.
"""

from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_db, get_current_user
from ..security import has_permission

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("/", response_model=List[schemas.ApprovalOut])
def list_approvals(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """List all approvals. Requires approvals.manage permission."""
    if not has_permission(current_user, "approvals.manage", db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    return db.query(models.Approval).order_by(models.Approval.id).all()


@router.post("/", response_model=schemas.ApprovalOut)
def create_approval(
    approval_in: schemas.ApprovalCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Create a new approval request for an entity.

    The ``requested_by`` field is automatically set to the current user's ID,
    and the timestamps are set to the current date.
    """
    approval = models.Approval(
        entity_type=approval_in.entity_type,
        entity_id=approval_in.entity_id,
        status=models.ApprovalStatus.pending,
        stage=1,
        requested_by=current_user.id,
        approver_id=None,
        created_at=date.today(),
        updated_at=date.today(),
    )
    db.add(approval)
    db.commit()
    db.refresh(approval)
    return approval


@router.put("/{approval_id}", response_model=schemas.ApprovalOut)
def update_approval(
    approval_id: int,
    approval_in: schemas.ApprovalUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Update an existing approval (status, stage or approver).

    Requires the approvals.manage permission. The ``updated_at`` field is set
    automatically.
    """
    if not has_permission(current_user, "approvals.manage", db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    approval = db.query(models.Approval).filter(models.Approval.id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval not found")
    # Update allowed fields
    for key, value in approval_in.dict(exclude_unset=True).items():
        setattr(approval, key, value)
    approval.updated_at = date.today()
    db.commit()
    db.refresh(approval)
    return approval