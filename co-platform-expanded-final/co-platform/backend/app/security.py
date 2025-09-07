"""Security utilities for password hashing and JWT creation.

This module wraps ``passlib`` and ``python-jose`` helpers to provide
functions for hashing passwords, verifying them, and generating
JSON Web Tokens (JWT) for authenticated sessions.
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# Additional imports for permission checks
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from .dependencies import get_db, get_current_user
from . import models

from .schemas import TokenData


# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
JWT_SECRET: str = os.getenv("JWT_SECRET", "supersecret")
JWT_ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours validity


def get_password_hash(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(*, data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token with the given data and expiry.

    Args:
        data: The claims to include in the token. Should contain at least a
            ``sub`` key mapping to the subject (user ID).
        expires_delta: Optional timedelta specifying token lifetime. If
            omitted, ``ACCESS_TOKEN_EXPIRE_MINUTES`` is used.

    Returns:
        A JWT encoded string.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """Decode a JWT and return the token data if valid.

    Returns None if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: int = payload.get("sub")  # subject claim contains user ID
        if user_id is None:
            return None
        return TokenData(user_id=user_id)
    except JWTError:
        return None


# -----------------------------------------------------------------------------
# Permission helpers
#
# The application uses a simple role-based permission system layered on top of
# clearance levels. Each role can be granted one or more permissions via
# RolePermission records. Users with a role clearance of 5 or higher are
# considered superusers and bypass permission checks. The functions below
# facilitate permission checks in routes.

def has_permission(user: models.User, perm_key: str, db: Session) -> bool:
    """Return True if the user has the given permission key.

    Superusers (role.clearance >= 5) automatically return True. Otherwise,
    check the permissions associated with the user's role via RolePermission.
    """
    # Superuser bypass
    if user.role and user.role.clearance >= 5:
        return True
    if not user.role:
        return False
    # Query permissions for the role
    perm_keys = (
        db.query(models.Permission.key)
        .join(models.RolePermission, models.RolePermission.permission_id == models.Permission.id)
        .filter(models.RolePermission.role_id == user.role_id)
        .all()
    )
    return any(key == perm_key for (key,) in perm_keys)


def require_permission(perm_key: str):
    """Dependency factory to enforce a permission check on an endpoint.

    Usage: decorate endpoint dependency with ``Depends(require_permission('perm.key'))``. The
    current user and database session are injected via FastAPI dependencies.
    Raises 403 if the user lacks the permission; returns the current user on success.
    """
    def _dep(
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> models.User:
        if has_permission(current_user, perm_key, db):
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    return _dep