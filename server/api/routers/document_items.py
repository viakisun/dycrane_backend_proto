import logging

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from server.database import get_db
from server.domain.schemas import (
    DocItemResponse,
    DocItemReviewIn,
    DocItemSubmitIn,
    DocSubmitResponse,
)
from server.domain.services import document_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=DocSubmitResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_document_item_endpoint(payload: DocItemSubmitIn, db: Session = Depends(get_db)):
    """
    Submit a new document item.
    """
    item = document_service.submit_document_item(db=db, item_in=payload)
    return DocSubmitResponse(item_id=item.id)


@router.post("/{item_id}/review", response_model=DocItemResponse)
def review_document_item_endpoint(
    item_id: str, payload: DocItemReviewIn, db: Session = Depends(get_db)
):
    """
    Review (approve or reject) a document item.
    """
    # Ensure the item ID from the path matches the one in the payload
    if item_id != payload.item_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item ID in path does not match item ID in payload.",
        )

    item = document_service.review_document_item(db=db, review_in=payload)
    return DocItemResponse(item_id=item.id, status=item.status)
