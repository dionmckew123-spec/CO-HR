"""Pydantic schemas for request and response bodies.

This module defines typed models that validate and serialise input and
output data for the API endpoints. Using Pydantic ensures strict
validation of request payloads and helps generate accurate OpenAPI
documentation.
"""

from datetime import date
from typing import Optional, List

from pydantic import BaseModel, EmailStr

from .models import LeaveType, LeaveStatus, TicketSeverity, TicketStatus
from .models import ProbationResult, AppealStatus, ApprovalStatus


class RoleBase(BaseModel):
    name: str
    clearance: int


class RoleOut(RoleBase):
    id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_initial: str
    role_id: Optional[int] = None


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    role: Optional[RoleOut] = None

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


class OnboardingUpdate(BaseModel):
    policy_signed: Optional[bool] = None
    confidentiality_signed: Optional[bool] = None


class OnboardingOut(BaseModel):
    policy_signed: bool
    confidentiality_signed: bool

    class Config:
        from_attributes = True


class LeaveCreate(BaseModel):
    type: LeaveType
    start_date: date
    end_date: date
    reason: Optional[str] = None


class LeaveOut(BaseModel):
    id: int
    type: LeaveType
    start_date: date
    end_date: date
    reason: Optional[str] = None
    status: LeaveStatus

    class Config:
        from_attributes = True


class TicketCreate(BaseModel):
    title: str
    description: str
    severity: Optional[TicketSeverity] = TicketSeverity.low


class TicketOut(BaseModel):
    id: int
    title: str
    description: str
    severity: TicketSeverity
    status: TicketStatus

    class Config:
        from_attributes = True


# Additional schemas for expanded HR functionality


class ProbationCreate(BaseModel):
    user_id: int
    start_date: date
    end_date: date
    result: Optional[ProbationResult] = None
    notes: Optional[str] = None


class ProbationOut(BaseModel):
    id: int
    user_id: int
    start_date: date
    end_date: date
    result: Optional[ProbationResult]
    notes: Optional[str]

    class Config:
        from_attributes = True


class TrainingStatusCreate(BaseModel):
    user_id: int
    module_name: str
    completed: bool = False
    completion_date: Optional[date] = None


class TrainingStatusOut(BaseModel):
    id: int
    user_id: int
    module_name: str
    completed: bool
    completion_date: Optional[date]

    class Config:
        from_attributes = True


class IncidentCreate(BaseModel):
    date: date
    description: str
    severity: TicketSeverity = TicketSeverity.low


class IncidentOut(BaseModel):
    id: int
    date: date
    description: str
    severity: TicketSeverity
    status: TicketStatus

    class Config:
        from_attributes = True


class AppealCreate(BaseModel):
    incident_id: int
    reason: str


class AppealOut(BaseModel):
    id: int
    user_id: int
    incident_id: int
    reason: str
    status: AppealStatus
    created_at: date

    class Config:
        from_attributes = True


class BragCreate(BaseModel):
    date: date
    behaviour: int
    relationships: int
    attitude: int
    growth: int
    notes: Optional[str] = None


class BragOut(BaseModel):
    id: int
    date: date
    behaviour: int
    relationships: int
    attitude: int
    growth: int
    notes: Optional[str]

    class Config:
        from_attributes = True


class OffboardingCreate(BaseModel):
    date: date
    assets_returned: bool = False
    knowledge_transferred: bool = False
    access_restricted: bool = False
    completed: bool = False


class OffboardingOut(BaseModel):
    id: int
    user_id: int
    date: date
    assets_returned: bool
    knowledge_transferred: bool
    access_restricted: bool
    completed: bool

    class Config:
        from_attributes = True

# -----------------------------------------------------------------------------
# Webhook schemas
#

class WebhookEventCreate(BaseModel):
    event_type: str
    url: str
    active: Optional[bool] = True
    description: Optional[str] = None


class WebhookEventOut(BaseModel):
    id: int
    event_type: str
    url: str
    active: bool
    description: Optional[str]

    class Config:
        from_attributes = True

# -----------------------------------------------------------------------------
# Approval schemas
#

class ApprovalCreate(BaseModel):
    entity_type: str
    entity_id: int


class ApprovalUpdate(BaseModel):
    status: Optional[ApprovalStatus] = None
    stage: Optional[int] = None
    approver_id: Optional[int] = None


class ApprovalOut(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    status: ApprovalStatus
    stage: int
    requested_by: int
    approver_id: Optional[int]
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True

# -----------------------------------------------------------------------------
# Attachment schemas
#

class AttachmentCreate(BaseModel):
    entity_type: str
    entity_id: int
    file_name: str
    file_path: str


class AttachmentOut(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    file_name: str
    file_path: str
    uploaded_by: int
    uploaded_at: date

    class Config:
        from_attributes = True

# -----------------------------------------------------------------------------
# Audit log schemas
#

class AuditLogOut(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    entity_type: Optional[str]
    entity_id: Optional[int]
    timestamp: date
    details: Optional[str]
    prev_hash: Optional[str]
    entry_hash: Optional[str]
    retention_expires_at: Optional[date]
    legal_hold: bool

    class Config:
        from_attributes = True


class RetentionExtensionCreate(BaseModel):
    entity_type: str
    entity_id: int
    extended_until: date
    reason: Optional[str] = None


class RetentionExtensionOut(RetentionExtensionCreate):
    id: int

    class Config:
        from_attributes = True

# -----------------------------------------------------------------------------
# Settings schemas
#
# These Pydantic models describe the payloads and responses for managing
# organisation-wide settings. The ``SettingsCreate`` schema is used when
# initially configuring the system via the Getting Started page, while
# ``SettingsOut`` serialises the saved settings back to clients.


class SettingsCreate(BaseModel):
    company_name: Optional[str] = None
    logo_url: Optional[str] = None
    working_days: Optional[str] = None
    holidays_json: Optional[str] = None
    leave_policy_json: Optional[str] = None
    default_channels_json: Optional[str] = None
    feature_flags_json: Optional[str] = None
    retention_years: Optional[int] = None


class SettingsOut(BaseModel):
    id: int
    company_name: Optional[str]
    logo_url: Optional[str]
    working_days: Optional[str]
    holidays_json: Optional[str]
    leave_policy_json: Optional[str]
    default_channels_json: Optional[str]
    feature_flags_json: Optional[str]
    retention_years: Optional[int]

    class Config:
        from_attributes = True