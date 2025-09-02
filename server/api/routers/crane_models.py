import logging
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.database import get_db
from server.domain.schemas import CraneModelOut
from server.domain.services import crane_model_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("", response_model=List[CraneModelOut])
def list_crane_models_endpoint(db: Session = Depends(get_db)):
    """
    List all crane models.
    """
    return crane_model_service.get_models(db=db)
