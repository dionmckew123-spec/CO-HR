"""Discord webhook integration service.

This module provides a helper for sending event notifications to Discord via
configured webhook URLs. Each event type may have multiple webhooks
registered. When an event is triggered in the application, call
``send_webhook_event`` with the event type and a payload dictionary. If
external HTTP requests are not permitted (e.g. within certain hosting
environments), the function will log the intended payload instead of
attempting to send it.
"""

import json
from typing import Any, Dict

import requests
from sqlalchemy.orm import Session

from .. import models


def send_webhook_event(event_type: str, payload: Dict[str, Any], db: Session) -> None:
    """Send a notification to all active webhooks registered for the given event.

    Parameters
    ----------
    event_type : str
        The type of event being emitted, e.g. ``"ticket.created"``.
    payload : dict
        A JSON-serialisable dictionary containing the event details. This
        dict will be sent as the body of the POST request to each webhook.
    db : Session
        A SQLAlchemy session used to query the ``WebhookEvent`` table.

    Notes
    -----
    If the environment cannot reach external URLs, this function will simply
    print the payload instead of attempting to send requests. In a real
    deployment, you might handle exceptions or implement retries.
    """
    webhooks = (
        db.query(models.WebhookEvent)
        .filter(models.WebhookEvent.event_type == event_type, models.WebhookEvent.active == True)
        .all()
    )
    if not webhooks:
        return
    for webhook in webhooks:
        try:
            # Send JSON payload to the webhook URL
            response = requests.post(webhook.url, json=payload, timeout=5)
            response.raise_for_status()
        except Exception as exc:
            # In this environment, network calls may fail; log instead
            print(f"[Webhook] Failed to send event '{event_type}' to {webhook.url}: {exc}")
            print("Payload:", json.dumps(payload))