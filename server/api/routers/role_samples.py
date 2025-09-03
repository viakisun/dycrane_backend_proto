from fastapi import APIRouter, Depends, Path, Query

from server.auth.rbac import require_roles

# This router is for demonstrating the RBAC decorator.
# The business logic is entirely placeholder.
router = APIRouter(tags=["_samples"])


@router.get(
    "/drivers/{driver_id}/active-assignments-sample",
    dependencies=[Depends(require_roles("DRIVER"))],
)
async def list_driver_active_assignments_sample(
    driver_id: str = Path(..., description="The ID of the driver"),
    date: str = Query("today", description="The target date for assignments"),
):
    """
    (Sample) Get active assignments for a specific driver. Requires DRIVER role.
    TODO(strict): DB 조회/페이징/정렬/필터, RBAC 재검증, 에러 규격 적용
    """
    return {"items": [], "total": 0}


@router.get(
    "/owners/{owner_id}/cranes-summary-sample", dependencies=[Depends(require_roles("OWNER"))]
)
async def list_owner_cranes_summary_sample(
    owner_id: str = Path(..., description="The ID of the owner"),
    summary: bool = Query(True, description="Flag to return summary data"),
):
    """
    (Sample) Get a summary of cranes for a specific owner. Requires OWNER role.
    TODO(strict): DB 조회/페이징/정렬/필터, RBAC 재검증, 에러 규격 적용
    """
    return {"status_counts": {"NORMAL": 0, "REPAIR": 0, "INBOUND": 0}}


@router.get("/sites-sample", dependencies=[Depends(require_roles("SAFETY_MANAGER"))])
async def list_managed_sites_sample(
    requested_by: str = Query("me", description="Filter by requester"),
    status: str = Query("ACTIVE", description="Filter by site status"),
):
    """
    (Sample) Get a list of sites relevant to the safety manager. Requires SAFETY_MANAGER role.
    TODO(strict): DB 조회/페이징/정렬/필터, RBAC 재검증, 에러 규격 적용
    """
    return []
