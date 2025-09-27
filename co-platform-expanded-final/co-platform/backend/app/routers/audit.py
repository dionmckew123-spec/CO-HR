"""Audit log endpoints including hash chain verification and export."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_current_user, get_db
from ..security import has_permission
from ..services.audit_chain import export_audit_logs, verify_hash_chain

router = APIRouter(prefix="/audit", tags=["audit"])
legacy_router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("/logs", response_model=List[schemas.AuditLogOut])
def list_audit_logs(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not has_permission(current_user, "audit.view", db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    return db.query(models.AuditLog).order_by(models.AuditLog.id).all()


@router.get("/verify-hash-chain")
def verify_chain(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not has_permission(current_user, "audit.view", db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    report = verify_hash_chain(db)
    return {
        "status": report.status,
        "entries_checked": report.entries_checked,
        "issues": report.issues,
    }


@router.get("/export")
def export_logs(
    fmt: str = Query("json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not has_permission(current_user, "audit.view", db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    payload, signature, mime = export_audit_logs(db, fmt)
    return {
        "format": fmt,
        "mime": mime,
        "payload": payload,
        "signature": signature,
    }


@legacy_router.get("/", response_model=List[schemas.AuditLogOut])
def legacy_list(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return list_audit_logs(db=db, current_user=current_user)
