import logging
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.database import get_db
from server.domain.schemas import CraneOut
from server.domain.services import crane_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/owners/{owner_org_id}/cranes", response_model=List[CraneOut])
def list_owner_cranes(owner_org_id: str, db: Session = Depends(get_db)):
    """
    List all cranes owned by a specific organization.
    """
    return crane_service.list_owner_cranes(db=db, owner_org_id=owner_org_id)
