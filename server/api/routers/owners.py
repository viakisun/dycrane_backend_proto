import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from server.database import get_db
from server.domain.schemas import (
    CraneOut,
    CraneStatus,
    OwnerStatsOut,
    RequestOut,
    RequestStatus,
    RequestType,
)
from server.domain.services import owner_service, crane_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[OwnerStatsOut])
def list_owners_endpoint(include: Optional[str] = None, db: Session = Depends(get_db)):
    """
    List all owners. If 'include=stats' is provided, includes statistics about their crane fleet.
    """
    try:
        return owner_service.get_owners_with_stats(db=db)
    except Exception as e:
        logger.error(f"Failed to get owners with stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/{ownerId}/cranes", response_model=List[CraneOut])
def list_owner_cranes_endpoint(
    ownerId: str,
    status: Optional[CraneStatus] = None,
    model_name: Optional[str] = None,
    min_capacity: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    List all cranes owned by a specific organization, with optional filters.
    """
    return crane_service.list_owner_cranes(
        db=db,
        owner_org_id=ownerId,
        status=status,
        model_name=model_name,
        min_capacity=min_capacity,
    )


