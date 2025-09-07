"""Authentication endpoints for the API.

This router provides a login route that verifies user credentials and
issues a JWT access token upon success. Clients should include this
token as a Bearer token in the ``Authorization`` header for
authenticated requests.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from .. import models, schemas, security
from ..dependencies import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """Authenticate a user and return a JWT access token if valid.

    Uses OAuth2PasswordRequestForm, which expects form fields ``username``
    and ``password``. In our system ``username`` corresponds to the user
    email.
    """
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = security.create_access_token(data={"sub": user.id})
    return schemas.Token(access_token=access_token, token_type="bearer")