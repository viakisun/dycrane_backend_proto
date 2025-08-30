"""
SQLAlchemy models for DY Crane Safety Management System.
Defines all database tables and their relationships in the ops schema.
"""

import uuid

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from server.database import Base
from server.domain.schemas import (
    AssignmentStatus,
    CraneStatus,
    DocItemStatus,
    OrgType,
    RequestStatus,
    RequestType,
    SiteStatus,
    UserRole,
)


class TimestampMixin:
    """Mixin for automatic timestamp management."""

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )


class User(Base, TimestampMixin):
    """User model representing system users with different roles."""

    __tablename__ = "users"
    __table_args__ = {"schema": "ops"}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


class Org(Base, TimestampMixin):
    """Organization model for crane owners and manufacturers."""

    __tablename__ = "orgs"
    __table_args__ = {"schema": "ops"}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    type = Column(Enum(OrgType), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<Org(id={self.id}, name={self.name}, type={self.type})>"


class UserOrg(Base):
    """Many-to-many relationship between users and organizations."""

    __tablename__ = "user_orgs"
    __table_args__ = {"schema": "ops"}

    user_id = Column(
        String, ForeignKey("ops.users.id", ondelete="CASCADE"), primary_key=True
    )
    org_id = Column(
        String, ForeignKey("ops.orgs.id", ondelete="CASCADE"), primary_key=True
    )


class Site(Base, TimestampMixin):
    """Construction site model requiring crane services."""

    __tablename__ = "sites"
    __table_args__ = {"schema": "ops"}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    address = Column(String)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(
        Enum(SiteStatus),
        default=SiteStatus.PENDING_APPROVAL,
        nullable=False,
        index=True,
    )
    requested_by_id = Column(
        String, ForeignKey("ops.users.id", ondelete="RESTRICT"), nullable=False
    )
    approved_by_id = Column(String, ForeignKey("ops.users.id", ondelete="SET NULL"))
    requested_at = Column(DateTime, default=func.now(), nullable=False)
    approved_at = Column(DateTime)

    def __repr__(self) -> str:
        return f"<Site(id={self.id}, name={self.name}, status={self.status})>"


from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy import Numeric

class CraneModel(Base, TimestampMixin):
    """Crane model with detailed specifications."""

    __tablename__ = "crane_models"
    __table_args__ = {"schema": "ops"}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    model_name = Column(String, nullable=False, unique=True)
    max_lifting_capacity_ton_m = Column(Integer)
    max_working_height_m = Column(Numeric(5, 2))
    max_working_radius_m = Column(Numeric(5, 2))
    iver_torque_phi_mm = Column(String)
    boom_sections = Column(Integer)
    tele_speed_m_sec = Column(String)
    boom_angle_speed_deg_sec = Column(String)
    lifting_load_distance_kg_m = Column(JSONB)
    optional_specs = Column(ARRAY(String))

    def __repr__(self) -> str:
        return f"<CraneModel(id={self.id}, model_name={self.model_name})>"


class Crane(Base, TimestampMixin):
    """Crane instance owned by an organization, based on a model."""

    __tablename__ = "cranes"
    __table_args__ = {"schema": "ops"}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_org_id = Column(
        String,
        ForeignKey("ops.orgs.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    model_id = Column(
        String,
        ForeignKey("ops.crane_models.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    serial_no = Column(String, unique=True)
    status = Column(
        Enum(CraneStatus), default=CraneStatus.NORMAL, nullable=False, index=True
    )

    model = relationship("CraneModel")

    def __repr__(self) -> str:
        return f"<Crane(id={self.id}, serial_no={self.serial_no}, status={self.status})>"


class SiteCraneAssignment(Base, TimestampMixin):
    """Assignment of cranes to construction sites."""

    __tablename__ = "site_crane_assignments"
    __table_args__ = {"schema": "ops"}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    site_id = Column(
        String,
        ForeignKey("ops.sites.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    crane_id = Column(
        String,
        ForeignKey("ops.cranes.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    assigned_by = Column(
        String, ForeignKey("ops.users.id", ondelete="RESTRICT"), nullable=False
    )
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    status = Column(
        Enum(AssignmentStatus), default=AssignmentStatus.ASSIGNED, nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<SiteCraneAssignment(id={self.id}, site_id={self.site_id}, "
            f"crane_id={self.crane_id})>"
        )


class DriverAssignment(Base, TimestampMixin):
    """Assignment of drivers to site-crane combinations."""

    __tablename__ = "driver_assignments"
    __table_args__ = {"schema": "ops"}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    site_crane_id = Column(
        String,
        ForeignKey("ops.site_crane_assignments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    driver_id = Column(
        String,
        ForeignKey("ops.users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    status = Column(
        Enum(AssignmentStatus), default=AssignmentStatus.ASSIGNED, nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<DriverAssignment(id={self.id}, driver_id={self.driver_id}, "
            f"site_crane_id={self.site_crane_id})>"
        )


class DriverAttendance(Base, TimestampMixin):
    """Daily attendance records for drivers."""

    __tablename__ = "driver_attendance"
    __table_args__ = (
        UniqueConstraint(
            "driver_assignment_id", "work_date", name="uq_attendance_unique_day"
        ),
        {"schema": "ops"},
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    driver_assignment_id = Column(
        String,
        ForeignKey("ops.driver_assignments.id", ondelete="CASCADE"),
        nullable=False,
    )
    work_date = Column(Date, nullable=False)
    check_in_at = Column(DateTime, nullable=False)
    check_out_at = Column(DateTime)

    def __repr__(self) -> str:
        return f"<DriverAttendance(id={self.id}, work_date={self.work_date})>"


class DriverDocumentRequest(Base, TimestampMixin):
    """Requests for drivers to submit documents."""

    __tablename__ = "driver_document_requests"
    __table_args__ = {"schema": "ops"}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    site_id = Column(
        String,
        ForeignKey("ops.sites.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    driver_id = Column(
        String,
        ForeignKey("ops.users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    requested_by_id = Column(
        String, ForeignKey("ops.users.id", ondelete="RESTRICT"), nullable=False
    )
    due_date = Column(Date)

    def __repr__(self) -> str:
        return f"<DriverDocumentRequest(id={self.id}, driver_id={self.driver_id})>"


class DriverDocumentItem(Base, TimestampMixin):
    """Individual document items within document requests."""

    __tablename__ = "driver_document_items"
    __table_args__ = {"schema": "ops"}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = Column(
        String,
        ForeignKey("ops.driver_document_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    doc_type = Column(String, nullable=False)
    file_url = Column(Text)
    status = Column(
        Enum(DocItemStatus), default=DocItemStatus.PENDING, nullable=False, index=True
    )
    reviewer_id = Column(String, ForeignKey("ops.users.id", ondelete="SET NULL"))
    submitted_at = Column(DateTime)
    reviewed_at = Column(DateTime)

    def __repr__(self) -> str:
        return (
            f"<DriverDocumentItem(id={self.id}, doc_type={self.doc_type}, "
            f"status={self.status})>"
        )


class Request(Base, TimestampMixin):
    """Generic requests for workflows like crane deployment."""

    __tablename__ = "requests"
    __table_args__ = {"schema": "ops"}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(Enum(RequestType), nullable=False)
    status = Column(
        Enum(RequestStatus), default=RequestStatus.PENDING, nullable=False, index=True
    )
    requester_id = Column(
        String, ForeignKey("ops.users.id", ondelete="CASCADE"), nullable=False
    )
    approver_id = Column(String, ForeignKey("ops.users.id", ondelete="SET NULL"))
    target_entity_id = Column(String, index=True)
    related_entity_id = Column(String, index=True)
    notes = Column(Text)
    requested_at = Column(DateTime, default=func.now(), nullable=False)
    responded_at = Column(DateTime)

    def __repr__(self) -> str:
        return f"<Request(id={self.id}, type={self.type}, status={self.status})>"
