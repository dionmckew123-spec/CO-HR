"""A simplified HR & Support system without external dependencies.

This module implements a basic in-memory HR and support platform
supporting user authentication, onboarding agreements, leave requests,
and support tickets. It uses Python dictionaries to persist data
while the server is running and issues simple session tokens for
authentication. Static HTML pages live in ``app/static`` and provide
a browser interface via fetch API calls to these endpoints.

NOTE: This implementation stores passwords in plain text and does not
persist data across restarts; it is intended for demonstration
purposes only. In production one should use a proper database and
password hashing.
"""

import os
import uuid
from datetime import datetime
from typing import Optional, Dict, List

from fastapi import FastAPI, HTTPException, status, Depends, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr

# --------------------------------------------------------------------------------------
# In-memory storage
# --------------------------------------------------------------------------------------

# Global data store. Keys map to lists/dictionaries representing tables.
DATA: Dict[str, Dict] = {
    "roles": {},  # role_id -> {name, clearance}
    "users": {},  # user_id -> {email, first_name, last_initial, password, role_id}
    "onboarding": {},  # user_id -> {policy_signed, confidentiality_signed}
    "leaves": {},  # leave_id -> {user_id, type, start_date, end_date, reason, status}
    "tickets": {},  # ticket_id -> {user_id, title, description, severity, status}
}

# Simple token store mapping token -> user_id
TOKENS: Dict[str, str] = {}

# Auto-increment counters for ids
COUNTERS = {"role": 1, "user": 1, "leave": 1, "ticket": 1}

# Enum-like constants
LEAVE_STATUSES = {"pending", "approved", "denied"}
LEAVE_TYPES = {"annual", "emergency", "sick"}
TICKET_SEVERITIES = {"low", "minor", "major", "critical"}
TICKET_STATUSES = {"open", "resolved"}


# --------------------------------------------------------------------------------------
# Pydantic models for request/response bodies
# --------------------------------------------------------------------------------------

class SeedAdminRequest(BaseModel):
    # Note: EmailStr normally validates email addresses using email-validator,
    # which isn't installed in this environment. We use plain str instead.
    email: str
    first_name: str
    last_initial: str
    password: str
    role_name: Optional[str] = "President"


class LoginRequest(BaseModel):
    # Use plain str for email to avoid dependency on email-validator
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class OnboardingUpdate(BaseModel):
    policy_signed: Optional[bool] = None
    confidentiality_signed: Optional[bool] = None


class LeaveCreate(BaseModel):
    type: str
    start_date: str  # ISO date
    end_date: str
    reason: Optional[str] = None

    def validate_dates(self):
        try:
            sd = datetime.fromisoformat(self.start_date).date()
            ed = datetime.fromisoformat(self.end_date).date()
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format")
        if ed < sd:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="End date must not be before start date")


class TicketCreate(BaseModel):
    title: str
    description: str
    severity: Optional[str] = "low"


# --------------------------------------------------------------------------------------
# Utility functions
# --------------------------------------------------------------------------------------

def get_next_id(name: str) -> int:
    COUNTERS[name] += 1
    return COUNTERS[name] - 1


def create_role(name: str, clearance: int) -> int:
    role_id = get_next_id("role")
    DATA["roles"][role_id] = {"name": name, "clearance": clearance}
    return role_id


def get_role_by_name(name: str) -> Optional[int]:
    for rid, role in DATA["roles"].items():
        if role["name"] == name:
            return rid
    return None


