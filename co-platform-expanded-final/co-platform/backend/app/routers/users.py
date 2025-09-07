"""User management endpoints.

This router exposes endpoints for seeding the initial admin user,
creating additional users (requires admin privileges), and fetching
information about the current user.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, security
from ..dependencies import get_db, get_current_user

router = APIRouter(prefix="/users", tags=["users"])


def get_or_create_role(db: Session, name: str, clearance: int) -> models.Role:
    role = db.query(models.Role).filter(models.Role.name == name).first()
    if role:
        return role
    role = models.Role(name=name, clearance=clearance)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@router.post("/seed-admin", response_model=schemas.UserOut)
def seed_admin(user_in: schemas.UserCreate, role_name: str = "President", db: Session = Depends(get_db)):
    """Seed the database with an initial superuser.

    This endpoint may be called only when no users exist. It creates a
    ``Role`` with clearance level 5 (superuser) if one does not already
    exist, seeds baseline permissions, assigns all permissions to the
    superuser role, and creates the first user in that role. The role
    name can be customised via the ``role_name`` query parameter.
    """
    # Prevent seeding if users already exist
    if db.query(models.User).count() > 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Users already exist")
    # Create or fetch the superuser role
    role = get_or_create_role(db, role_name, clearance=5)
    # Define baseline permissions for the system. These keys correspond
    # to actions that can be restricted through the permission system.
    baseline_perms = [
        "settings.view",
        "settings.edit",
        "webhook.manage",
        "leave.request.create",
        "leave.view",
        "leave.approve",
        "ticket.create",
        "ticket.view",
        "incident.create",
        "incident.view",
        "appeal.manage",
        "probation.manage",
        "training.manage",
        "offboarding.manage",
        "audit.view",
        "search.use",
        "attachments.manage",
        "approvals.manage",
        "privacy.dsar",
        "privacy.retention",
    ]
    # Ensure permissions exist and assign them to the role
    for perm_key in baseline_perms:
        perm = db.query(models.Permission).filter(models.Permission.key == perm_key).first()
        if not perm:
            perm = models.Permission(key=perm_key, description=perm_key)
            db.add(perm)
            db.flush()  # assign ID
        # Link permission to role if not already linked
        if not any(rp.permission_id == perm.id for rp in role.role_permissions):
            rp = models.RolePermission(role_id=role.id, permission_id=perm.id)
            db.add(rp)
    # Create the superuser
    hashed_password = security.get_password_hash(user_in.password)
    user = models.User(
        email=user_in.email,
        first_name=user_in.first_name,
        last_initial=user_in.last_initial,
        hashed_password=hashed_password,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    # Create onboarding record
    onboarding = models.OnboardingStatus(user_id=user.id)
    db.add(onboarding)
    db.commit()
    db.refresh(user)
    return user


@router.get("/exists")
def users_exist(db: Session = Depends(get_db)) -> dict:
    """Return whether any users exist in the system.

    This endpoint is used by the frontend to determine whether to display the
    Getting Started page or the Login page. It simply returns a JSON
    object with a single boolean field ``exists``.
    """
    exists = db.query(models.User).count() > 0
    return {"exists": exists}


@router.get("/me", response_model=schemas.UserOut)
def read_current_user(current_user: models.User = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return current_user


@router.post("/", response_model=schemas.UserOut)
def create_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Create a new user (requires admin privileges).

    Only users with a role clearance of 5 (e.g. President) may create
    other users. The caller must supply a role_id for the new user.
    """
    if not current_user.role or current_user.role.clearance < 5:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    # Validate role
    role = None
    if user_in.role_id:
        role = db.query(models.Role).filter(models.Role.id == user_in.role_id).first()
        if role is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role ID")
    # Check email uniqueness
    if db.query(models.User).filter(models.User.email == user_in.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = models.User(
        email=user_in.email,
        first_name=user_in.first_name,
        last_initial=user_in.last_initial,
        hashed_password=security.get_password_hash(user_in.password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    # Add onboarding status for the user
    onboarding = models.OnboardingStatus(user_id=user.id)
    db.add(onboarding)
    db.commit()
    return user