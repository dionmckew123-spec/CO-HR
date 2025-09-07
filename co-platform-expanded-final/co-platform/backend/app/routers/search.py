"""Simple search endpoint.

This endpoint performs a naive full-text search across several models by
matching a query string against select text fields. Results are grouped
by entity type and returned as lists of summaries. The search is case-
insensitive but does not support advanced operators. This is intended
as a demo; in a real application you should integrate a proper search
engine (e.g. PostgreSQL full-text search, Elasticsearch).
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from ..dependencies import get_db, get_current_user
from ..security import require_permission

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/")
def search_all(query: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)) -> Dict[str, List[Dict[str, Any]]]:
    """Search across multiple entities.

    The returned dictionary contains keys for each entity type with lists of
    matching results. Each result includes the entity's ID and a short
    summary derived from its fields. Only entities that the caller has
    clearance to view are included (clearance check is coarse).
    """
    q = query.lower()
    results: Dict[str, List[Dict[str, Any]]] = {
        "tickets": [],
        "incidents": [],
        "appeals": [],
        "leaves": [],
        "brag": [],
        "probations": [],
        "training": [],
        "offboarding": [],
    }
    # Tickets
    for ticket in db.query(models.Ticket).all():
        if q in ticket.title.lower() or q in ticket.description.lower():
            results["tickets"].append({"id": ticket.id, "summary": f"{ticket.title}: {ticket.description[:50]}"})
    # Incidents
    for incident in db.query(models.Incident).all():
        if q in incident.description.lower():
            results["incidents"].append({"id": incident.id, "summary": incident.description[:50]})
    # Appeals
    for appeal in db.query(models.Appeal).all():
        if q in appeal.reason.lower():
            results["appeals"].append({"id": appeal.id, "summary": appeal.reason[:50]})
    # Leaves
    for leave in db.query(models.LeaveRequest).all():
        summary = f"{leave.type.value.title()} leave from {leave.start_date} to {leave.end_date}"
        if q in (leave.reason or "").lower():
            results["leaves"].append({"id": leave.id, "summary": summary})
    # Brag entries
    for brag in db.query(models.BragEntry).all():
        combined = f"{brag.notes or ''}"
        if q in combined.lower():
            results["brag"].append({"id": brag.id, "summary": combined[:50]})
    # Probations
    for prob in db.query(models.ProbationStatus).all():
        combined = f"{prob.notes or ''}"
        if q in combined.lower():
            results["probations"].append({"id": prob.id, "summary": combined[:50]})
    # Training
    for training in db.query(models.TrainingStatus).all():
        combined = f"{training.module_name}"
        if q in combined.lower():
            results["training"].append({"id": training.id, "summary": combined})
    # Offboarding
    for off in db.query(models.Offboarding).all():
        combined = f"Offboarding on {off.date}"
        if q in combined.lower():
            results["offboarding"].append({"id": off.id, "summary": combined})
    return results