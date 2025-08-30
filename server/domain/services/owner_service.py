import logging
from typing import List, Optional

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from server.domain.models import Crane, Org, Request, UserOrg
from server.domain.schemas import (
    CraneStatus,
    OrgType,
    OwnerStatsOut,
    RequestStatus,
    RequestType,
)

logger = logging.getLogger(__name__)


class OwnerService:
    def get_owners_with_stats(self, db: Session) -> List[OwnerStatsOut]:
        results = (
            db.query(
                Org.id,
                Org.name,
                func.count(Crane.id).label("total_cranes"),
                func.count(case((Crane.status == CraneStatus.NORMAL, Crane.id))).label(
                    "available_cranes"
                ),
            )
            .outerjoin(Crane, Org.id == Crane.owner_org_id)
            .filter(Org.type == OrgType.OWNER)
            .group_by(Org.id, Org.name)
            .order_by(Org.name)
            .all()
        )
        return [OwnerStatsOut.model_validate(row) for row in results]

    def get_my_requests(
        self,
        db: Session,
        *,
        user_id: str,
        type: Optional[RequestType] = None,
        status: Optional[RequestStatus] = None,
    ) -> List[Request]:
        user_org = db.query(UserOrg).filter(UserOrg.user_id == user_id).first()
        if not user_org:
            return []
        owner_org_id = user_org.org_id
        query = (
            db.query(Request)
            .join(Crane, Request.target_entity_id == Crane.id)
            .filter(Crane.owner_org_id == owner_org_id)
        )
        if type:
            query = query.filter(Request.type == type)
        if status:
            query = query.filter(Request.status == status)
        return query.order_by(Request.requested_at.desc()).all()


owner_service = OwnerService()
