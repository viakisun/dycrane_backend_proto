import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from server.domain.models import Crane
from server.domain.repositories import crane_repo
from server.domain.schemas import CraneStatus

logger = logging.getLogger(__name__)


class CraneService:
    def list_owner_cranes(
        self,
        db: Session,
        *,
        owner_org_id: Optional[str] = None,
        status: Optional[CraneStatus] = None,
        model_name: Optional[str] = None,
        min_capacity: Optional[int] = None,
    ) -> List[Crane]:
        """
        List all cranes owned by a specific organization, with optional filters.
        """
        logger.info(f"Listing cranes for org: {owner_org_id} with filters")
        cranes = crane_repo.get_by_owner(
            db,
            owner_org_id=owner_org_id,
            status=status,
            model_name=model_name,
            min_capacity=min_capacity,
        )
        logger.info(f"Found {len(cranes)} cranes for organization: {owner_org_id}")
        return cranes


crane_service = CraneService()
