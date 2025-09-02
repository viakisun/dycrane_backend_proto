import datetime as dt
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .enums import SiteStatus


class SiteCreate(BaseModel):
    """Schema for creating a new construction site."""

    name: str = Field(..., min_length=1, max_length=255, description="Site name")
    address: Optional[str] = Field(None, description="Site address")
    start_date: dt.date = Field(..., description="Project start date")
    end_date: dt.date = Field(..., description="Project end date")
    requested_by_id: str = Field(..., description="SAFETY_MANAGER user ID")

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v, info):
        """Ensure end_date is after start_date."""
        if "start_date" in info.data and v < info.data["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Downtown Construction Site",
                "address": "123 Main Street, Seoul",
                "start_date": "2025-09-01",
                "end_date": "2025-12-31",
                "requested_by_id": "safety-manager-uuid",
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
    approved_by_id: Optional[str] = None
    approved_at: Optional[dt.datetime] = None


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
