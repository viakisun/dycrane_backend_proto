import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from server.database import get_db
from server.domain.schemas import SiteCreate, SiteOut, SiteUpdate
from server.domain.services import site_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=SiteOut, status_code=status.HTTP_201_CREATED)
def create_site_endpoint(payload: SiteCreate, db: Session = Depends(get_db)):
    """
    Create a new construction site.
    """
    return site_service.create_site(db=db, site_in=payload)


@router.get("", response_model=List[SiteOut])
def list_sites_endpoint(
    db: Session = Depends(get_db),
    mine: Optional[bool] = None,
    user_id: Optional[str] = None,
):
    """
    List all construction sites.
    If 'mine' is true, returns only sites relevant to the user_id.
    NOTE: In a real app, user_id would come from an auth dependency.
    """
    return site_service.list_sites(db=db, mine=mine, user_id=user_id)


@router.patch("/{site_id}", response_model=SiteOut)
def update_site_endpoint(site_id: str, payload: SiteUpdate, db: Session = Depends(get_db)):
    """
    Update a site's attributes, including approving it.
    """
    return site_service.update_site(db=db, site_id=site_id, site_in=payload)
