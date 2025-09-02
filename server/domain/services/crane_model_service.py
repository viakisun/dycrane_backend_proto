import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from server.domain.models import CraneModel
from server.domain.repositories import crane_model_repo

logger = logging.getLogger(__name__)


class CraneModelService:
    def get_models(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[CraneModel]:
        """
        Retrieves a list of crane models.
        """
        logger.info("Fetching list of crane models")
        return crane_model_repo.get_multi(db, skip=skip, limit=limit)

    def get_model(self, db: Session, model_id: str) -> Optional[CraneModel]:
        """
        Retrieves a single crane model by its ID.
        """
        logger.info(f"Fetching crane model with id: {model_id}")
        return crane_model_repo.get(db, id=model_id)


crane_model_service = CraneModelService()
