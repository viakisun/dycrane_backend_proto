import logging
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from server.database import get_db
from server.domain.schemas import (
    DocRequestIn,
    DocItemSubmitIn,
    DocItemReviewIn,
    DocRequestResponse,
    DocSubmitResponse,
    DocItemResponse,
)
from server.domain.services import StoredProcedureService, ValidationService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/requests", response_model=DocRequestResponse, status_code=status.HTTP_201_CREATED)
def create_document_request(payload: DocRequestIn, db: Session = Depends(get_db)):
    logger.info(f"Creating document request for driver {payload.driver_id} on site {payload.site_id}")

    request_id = StoredProcedureService.execute_returning_id(
        db,
        "ops.sp_doc_request_create",
        {
            "p_site_id": payload.site_id,
            "p_driver_id": payload.driver_id,
            "p_requested_by_id": payload.requested_by_id,
            "p_due_date": payload.due_date
        }
    )

    db.commit()
    logger.info(f"Document request created: {request_id}")
    return DocRequestResponse(request_id=request_id)


@router.post("/items/submit", response_model=DocSubmitResponse, status_code=status.HTTP_201_CREATED)
def submit_document_item(payload: DocItemSubmitIn, db: Session = Depends(get_db)):
    logger.info(f"Submitting document for request {payload.request_id}: {payload.doc_type}")

    # Application-layer file URL validation
    ValidationService.validate_file_url(str(payload.file_url))

    item_id = StoredProcedureService.execute_returning_id(
        db,
        "ops.sp_doc_item_submit",
        {
            "p_request_id": payload.request_id,
            "p_doc_type": payload.doc_type,
            "p_file_url": str(payload.file_url)
        }
    )

    db.commit()
    logger.info(f"Document item submitted: {item_id}")
    return DocSubmitResponse(item_id=item_id)


@router.post("/items/review", response_model=DocItemResponse)
def review_document_item(payload: DocItemReviewIn, db: Session = Depends(get_db)):
    action = "approving" if payload.approve else "rejecting"
    logger.info(f"Reviewing document item {payload.item_id}: {action}")

    status_value = StoredProcedureService.execute_returning_status(
        db,
        "ops.sp_doc_item_review",
        {
            "p_item_id": payload.item_id,
            "p_reviewer_id": payload.reviewer_id,
            "p_approve": payload.approve
        }
    )

    db.commit()
    logger.info(f"Document review completed: {payload.item_id} -> {status_value}")
    return DocItemResponse(item_id=payload.item_id, status=status_value)
