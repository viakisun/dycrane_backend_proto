import logging
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.database import get_db
from server.domain.schemas import (
    CraneOut,
    CraneStatus,
)
from server.domain.services import crane_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("", response_model=List[CraneOut])
def list_cranes_endpoint(
    db: Session = Depends(get_db),
    owner_org_id: Optional[str] = None,
    status: Optional[CraneStatus] = None,
    model_name: Optional[str] = None,
    min_capacity: Optional[int] = None,
):
    """
    List all cranes with optional filtering.
    """
    return crane_service.list_owner_cranes(
        db=db,
        owner_org_id=owner_org_id,
        status=status,
        model_name=model_name,
        min_capacity=min_capacity,
    )
