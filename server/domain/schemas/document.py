import datetime as dt
from typing import Optional

from pydantic import AnyHttpUrl, BaseModel, Field

from .enums import DocItemStatus


class DocRequestIn(BaseModel):
    """Schema for creating a document request."""

    site_id: str = Field(..., description="Site ID")
    driver_id: str = Field(..., description="Driver user ID")
    requested_by_id: str = Field(..., description="SAFETY_MANAGER user ID")
    due_date: Optional[dt.date] = Field(
        None, description="Document submission due date"
    )


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


class DocumentRequestCreate(BaseModel):
    site_id: str
    driver_id: str
    requested_by_id: str
    due_date: Optional[dt.date] = None


class DocumentRequestUpdate(BaseModel):
    pass


class DocumentItemCreate(BaseModel):
    request_id: str
    doc_type: str
    file_url: str  # Must be a plain string for the DB layer


class DocumentItemUpdate(BaseModel):
    status: Optional[DocItemStatus] = None
    reviewer_id: Optional[str] = None
    reviewed_at: Optional[dt.datetime] = None
