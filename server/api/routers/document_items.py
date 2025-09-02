import logging

from fastapi import APIRouter, Depends, status
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


@router.patch("/{item_id}", response_model=DocItemResponse)
def review_document_item_endpoint(
    item_id: str, payload: DocItemReviewIn, db: Session = Depends(get_db)
):
    """
    Review (approve or reject) a document item.
    """
    # The payload for review_in should not contain the item_id from the payload, but from the path.
    # The DocItemReviewIn schema does not have item_id, so we add it for the service.
    review_with_id = payload.dict()
    review_with_id['item_id'] = itemId
    item = document_service.review_document_item(db=db, review_in=review_with_id)
    return DocItemResponse(item_id=item.id, status=item.status)
