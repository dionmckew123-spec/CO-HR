"""Endpoints for creating and viewing support tickets."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..dependencies import get_db, get_current_user
from ..services.discord import send_webhook_event

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("/", response_model=schemas.TicketOut)
def create_ticket(
    ticket_in: schemas.TicketCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new support ticket for the authenticated user."""
    ticket = models.Ticket(
        user_id=current_user.id,
        title=ticket_in.title,
        description=ticket_in.description,
        severity=ticket_in.severity,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    # Emit webhook notification
    payload = {
        "ticket_id": ticket.id,
        "title": ticket.title,
        "description": ticket.description,
        "severity": ticket.severity.value,
        "user_id": ticket.user_id,
    }
    try:
        send_webhook_event("ticket.created", payload, db)
    except Exception:
        # Ignore webhook failures
        pass
    return ticket


@router.get("/", response_model=List[schemas.TicketOut])
def list_tickets(
    current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """List all tickets created by the authenticated user."""
    return db.query(models.Ticket).filter(models.Ticket.user_id == current_user.id).all()