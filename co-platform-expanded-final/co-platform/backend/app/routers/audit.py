"""Audit log endpoints.

This router exposes a read-only view of the audit log. Only users with
clearance >= 5 may view audit entries. Recording audit entries must be
implemented in each individual router or via middleware; currently not
all endpoints log actions.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_db, get_current_user
from ..security import has_permission

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("/", response_model=List[schemas.AuditLogOut])
def list_audit_logs(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """List all audit log entries. Requires admin clearance."""
    if not has_permission(current_user, "audit.view", db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    return db.query(models.AuditLog).order_by(models.AuditLog.id).all()