import datetime as dt
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class AttendanceIn(BaseModel):
    """Schema for recording driver attendance."""

    driver_assignment_id: str = Field(..., description="Driver assignment ID")
    work_date: dt.date = Field(..., description="Work date")
    check_in_at: dt.datetime = Field(..., description="Check-in timestamp")
    check_out_at: Optional[dt.datetime] = Field(None, description="Check-out timestamp")

    @field_validator("check_out_at")
    @classmethod
    def validate_time_range(cls, v, info):
        """Ensure check_out_at is after check_in_at if provided."""
        if (
            v is not None
            and "check_in_at" in info.data
            and v < info.data["check_in_at"]
        ):
            raise ValueError("check_out_at must be after check_in_at")
        return v


class AttendanceResponse(BaseModel):
    """Schema for attendance recording responses."""

    attendance_id: str = Field(..., description="Created attendance record ID")


class AttendanceCreate(BaseModel):
    driver_assignment_id: str
    work_date: dt.date
    check_in_at: dt.datetime
    check_out_at: Optional[dt.datetime] = None


class AttendanceUpdate(BaseModel):
    check_out_at: Optional[dt.datetime] = None
