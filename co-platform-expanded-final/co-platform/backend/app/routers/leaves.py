"""Endpoints for submitting and viewing leave requests."""

from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..dependencies import get_db, get_current_user
from ..services.discord import send_webhook_event
from ..models import Approval, ApprovalStatus

router = APIRouter(prefix="/leaves", tags=["leaves"])


@router.post("/", response_model=schemas.LeaveOut)
def create_leave(
    leave_in: schemas.LeaveCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit a new leave request for the authenticated user."""
    # Basic validation: end date should not precede start date
    if leave_in.end_date < leave_in.start_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="End date must not be before start date")
    leave = models.LeaveRequest(
        user_id=current_user.id,
        type=leave_in.type,
        start_date=leave_in.start_date,
        end_date=leave_in.end_date,
        reason=leave_in.reason,
    )
    db.add(leave)
    db.commit()
    db.refresh(leave)

    # Automatically create an approval request for this leave. The
    # requesting user is the current user; approver and stage are
    # initialised. The approval must be processed by a user with
    # sufficient clearance via the /approvals endpoint.
    approval = Approval(
        entity_type="LeaveRequest",
        entity_id=leave.id,
        status=ApprovalStatus.pending,
        stage=1,
        requested_by=current_user.id,
        approver_id=None,
        created_at=date.today(),
        updated_at=date.today(),
    )
    db.add(approval)
    db.commit()
    db.refresh(approval)
    # Emit webhook notification
    payload = {
        "leave_id": leave.id,
        "user_id": leave.user_id,
        "type": leave.type.value,
        "start_date": str(leave.start_date),
        "end_date": str(leave.end_date),
        "reason": leave.reason,
    }
    try:
        send_webhook_event("leave.requested", payload, db)
    except Exception:
        pass
    return leave


@router.get("/", response_model=List[schemas.LeaveOut])
def list_leaves(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all leave requests for the authenticated user."""
    return db.query(models.LeaveRequest).filter(models.LeaveRequest.user_id == current_user.id).all()