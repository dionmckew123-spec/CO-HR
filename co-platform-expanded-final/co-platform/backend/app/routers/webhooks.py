"""Webhook management endpoints.

This router allows administrators to configure Discord webhooks for various
event types. Each webhook record stores an event type (e.g. ``ticket.created``)
and a URL. When an event occurs in the application, the service will send
a POST request to the registered URLs. Only users with a role clearance
level of 5 or higher may manage webhooks.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..dependencies import get_db, get_current_user
from ..security import require_permission

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def require_admin(current_user: models.User, db: Session) -> None:
    """Legacy admin check. Retained for backward compatibility."""
    # Use the has_permission helper for the webhook.manage permission
    from ..security import has_permission
    if not has_permission(current_user, "webhook.manage", db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")


@router.get("/", response_model=List[schemas.WebhookEventOut])
def list_webhooks(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_permission("webhook.manage")),
):
    """List all registered webhooks."""
    return db.query(models.WebhookEvent).order_by(models.WebhookEvent.id).all()


@router.post("/", response_model=schemas.WebhookEventOut)
def create_webhook(
    webhook_in: schemas.WebhookEventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_permission("webhook.manage")),
):
    """Create a new webhook configuration."""
    webhook = models.WebhookEvent(
        event_type=webhook_in.event_type,
        url=webhook_in.url,
        active=webhook_in.active,
        description=webhook_in.description,
    )
    db.add(webhook)
    db.commit()
    db.refresh(webhook)
    return webhook


@router.put("/{webhook_id}", response_model=schemas.WebhookEventOut)
def update_webhook(
    webhook_id: int,
    webhook_in: schemas.WebhookEventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_permission("webhook.manage")),
):
    """Update an existing webhook configuration."""
    webhook = db.query(models.WebhookEvent).filter(models.WebhookEvent.id == webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")
    for key, value in webhook_in.dict().items():
        setattr(webhook, key, value)
    db.commit()
    db.refresh(webhook)
    return webhook


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_webhook(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_permission("webhook.manage")),
):
    """Delete a webhook configuration."""
    webhook = db.query(models.WebhookEvent).filter(models.WebhookEvent.id == webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")
    db.delete(webhook)
    db.commit()
    return None