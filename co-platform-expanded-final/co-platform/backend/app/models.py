"""SQLAlchemy models for the HR/Support system.

The models in this module define the core schema for the application:

- ``Role`` describes different job roles in the organisation and assigns
  a clearance level to each role.
- ``User`` represents staff members and links to a ``Role``. Passwords
  are stored as bcrypt hashes.
- ``OnboardingStatus`` tracks whether a user has signed required
  agreements (policy and confidentiality).
- ``LeaveRequest`` stores leave requests with date ranges and status.
- ``Ticket`` records support tickets raised by users with severity and
  status.

These models are mapped to tables via SQLAlchemy's declarative base.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Enum,
    Boolean,
    Date,
    Text,
)
from sqlalchemy.orm import relationship
import enum

from .database import Base


class Role(Base):
    """Defines a job role with an associated clearance level."""

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    clearance = Column(Integer, nullable=False)

    users = relationship("User", back_populates="role")
    # Relationship to assign permissions to this role. Each RolePermission
    # links a role to a specific Permission entry. When adding new
    # permissions, ensure they are created in the database and associated
    # with roles via RolePermission records.
    role_permissions = relationship(
        "RolePermission", cascade="all, delete-orphan", back_populates="role"
    )


class User(Base):
    """Represents a staff member in the organisation."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_initial = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"))

    role = relationship("Role", back_populates="users")
    onboarding = relationship("OnboardingStatus", uselist=False, back_populates="user")
    leaves = relationship("LeaveRequest", back_populates="user")
    tickets = relationship("Ticket", back_populates="creator")


class OnboardingStatus(Base):
    """Tracks the onboarding agreement signatures for a user."""

    __tablename__ = "onboarding_status"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    policy_signed = Column(Boolean, default=False)
    confidentiality_signed = Column(Boolean, default=False)

    user = relationship("User", back_populates="onboarding")


class LeaveType(str, enum.Enum):
    annual = "annual"
    emergency = "emergency"
    sick = "sick"


class LeaveStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    denied = "denied"


class LeaveRequest(Base):
    """Represents a leave request submitted by a user."""

    __tablename__ = "leaves"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(LeaveType), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(Text)
    status = Column(Enum(LeaveStatus), default=LeaveStatus.pending, nullable=False)

    user = relationship("User", back_populates="leaves")


class TicketSeverity(str, enum.Enum):
    low = "low"
    minor = "minor"
    major = "major"
    critical = "critical"


class TicketStatus(str, enum.Enum):
    open = "open"
    resolved = "resolved"


class Ticket(Base):
    """Represents a support ticket raised by a user."""

    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(Enum(TicketSeverity), default=TicketSeverity.low, nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.open, nullable=False)

    creator = relationship("User", back_populates="tickets")


# Additional models for expanded HR functionality

class ProbationResult(str, enum.Enum):
    pass_ = "pass"
    extend = "extend"
    fail = "fail"


class ProbationStatus(Base):
    """Represents a user's probation period and outcome."""

    __tablename__ = "probations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    result = Column(Enum(ProbationResult), nullable=True)
    notes = Column(Text)

    user = relationship("User")


class TrainingStatus(Base):
    """Tracks completion of training modules by users."""

    __tablename__ = "training_status"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    module_name = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    completion_date = Column(Date, nullable=True)

    user = relationship("User")


class Incident(Base):
    """Records disciplinary or support incidents reported by staff."""

    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(Enum(TicketSeverity), default=TicketSeverity.low, nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.open, nullable=False)

    reporter = relationship("User")


class AppealStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    denied = "denied"


class Appeal(Base):
    """Represents an appeal lodged against an incident or decision."""

    __tablename__ = "appeals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(Enum(AppealStatus), default=AppealStatus.pending, nullable=False)
    created_at = Column(Date, nullable=False)

    user = relationship("User")
    incident = relationship("Incident")


class BragEntry(Base):
    """Represents a BRAG (Behaviour, Relationships, Attitude, Growth) entry for a user."""

    __tablename__ = "brag_entries"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    behaviour = Column(Integer, nullable=False)
    relationships = Column(Integer, nullable=False)
    attitude = Column(Integer, nullable=False)
    growth = Column(Integer, nullable=False)
    notes = Column(Text)

    user = relationship("User")


