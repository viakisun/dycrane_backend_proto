import logging
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from server.domain.models import Org, Crane
from server.domain.schemas import OrgType, CraneStatus, OwnerStatsOut

logger = logging.getLogger(__name__)

def get_owners_with_stats(db: Session) -> List[OwnerStatsOut]:
    """
    Retrieves all owner organizations along with statistics about their crane fleet.
    """
    logger.info("Fetching all owner organizations with crane stats")

    # This query calculates the total number of cranes and the number of
    # available (NORMAL status) cranes for each owner organization.
    results = (
        db.query(
            Org.id,
            Org.name,
            func.count(Crane.id).label("total_cranes"),
            func.count(case((Crane.status == CraneStatus.NORMAL, Crane.id))).label("available_cranes"),
        )
        .outerjoin(Crane, Org.id == Crane.owner_org_id)
        .filter(Org.type == OrgType.OWNER)
        .group_by(Org.id, Org.name)
        .order_by(Org.name)
        .all()
    )

    # Convert the raw database result into a list of Pydantic models
    owners_with_stats = [
        OwnerStatsOut(
            id=row.id,
            name=row.name,
            total_cranes=row.total_cranes,
            available_cranes=row.available_cranes,
        )
        for row in results
    ]

from server.domain.models import User, UserOrg, Request
from server.domain.schemas import RequestType, RequestStatus
from typing import Optional

    logger.info(f"Found {len(owners_with_stats)} owner organizations.")
    return owners_with_stats


def get_my_requests(db: Session, *, user_id: str, type: Optional[RequestType] = None, status: Optional[RequestStatus] = None) -> List[Request]:
    """
    Get all requests for cranes owned by the organization of the given user_id.
    """
    logger.info(f"Fetching requests for owner user {user_id}")

    # Find the organization of the user
    user_org = db.query(UserOrg).filter(UserOrg.user_id == user_id).first()
    if not user_org:
        logger.warning(f"User {user_id} is not associated with any organization.")
        return []

    owner_org_id = user_org.org_id

    # Query for requests where the target_entity_id (crane_id) belongs to a crane
    # owned by the user's organization.
    query = (
        db.query(Request)
        .join(Crane, Request.target_entity_id == Crane.id)
        .filter(Crane.owner_org_id == owner_org_id)
    )

    if type:
        query = query.filter(Request.type == type)
    if status:
        query = query.filter(Request.status == status)

    requests = query.order_by(Request.requested_at.desc()).all()

    logger.info(f"Found {len(requests)} requests for owner org {owner_org_id}")
    return requests
