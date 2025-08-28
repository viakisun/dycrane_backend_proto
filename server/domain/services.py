import logging
import datetime as dt
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from server.domain.models import User, Site, Crane
from server.domain.repositories import user_repo, site_repo, crane_repo
from server.domain.schemas import UserRole, SiteCreate, SiteStatus, SiteUpdate, CraneCreate, CraneUpdate, OrgType

logger = logging.getLogger(__name__)


class UserService:
    def get_user_and_validate_role(
        self, db: Session, *, user_id: str, expected_role: UserRole
    ) -> User:
        """
        Retrieves a user by ID and validates their role.
        """
        logger.debug(f"Validating user {user_id} for role {expected_role.value}")
        user = user_repo.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User {user_id} is inactive",
            )
        if user.role != expected_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User must have role {expected_role.value}, but has {user.role.value}",
            )
        logger.info(f"User {user_id} validated successfully for role {expected_role.value}")
        return user


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

    def approve_site(
        self, db: Session, *, site_id: str, approved_by_id: str
    ) -> Site:
        """
        Approves a construction site.
        """
        logger.info(f"Approving site {site_id} by user {approved_by_id}")
        # Validate manufacturer
        self.user_service.get_user_and_validate_role(
            db, user_id=approved_by_id, expected_role=UserRole.MANUFACTURER
        )

        site = site_repo.get(db, id=site_id)
        if not site:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Site not found"
            )

        if site.status != SiteStatus.PENDING_APPROVAL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Site status is {site.status}, cannot approve",
            )

        update_data = {
            "status": SiteStatus.ACTIVE,
            "approved_by_id": approved_by_id,
            "approved_at": dt.datetime.utcnow(),
        }
        site = site_repo.update(db, db_obj=site, obj_in=update_data)
        logger.info(f"Site approved successfully: {site.id} - {site.name}")
        return site


class CraneService:
    def list_owner_cranes(self, db: Session, *, owner_org_id: str) -> List[Crane]:
        """
        List all cranes owned by a specific organization.
        """
        logger.info(f"Listing cranes for organization: {owner_org_id}")
        # This is a simplified example. In a real scenario, you would also
        # validate the organization exists and is of the correct type.
        cranes = crane_repo.get_by_owner(db, owner_org_id=owner_org_id)
        logger.info(f"Found {len(cranes)} cranes for organization: {owner_org_id}")
        return cranes

# Instantiate services
user_service = UserService()
site_service = SiteService(user_service=user_service)
crane_service = CraneService()