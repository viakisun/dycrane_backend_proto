import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from server.auth.context import get_current_user
from server.auth.rbac import require_roles
from server.auth.schemas import CurrentUserSchema
from server.database import get_db
from server.domain.schemas import SiteCreate, SiteOut, SiteUpdate, SiteStatus
from server.domain.services import site_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=SiteOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(["SAFETY_MANAGER"]))],
)
def create_site_endpoint(
    payload: SiteCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    """
    Create a new construction site.
    Requires SAFETY_MANAGER role.
    """
    # TODO: Validate that payload.requested_by_id matches current_user.id
    return site_service.create_site(db=db, site_in=payload)


@router.get(
    "",
    response_model=List[SiteOut],
    dependencies=[Depends(require_roles(["SAFETY_MANAGER", "DRIVER"]))],
)
def list_sites_endpoint(
    db: Session = Depends(get_db),
    current_user: CurrentUserSchema = Depends(get_current_user),
    requested_by: Optional[str] = None,
    status: Optional[SiteStatus] = None,
):
    """
    List all construction sites.
    - If 'requested_by=me' is used, it returns sites requested by the current user.
    - This endpoint is available to SAFETY_MANAGER and DRIVER roles.
    """
    # TODO(strict): DB 조회/페이징/정렬/필터, RBAC 재검증, 에러 규격 적용
    user_id_filter = current_user.id if requested_by == "me" else None
    if requested_by and requested_by != 'me':
        logger.warning(f"Unsupported value for requested_by: {requested_by}")

    # For now, we pass the user_id to the service layer.
    # The service layer will need to be updated to handle this.
    # In DEV mode, we just return an empty list as per instructions.
    return []


@router.patch("/{site_id}", response_model=SiteOut)
def update_site_endpoint(site_id: str, payload: SiteUpdate, db: Session = Depends(get_db)):
    """
    Update a site's attributes, including approving it.
    """
    return site_service.update_site(db=db, site_id=site_id, site_in=payload)
