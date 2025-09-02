"""
SQLAlchemy models for DY Crane Safety Management System.
Defines all database tables and their relationships in the ops schema.
"""

import datetime as dt
import uuid
from decimal import Decimal
from typing import Any, List

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )


class User(Base, TimestampMixin):
    """User model representing system users with different roles."""

    __tablename__ = "users"
    __table_args__ = {"schema": "ops"}

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


class Org(Base, TimestampMixin):
    """Organization model for crane owners and manufacturers."""

    __tablename__ = "orgs"
    __table_args__ = {"schema": "ops"}

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[OrgType] = mapped_column(Enum(OrgType), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<Org(id={self.id}, name={self.name}, type={self.type})>"


class UserOrg(Base):
    """Many-to-many relationship between users and organizations."""

    __tablename__ = "user_orgs"
    __table_args__ = {"schema": "ops"}

    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("ops.users.id", ondelete="CASCADE"), primary_key=True
    )
    org_id: Mapped[str] = mapped_column(
        String, ForeignKey("ops.orgs.id", ondelete="CASCADE"), primary_key=True
    )


class Site(Base, TimestampMixin):
    """Construction site model requiring crane services."""

    __tablename__ = "sites"
    __table_args__ = {"schema": "ops"}

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str | None] = mapped_column(String)
    start_date: Mapped[dt.date] = mapped_column(Date, nullable=False)
    end_date: Mapped[dt.date] = mapped_column(Date, nullable=False)
    status: Mapped[SiteStatus] = mapped_column(
        Enum(SiteStatus),
        default=SiteStatus.PENDING_APPROVAL,
        nullable=False,
        index=True,
    )
    requested_by_id: Mapped[str] = mapped_column(
        String, ForeignKey("ops.users.id", ondelete="RESTRICT"), nullable=False
    )
    approved_by_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("ops.users.id", ondelete="SET NULL")
    )
    requested_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    approved_at: Mapped[dt.datetime | None] = mapped_column(DateTime)

    def __repr__(self) -> str:
        return f"<Site(id={self.id}, name={self.name}, status={self.status})>"



# Use JSON for SQLite and JSONB for other dialects like PostgreSQL
JsonVariant = JSON().with_variant(JSONB, "postgresql")
ArrayVariant = JSON().with_variant(ARRAY(String), "postgresql")


class CraneModel(Base, TimestampMixin):
    """Crane model with detailed specifications."""

    __tablename__ = "crane_models"
    __table_args__ = {"schema": "ops"}

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    model_name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    max_lifting_capacity_ton_m: Mapped[int | None] = mapped_column(Integer)
    max_working_height_m: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    max_working_radius_m: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    iver_torque_phi_mm: Mapped[str | None] = mapped_column(String)
    boom_sections: Mapped[int | None] = mapped_column(Integer)
    tele_speed_m_sec: Mapped[str | None] = mapped_column(String)
    boom_angle_speed_deg_sec: Mapped[str | None] = mapped_column(String)
    lifting_load_distance_kg_m: Mapped[dict[str, Any] | None] = mapped_column(
        JsonVariant
    )
    optional_specs: Mapped[List[str] | None] = mapped_column(ArrayVariant)

    def __repr__(self) -> str:
        return f"<CraneModel(id={self.id}, model_name={self.model_name})>"


