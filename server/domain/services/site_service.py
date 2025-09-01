import datetime as dt
import logging
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from server.domain.models import Site
from server.domain.repositories import site_repo
from server.domain.schemas import SiteCreate, SiteUpdate, SiteStatus, UserRole
from .user_service import UserService, user_service

logger = logging.getLogger(__name__)


class SiteService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def create_site(self, db: Session, *, site_in: SiteCreate) -> Site:
        """
        Creates a new construction site.
        """
        logger.info(f"Creating site: {site_in.name}")
        # Validate safety manager
        self.user_service.get_user_and_validate_role(
            db,
            user_id=site_in.requested_by_id,
            expected_role=UserRole.SAFETY_MANAGER,
        )

        if site_in.end_date < site_in.start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="end_date must be after start_date",
            )

        site = site_repo.create(db, obj_in=site_in)
        logger.info(f"Site created successfully: {site.id} - {site.name}")
        return site

    def update_site(self, db: Session, *, site_id: str, site_in: SiteUpdate) -> Site:
        """
        Updates a construction site.
        """
        logger.info(f"Updating site {site_id}")
        site = site_repo.get(db, id=site_id)
        if not site:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Site not found"
            )

        update_data = site_in.model_dump(exclude_unset=True)

        # If the status is being changed to ACTIVE, it's an approval action
        if "status" in update_data and update_data["status"] == SiteStatus.ACTIVE:
            if site.status != SiteStatus.PENDING_APPROVAL:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Site status is {site.status}, cannot approve",
                )
            if not site_in.approved_by_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="approved_by_id is required to approve a site",
                )
            # Validate the user approving is a manufacturer
            self.user_service.get_user_and_validate_role(
                db, user_id=site_in.approved_by_id, expected_role=UserRole.MANUFACTURER
            )
            update_data["approved_at"] = dt.datetime.utcnow()

        updated_site = site_repo.update(db, db_obj=site, obj_in=update_data)
        logger.info(f"Site updated successfully: {site.id} - {site.name}")
        return updated_site

    def list_sites(
        self, db: Session, *, mine: Optional[bool], user_id: Optional[str]
    ) -> List[Site]:
        """
        Lists construction sites. If 'mine' is True, filters for sites
        relevant to the given user_id.
        """
        if mine and not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id is required when 'mine' is true",
            )

        logger.info(f"Listing sites with mine={mine} for user_id={user_id}")
        return site_repo.get_multi_for_user(db, user_id=user_id if mine else None)


site_service = SiteService(user_service=user_service)
