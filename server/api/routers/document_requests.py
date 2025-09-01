import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from server.database import get_db
from server.domain.schemas import DocRequestIn, DocRequestResponse
from server.domain.services import document_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "", response_model=DocRequestResponse, status_code=status.HTTP_201_CREATED
)
def create_document_request_endpoint(payload: DocRequestIn, db: Session = Depends(get_db)):
    """
    Request a document from a driver.
    """
    request = document_service.create_document_request(db=db, request_in=payload)
    return DocRequestResponse(request_id=request.id)