class Crane(Base, TimestampMixin):
    """Crane instance owned by an organization, based on a model."""

    __tablename__ = "cranes"
    __table_args__ = {"schema": "ops"}

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    owner_org_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("ops.orgs.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    model_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("ops.crane_models.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    serial_no: Mapped[str | None] = mapped_column(String, unique=True)
    status: Mapped[CraneStatus] = mapped_column(
        Enum(CraneStatus), default=CraneStatus.NORMAL, nullable=False, index=True
    )

    model: Mapped["CraneModel"] = relationship("CraneModel")

    def __repr__(self) -> str:
        return (
            f"<Crane(id={self.id}, serial_no={self.serial_no}, status={self.status})>"
        )


class SiteCraneAssignment(Base, TimestampMixin):
    """Assignment of cranes to construction sites."""

    __tablename__ = "site_crane_assignments"
    __table_args__ = {"schema": "ops"}

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    site_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("ops.sites.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    crane_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("ops.cranes.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    assigned_by: Mapped[str] = mapped_column(
        String, ForeignKey("ops.users.id", ondelete="RESTRICT"), nullable=False
    )
    start_date: Mapped[dt.date] = mapped_column(Date, nullable=False)
    end_date: Mapped[dt.date | None] = mapped_column(Date)
    status: Mapped[AssignmentStatus] = mapped_column(
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

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    site_crane_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("ops.site_crane_assignments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    driver_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("ops.users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    start_date: Mapped[dt.date] = mapped_column(Date, nullable=False)
    end_date: Mapped[dt.date | None] = mapped_column(Date)
    status: Mapped[AssignmentStatus] = mapped_column(
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

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    driver_assignment_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("ops.driver_assignments.id", ondelete="CASCADE"),
        nullable=False,
    )
    work_date: Mapped[dt.date] = mapped_column(Date, nullable=False)
    check_in_at: Mapped[dt.datetime] = mapped_column(DateTime, nullable=False)
    check_out_at: Mapped[dt.datetime | None] = mapped_column(DateTime)

    def __repr__(self) -> str:
        return f"<DriverAttendance(id={self.id}, work_date={self.work_date})>"


class DriverDocumentRequest(Base, TimestampMixin):
    """Requests for drivers to submit documents."""

    __tablename__ = "driver_document_requests"
    __table_args__ = {"schema": "ops"}

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    site_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("ops.sites.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    driver_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("ops.users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    requested_by_id: Mapped[str] = mapped_column(
        String, ForeignKey("ops.users.id", ondelete="RESTRICT"), nullable=False
    )
    due_date: Mapped[dt.date | None] = mapped_column(Date)

    def __repr__(self) -> str:
        return f"<DriverDocumentRequest(id={self.id}, driver_id={self.driver_id})>"


class DriverDocumentItem(Base, TimestampMixin):
    """Individual document items within document requests."""

    __tablename__ = "driver_document_items"
    __table_args__ = {"schema": "ops"}

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    request_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("ops.driver_document_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    doc_type: Mapped[str] = mapped_column(String, nullable=False)
    file_url: Mapped[str | None] = mapped_column(Text)
    status: Mapped[DocItemStatus] = mapped_column(
        Enum(DocItemStatus), default=DocItemStatus.PENDING, nullable=False, index=True
    )
    reviewer_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("ops.users.id", ondelete="SET NULL")
    )
    submitted_at: Mapped[dt.datetime | None] = mapped_column(DateTime)
    reviewed_at: Mapped[dt.datetime | None] = mapped_column(DateTime)

    def __repr__(self) -> str:
        return (
            f"<DriverDocumentItem(id={self.id}, doc_type={self.doc_type}, "
            f"status={self.status})>"
        )


class Request(Base, TimestampMixin):
    """Generic requests for workflows like crane deployment."""

    __tablename__ = "requests"
    __table_args__ = {"schema": "ops"}

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    type: Mapped[RequestType] = mapped_column(Enum(RequestType), nullable=False)
    status: Mapped[RequestStatus] = mapped_column(
        Enum(RequestStatus), default=RequestStatus.PENDING, nullable=False, index=True
    )
    requester_id: Mapped[str] = mapped_column(
        String, ForeignKey("ops.users.id", ondelete="CASCADE"), nullable=False
    )
    approver_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("ops.users.id", ondelete="SET NULL")
    )
    target_entity_id: Mapped[str | None] = mapped_column(String, index=True)
    related_entity_id: Mapped[str | None] = mapped_column(String, index=True)
    notes: Mapped[str | None] = mapped_column(Text)
    requested_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    responded_at: Mapped[dt.datetime | None] = mapped_column(DateTime)

    def __repr__(self) -> str:
        return f"<Request(id={self.id}, type={self.type}, status={self.status})>"
