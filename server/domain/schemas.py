"""
Pydantic schemas and enums for DY Crane Safety Management System.
Defines API request/response models and validation rules.
"""

import datetime as dt
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, AnyHttpUrl, ConfigDict, field_validator


# ========= ENUMS =========

class UserRole(str, Enum):
    """User roles in the system."""
    DRIVER = "DRIVER"
    SAFETY_MANAGER = "SAFETY_MANAGER"
    OWNER = "OWNER"
    MANUFACTURER = "MANUFACTURER"


class SiteStatus(str, Enum):
    """Construction site status values."""
    PENDING_APPROVAL = "PENDING_APPROVAL"
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"


class CraneStatus(str, Enum):
    """Crane operational status values."""
    NORMAL = "NORMAL"      # Available for assignment
    REPAIR = "REPAIR"      # Under maintenance
    INBOUND = "INBOUND"    # Being transported


class AssignmentStatus(str, Enum):
    """Assignment status for both crane and driver assignments."""
    ASSIGNED = "ASSIGNED"
    RELEASED = "RELEASED"


class DocItemStatus(str, Enum):
    """Document item review status."""
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class OrgType(str, Enum):
    """Organization type classification."""
    OWNER = "OWNER"              # Construction company owning cranes
    MANUFACTURER = "MANUFACTURER"  # Crane manufacturer providing approval


# ========= REQUEST SCHEMAS =========

class SiteCreate(BaseModel):
    """Schema for creating a new construction site."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Site name")
    address: Optional[str] = Field(None, description="Site address")
    start_date: dt.date = Field(..., description="Project start date")
    end_date: dt.date = Field(..., description="Project end date")
    requested_by_id: str = Field(..., description="SAFETY_MANAGER user ID")
    
    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, info):
        """Ensure end_date is after start_date."""
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError('end_date must be after start_date')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Downtown Construction Site",
                "address": "123 Main Street, Seoul",
                "start_date": "2025-09-01",
                "end_date": "2025-12-31",
                "requested_by_id": "safety-manager-uuid"
            }
        }
    )

class SiteUpdate(BaseModel):
    """Schema for updating a site. All fields are optional."""
    name: Optional[str] = None
    address: Optional[str] = None
    start_date: Optional[dt.date] = None
    end_date: Optional[dt.date] = None
    status: Optional[SiteStatus] = None


class SiteApprove(BaseModel):
    """Schema for approving a construction site."""
    
    approved_by_id: str = Field(..., description="MANUFACTURER user ID")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "approved_by_id": "manufacturer-uuid"
            }
        }
    )


class AssignCraneIn(BaseModel):
    """Schema for assigning a crane to a site."""
    
    site_id: str = Field(..., description="Target site ID")
    crane_id: str = Field(..., description="Crane to assign")
    safety_manager_id: str = Field(..., description="SAFETY_MANAGER user ID")
    start_date: dt.date = Field(..., description="Assignment start date")
    end_date: Optional[dt.date] = Field(None, description="Assignment end date")
    
    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, info):
        """Ensure end_date is after start_date if provided."""
        if v is not None and 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class AssignDriverIn(BaseModel):
    """Schema for assigning a driver to a site-crane combination."""
    
    site_crane_id: str = Field(..., description="Site-crane assignment ID")
    driver_id: str = Field(..., description="DRIVER user ID")
    start_date: dt.date = Field(..., description="Driver assignment start date")
    end_date: Optional[dt.date] = Field(None, description="Driver assignment end date")
    
    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, info):
        """Ensure end_date is after start_date if provided."""
        if v is not None and 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class AttendanceIn(BaseModel):
    """Schema for recording driver attendance."""
    
    driver_assignment_id: str = Field(..., description="Driver assignment ID")
    work_date: dt.date = Field(..., description="Work date")
    check_in_at: dt.datetime = Field(..., description="Check-in timestamp")
    check_out_at: Optional[dt.datetime] = Field(None, description="Check-out timestamp")
    
    @field_validator('check_out_at')
    @classmethod
    def validate_time_range(cls, v, info):
        """Ensure check_out_at is after check_in_at if provided."""
        if v is not None and 'check_in_at' in info.data and v < info.data['check_in_at']:
            raise ValueError('check_out_at must be after check_in_at')
        return v


class DocRequestIn(BaseModel):
    """Schema for creating a document request."""
    
    site_id: str = Field(..., description="Site ID")
    driver_id: str = Field(..., description="Driver user ID")
    requested_by_id: str = Field(..., description="SAFETY_MANAGER user ID")
    due_date: Optional[dt.date] = Field(None, description="Document submission due date")


class DocItemSubmitIn(BaseModel):
    """Schema for submitting a document item."""
    
    request_id: str = Field(..., description="Document request ID")
    doc_type: str = Field(..., min_length=1, description="Document type")
    file_url: AnyHttpUrl = Field(..., description="HTTPS URL to document file")


class DocItemReviewIn(BaseModel):
    """Schema for reviewing a document item."""
    
    item_id: str = Field(..., description="Document item ID")
    reviewer_id: str = Field(..., description="SAFETY_MANAGER user ID")
    approve: bool = Field(..., description="True to approve, False to reject")


# ========= RESPONSE SCHEMAS =========

class SiteOut(BaseModel):
    """Schema for site information in API responses."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    name: str
    address: Optional[str] = None
    start_date: dt.date
    end_date: dt.date
    status: SiteStatus
    requested_by_id: str
    approved_by_id: Optional[str] = None
    requested_at: dt.datetime
    approved_at: Optional[dt.datetime] = None
    created_at: dt.datetime
    updated_at: dt.datetime


