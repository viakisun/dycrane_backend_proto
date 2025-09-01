import datetime as dt
from typing import Optional

from pydantic import BaseModel, ConfigDict
from .enums import RequestType, RequestStatus


class RequestCreate(BaseModel):
    """Schema for creating a generic request."""

    type: RequestType
    requester_id: str
    target_entity_id: str
    related_entity_id: Optional[str] = None
    notes: Optional[str] = None


class RequestUpdate(BaseModel):
    """Schema for approving or rejecting a request."""

    status: RequestStatus
    approver_id: str
    notes: Optional[str] = None


class RequestOut(BaseModel):
    """Schema for request information in API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    type: RequestType
    status: RequestStatus
    requester_id: str
    approver_id: Optional[str] = None
    target_entity_id: Optional[str] = None
    related_entity_id: Optional[str] = None
    notes: Optional[str] = None
    requested_at: dt.datetime
    responded_at: Optional[dt.datetime] = None
