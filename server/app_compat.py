"""
DY Crane Safety Management System - Backward Compatibility Module
This module provides backward compatibility by re-exporting components
that existing code (like test.py) expects to import from app.py.
"""

# Import the main application and required components
from main import app
from database import db_manager
from models import *  # Re-export all models
from schemas import *  # Re-export all schemas and enums

# Re-export database components that test.py expects
engine = db_manager.engine
SessionLocal = db_manager.SessionLocal
Base = db_manager.Base

# Re-export for backward compatibility
__all__ = [
    "app", "engine", "SessionLocal", "Base",
    # Models
    "User", "Org", "UserOrg", "Site", "Crane", 
    "SiteCraneAssignment", "DriverAssignment", "DriverAttendance",
    "DriverDocumentRequest", "DriverDocumentItem",
    # Enums 
    "UserRole", "SiteStatus", "CraneStatus", "AssignmentStatus", 
    "DocItemStatus", "OrgType"
]