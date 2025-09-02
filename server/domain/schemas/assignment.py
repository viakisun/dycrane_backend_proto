import datetime as dt
from typing import Optional

from pydantic import BaseModel, Field, field_validator
from .enums import AssignmentStatus


class AssignCraneIn(BaseModel):
    """Schema for assigning a crane to a site."""

    site_id: str = Field(..., description="Target site ID")
    crane_id: str = Field(..., description="Crane to assign")
    safety_manager_id: str = Field(..., description="SAFETY_MANAGER user ID")
    start_date: dt.date = Field(..., description="Assignment start date")
    end_date: Optional[dt.date] = Field(None, description="Assignment end date")

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v, info):
        """Ensure end_date is after start_date if provided."""
        if v is not None and "start_date" in info.data and v < info.data["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v


class AssignDriverIn(BaseModel):
    """Schema for assigning a driver to a site-crane combination."""

    site_crane_id: str = Field(..., description="Site-crane assignment ID")
    driver_id: str = Field(..., description="DRIVER user ID")
    start_date: dt.date = Field(..., description="Driver assignment start date")
    end_date: Optional[dt.date] = Field(None, description="Driver assignment end date")

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v, info):
        """Ensure end_date is after start_date if provided."""
        if v is not None and "start_date" in info.data and v < info.data["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v


class AssignmentResponse(BaseModel):
    """Schema for crane assignment operation responses."""

    assignment_id: str = Field(..., description="Created assignment ID")


class DriverAssignmentResponse(BaseModel):
    """Schema for driver assignment operation responses."""

    driver_assignment_id: str = Field(..., description="Created driver assignment ID")


class SiteCraneAssignmentCreate(BaseModel):
    site_id: str
    crane_id: str
    assigned_by: str
    start_date: dt.date
    end_date: Optional[dt.date] = None


class SiteCraneAssignmentUpdate(BaseModel):
    status: Optional[AssignmentStatus] = None


class DriverAssignmentCreate(BaseModel):
    site_crane_id: str
    driver_id: str
    start_date: dt.date
    end_date: Optional[dt.date] = None


class DriverAssignmentUpdate(BaseModel):
    status: Optional[AssignmentStatus] = None
