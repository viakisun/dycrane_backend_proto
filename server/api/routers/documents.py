import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from server.database import get_db
from server.domain.schemas import (
    DocItemResponse,
    DocItemReviewIn,
    DocItemSubmitIn,
    DocRequestIn,
    DocRequestResponse,
    DocSubmitResponse,
)
from server.domain.services import document_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/requests", response_model=DocRequestResponse, status_code=status.HTTP_201_CREATED
)
def create_document_request(payload: DocRequestIn, db: Session = Depends(get_db)):
    request = document_service.create_document_request(db=db, request_in=payload)
    return DocRequestResponse(request_id=request.id)


@router.post(
    "/items/submit",
    response_model=DocSubmitResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_document_item(payload: DocItemSubmitIn, db: Session = Depends(get_db)):
    item = document_service.submit_document_item(db=db, item_in=payload)
    return DocSubmitResponse(item_id=item.id)


@router.post("/items/review", response_model=DocItemResponse)
def review_document_item(payload: DocItemReviewIn, db: Session = Depends(get_db)):
    item = document_service.review_document_item(db=db, review_in=payload)
    return DocItemResponse(item_id=item.id, status=item.status)