class CraneOut(BaseModel):
    """Schema for crane information in API responses."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    owner_org_id: str
    model_name: str
    serial_no: Optional[str] = None
    status: CraneStatus
    created_at: dt.datetime
    updated_at: dt.datetime


class AssignmentResponse(BaseModel):
    """Schema for crane assignment operation responses."""
    
    assignment_id: str = Field(..., description="Created assignment ID")


class DriverAssignmentResponse(BaseModel):
    """Schema for driver assignment operation responses."""
    
    driver_assignment_id: str = Field(..., description="Created driver assignment ID")


class AttendanceResponse(BaseModel):
    """Schema for attendance recording responses."""
    
    attendance_id: str = Field(..., description="Created attendance record ID")


class DocRequestResponse(BaseModel):
    """Schema for document request creation responses."""
    
    request_id: str = Field(..., description="Created document request ID")


class DocSubmitResponse(BaseModel):
    """Schema for document submission responses."""
    
    item_id: str = Field(..., description="Created document item ID")


class DocItemResponse(BaseModel):
    """Schema for document review responses."""
    
    item_id: str = Field(..., description="Document item ID")
    status: DocItemStatus = Field(..., description="Current document status")


class HealthCheckResponse(BaseModel):
    """Schema for health check endpoint response."""
    
    status: str = Field(..., description="Service status")
    timestamp: dt.datetime = Field(..., description="Current server time")
    database_healthy: bool = Field(..., description="Database connectivity status")


# ========= USER SCHEMAS =========

class UserBase(BaseModel):
    email: Optional[str] = None
    is_active: Optional[bool] = True
    name: Optional[str] = None
    role: Optional[UserRole] = None


class UserCreate(UserBase):
    email: str
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


# ========= CRANE SCHEMAS =========

class CraneBase(BaseModel):
    model_name: Optional[str] = None
    serial_no: Optional[str] = None
    status: Optional[CraneStatus] = CraneStatus.NORMAL
    owner_org_id: Optional[str] = None

class CraneCreate(CraneBase):
    model_name: str
    owner_org_id: str

class CraneUpdate(CraneBase):
    pass