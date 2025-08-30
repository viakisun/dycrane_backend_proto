import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from server.database import get_db
from server.domain.schemas import (
    CraneOut,
    CraneStatus,
    RequestCreate,
    RequestOut,
    RequestType,
)
from server.domain.services import crane_service, request_service

router = APIRouter()
logger = logging.getLogger(__name__)




@router.post(
    "/{crane_id}/deploy-requests",
    response_model=RequestOut,
    status_code=status.HTTP_201_CREATED,
)
def create_deployment_request(
    crane_id: str, payload: RequestCreate, db: Session = Depends(get_db)
):
    """
    Request a crane to be deployed to a site.
    This is typically done by a SAFETY_MANAGER.
    """
    try:
        # Ensure the request type is correct
        if payload.type != RequestType.CRANE_DEPLOY:
            raise ValueError("Invalid request type for this endpoint.")

        # Set the target entity to the crane being requested
        payload.target_entity_id = crane_id

        new_request = request_service.create_request(db=db, request_in=payload)
        return new_request
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create deployment request for crane {crane_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