def seed_admin(req: SeedAdminRequest):
    if DATA["users"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Users already exist")
    role_id = get_role_by_name(req.role_name)
    if role_id is None:
        role_id = create_role(req.role_name, clearance=5)
    user_id = get_next_id("user")
    DATA["users"][user_id] = {
        "email": req.email,
        "first_name": req.first_name,
        "last_initial": req.last_initial,
        "password": req.password,
        "role_id": role_id,
    }
    DATA["onboarding"][user_id] = {"policy_signed": False, "confidentiality_signed": False}
    return user_id


def authenticate_user(email: str, password: str) -> Optional[int]:
    for uid, user in DATA["users"].items():
        if user["email"] == email and user["password"] == password:
            return uid
    return None


def create_token(user_id: int) -> str:
    token = uuid.uuid4().hex
    TOKENS[token] = user_id
    return token


def get_current_user(token: str) -> Dict:
    user_id = TOKENS.get(token)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return {"id": user_id, **DATA["users"][user_id]}


# --------------------------------------------------------------------------------------
# FastAPI application
# --------------------------------------------------------------------------------------

app = FastAPI(title="Simple HR & Support API", version="0.1.0-simple")

# Configure CORS for local development (optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Authentication endpoints
@app.post("/auth/login", response_model=TokenResponse)
def login(req: LoginRequest):
    user_id = authenticate_user(req.email, req.password)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    token = create_token(user_id)
    return TokenResponse(access_token=token)


# Helper dependency to extract bearer token from Authorization header
def require_token(Authorization: Optional[str] = Header(None)) -> str:
    """Extracts and returns the bearer token from the Authorization header."""
    if not Authorization or not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    return Authorization.split(" ", 1)[1]


# User endpoints
@app.post("/users/seed-admin", response_model=Dict)
def api_seed_admin(req: SeedAdminRequest):
    user_id = seed_admin(req)
    return {"id": user_id, **DATA["users"][user_id]}


@app.get("/users/me", response_model=Dict)
def api_users_me(token: str = Depends(require_token)):
    return get_current_user(token)


# Onboarding
@app.get("/onboarding/status", response_model=Dict)
def api_onboarding_status(token: str = Depends(require_token)):
    user = get_current_user(token)
    status_dict = DATA["onboarding"][user["id"]]
    return status_dict


@app.post("/onboarding/sign", response_model=Dict)
def api_onboarding_sign(update: OnboardingUpdate, token: str = Depends(require_token)):
    user = get_current_user(token)
    record = DATA["onboarding"][user["id"]]
    if update.policy_signed is not None:
        record["policy_signed"] = update.policy_signed
    if update.confidentiality_signed is not None:
        record["confidentiality_signed"] = update.confidentiality_signed
    return record


# Leave management
@app.get("/leaves/", response_model=List[Dict])
def api_list_leaves(token: str = Depends(require_token)):
    user = get_current_user(token)
    result = []
    for lid, leave in DATA["leaves"].items():
        if leave["user_id"] == user["id"]:
            item = {"id": lid, **leave}
            result.append(item)
    return result


@app.post("/leaves/", response_model=Dict)
def api_create_leave(leave: LeaveCreate, token: str = Depends(require_token)):
    user = get_current_user(token)
    if leave.type not in LEAVE_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid leave type: {leave.type}")
    leave.validate_dates()
    leave_id = get_next_id("leave")
    DATA["leaves"][leave_id] = {
        "user_id": user["id"],
        "type": leave.type,
        "start_date": leave.start_date,
        "end_date": leave.end_date,
        "reason": leave.reason,
        "status": "pending",
    }
    return {"id": leave_id, **DATA["leaves"][leave_id]}


# Ticket management
@app.get("/tickets/", response_model=List[Dict])
def api_list_tickets(token: str = Depends(require_token)):
    user = get_current_user(token)
    result = []
    for tid, tk in DATA["tickets"].items():
        if tk["user_id"] == user["id"]:
            result.append({"id": tid, **tk})
    return result


@app.post("/tickets/", response_model=Dict)
def api_create_ticket(ticket: TicketCreate, token: str = Depends(require_token)):
    user = get_current_user(token)
    severity = ticket.severity or "low"
    if severity not in TICKET_SEVERITIES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid severity: {severity}")
    ticket_id = get_next_id("ticket")
    DATA["tickets"][ticket_id] = {
        "user_id": user["id"],
        "title": ticket.title,
        "description": ticket.description,
        "severity": severity,
        "status": "open",
    }
    return {"id": ticket_id, **DATA["tickets"][ticket_id]}


# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")