class Offboarding(Base):
    """Tracks offboarding tasks and status for a departing user."""

    __tablename__ = "offboarding"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    assets_returned = Column(Boolean, default=False)
    knowledge_transferred = Column(Boolean, default=False)
    access_restricted = Column(Boolean, default=False)
    completed = Column(Boolean, default=False)

    user = relationship("User")

# -----------------------------------------------------------------------------
# Settings Model
#
# The Settings model stores organisation-wide configuration that is not tied to
# individual users. Currently it holds the company/organisation name and an
# optional logo URL. Additional configuration fields (e.g., leave allowances,
# contact info) may be added in the future.

class Settings(Base):
    """Represents global settings for the organisation.

    This table is expected to have a single row; however multiple rows are
    allowed to support potential versioning in the future. Clients should
    always fetch the first record (id=1) when reading settings.
    """

    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    # Human-friendly organisation name to display throughout the UI
    company_name = Column(String, nullable=True)
    # URL pointing to the organisation logo (e.g., served from /static)
    logo_url = Column(String, nullable=True)

    # Additional configuration fields
    # Comma-separated list (e.g. "Mon,Tue,Wed,Thu,Fri") representing the working days.
    working_days = Column(String, nullable=True)
    # JSON-encoded list of holiday dates (YYYY-MM-DD strings) for the leave engine.
    holidays_json = Column(Text, nullable=True)
    # JSON-encoded leave policy (min/max durations, accrual, carry-over rules).
    leave_policy_json = Column(Text, nullable=True)
    # JSON-encoded default Discord channel mappings for notifications by module.
    default_channels_json = Column(Text, nullable=True)
    # JSON-encoded feature flags to toggle modules on/off or enable betas.
    feature_flags_json = Column(Text, nullable=True)
    # Number of years to retain data before purging (used by retention cleanup).
    retention_years = Column(Integer, default=4)


# -----------------------------------------------------------------------------
# Permission and RolePermission Models
#
# These models implement a simple permission system. A Permission defines a
# string key (e.g. "settings.edit" or "leave.request.create") and a human-
# friendly description. Roles are associated with zero or more permissions
# through the RolePermission join table. Users inherit permissions from their
# role. Clearance level 5 roles automatically bypass permission checks.

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)

    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission")

# -----------------------------------------------------------------------------
# Webhook Events
#
# Stores Discord webhook configurations. Each record defines an event type and the
# corresponding webhook URL to invoke when that event occurs. The `active`
# flag allows administrators to enable/disable specific webhooks without
# deleting them.

class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False, index=True)
    url = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    description = Column(String, nullable=True)


# -----------------------------------------------------------------------------
# Approvals
#
# Represents a generic approval process. When a user submits a request (e.g.
# leave request, incident report, ticket escalation) that requires approval,
# an ``Approval`` record is created. It tracks the entity being approved, the
# current stage of the approval chain and its status. Implementing multi-step
# approvals requires defining the chain externally; this model only stores
# state.

class ApprovalStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    denied = "denied"
    escalated = "escalated"


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.pending, nullable=False)
    stage = Column(Integer, default=1, nullable=False)
    # User who submitted the request requiring approval
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    # User who approved/denied the request. Nullable until approval action taken.
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(Date, nullable=False)
    updated_at = Column(Date, nullable=False)

    requester = relationship("User", foreign_keys=[requested_by], backref="approvals_requested")
    approver = relationship("User", foreign_keys=[approver_id], backref="approvals_approved")


# -----------------------------------------------------------------------------
# Attachments
#
# Represents a file attached to an entity (ticket, incident, leave request,
# etc.). Actual file storage is out of scope for this demo; the ``file_path``
# should point to a location on the server where the file is stored.

class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(Date, nullable=False)

    uploader = relationship("User", backref="attachments")


# -----------------------------------------------------------------------------
# Audit Logs
#
# Records each significant action in the system for traceability and compliance.
# Not every endpoint currently logs to ``AuditLog``; logging should be added
# incrementally as features expand.

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=True)
    entity_id = Column(Integer, nullable=True)
    timestamp = Column(Date, nullable=False)
    details = Column(Text, nullable=True)

    user = relationship("User", backref="audit_logs")