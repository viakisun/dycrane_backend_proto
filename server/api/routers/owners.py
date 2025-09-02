import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from server.auth.rbac import require_roles
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


@router.get(
    "/{ownerId}/cranes",
    response_model=List[CraneOut],
    dependencies=[Depends(require_roles(["OWNER"]))],
)
def list_owner_cranes_endpoint(
    ownerId: str,
    status: Optional[CraneStatus] = None,
    model_name: Optional[str] = None,
    min_capacity: Optional[int] = None,
    summary: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """
    List all cranes owned by a specific organization, with optional filters.
    Requires OWNER role.
    If summary=true, returns status counts instead of a list.
    """
    # TODO(strict): DB 조회/페이징/정렬/필터, RBAC 재검증, 에러 규격 적용
    if summary:
        # This is a DEV mode stub as requested
        return JSONResponse(content={"status_counts": {"NORMAL": 0, "REPAIR": 0, "INBOUND": 0}})

    return crane_service.list_owner_cranes(
        db=db,
        owner_org_id=ownerId,
        status=status,
        model_name=model_name,
        min_capacity=min_capacity,
    )


