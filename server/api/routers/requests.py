import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from server.database import get_db
from server.domain.schemas import RequestCreate, RequestOut, RequestUpdate, RequestType
from server.domain.services import request_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=RequestOut, status_code=status.HTTP_201_CREATED)
def create_request_endpoint(payload: RequestCreate, db: Session = Depends(get_db)):
    """
    Create a new request, e.g. for crane deployment.
    """
    try:
        new_request = request_service.create_request(db=db, request_in=payload)
        return new_request
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/{request_id}/respond", response_model=RequestOut)
def respond_to_request_endpoint(
    request_id: str, payload: RequestUpdate, db: Session = Depends(get_db)
):
    """
    Approve or reject a deployment request.
    This is typically done by an OWNER.
    """
    try:
        updated_request = request_service.respond_to_request(
            db=db, request_id=request_id, response_in=payload
        )
        return updated_request
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to respond to request {request_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
