"""
DY Crane Safety Management System - Backward Compatibility Module
This module provides backward compatibility by re-exporting components
that existing code (like test.py) expects to import from app.py.
"""

# Import the main application and required components
from database import db_manager
from main import app

from server.domain.models import (
    Crane,
    DriverAssignment,
    DriverAttendance,
    DriverDocumentItem,
    DriverDocumentRequest,
    Org,
    Request,
    Site,
    SiteCraneAssignment,
    User,
    UserOrg,
)
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

# Re-export database components that test.py expects
engine = db_manager.engine
SessionLocal = db_manager.SessionLocal
Base = db_manager.Base

# Re-export for backward compatibility
__all__ = [
    "app",
    "engine",
    "SessionLocal",
    "Base",
    # Models
    "User",
    "Org",
    "UserOrg",
    "Site",
    "Crane",
    "SiteCraneAssignment",
    "DriverAssignment",
    "DriverAttendance",
    "DriverDocumentRequest",
    "DriverDocumentItem",
    "Request",
    # Enums
    "UserRole",
    "SiteStatus",
    "CraneStatus",
    "AssignmentStatus",
    "DocItemStatus",
    "OrgType",
    "RequestType",
    "RequestStatus",
]
