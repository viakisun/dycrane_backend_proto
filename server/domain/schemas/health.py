import datetime as dt
from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    """Schema for health check endpoint response."""

    status: str = Field(..., description="Service status")
    timestamp: dt.datetime = Field(..., description="Current server time")
    database_healthy: bool = Field(..., description="Database connectivity status")
