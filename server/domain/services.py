import logging
import datetime as dt
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from server.domain.models import User, Site, Crane, SiteCraneAssignment, DriverAssignment, DriverDocumentRequest, DriverDocumentItem, DriverAttendance
from server.domain.repositories import user_repo, site_repo, crane_repo, site_crane_assignment_repo, driver_assignment_repo, document_request_repo, document_item_repo, attendance_repo
from server.domain.schemas import UserRole, SiteCreate, SiteStatus, SiteUpdate, CraneCreate, CraneUpdate, OrgType, SiteCraneAssignmentCreate, DriverAssignmentCreate, DocumentRequestCreate, DocumentItemCreate, DocItemStatus, DocumentItemUpdate, AttendanceCreate

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

    def list_sites(self, db: Session, *, mine: Optional[bool], user_id: Optional[str]) -> List[Site]:
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


from server.domain.schemas import UserRole, SiteCreate, SiteStatus, SiteUpdate, CraneCreate, CraneUpdate, OrgType, SiteCraneAssignmentCreate, DriverAssignmentCreate, DocumentRequestCreate, DocumentItemCreate, DocItemStatus, DocumentItemUpdate, AttendanceCreate, CraneStatus

class CraneService:
    def list_owner_cranes(self, db: Session, *, owner_org_id: str, status: Optional[CraneStatus] = None) -> List[Crane]:
        """
        List all cranes owned by a specific organization, with optional status filtering.
        """
        logger.info(f"Listing cranes for organization: {owner_org_id} with status filter: {status}")
        # This is a simplified example. In a real scenario, you would also
        # validate the organization exists and is of the correct type.
        cranes = crane_repo.get_by_owner(db, owner_org_id=owner_org_id, status=status)
        logger.info(f"Found {len(cranes)} cranes for organization: {owner_org_id}")
        return cranes

class AssignmentService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def assign_crane_to_site(self, db: Session, *, assignment_in: "AssignCraneIn") -> SiteCraneAssignment:
        # Simplified for now. A real implementation would have more validation.
        self.user_service.get_user_and_validate_role(
            db, user_id=assignment_in.safety_manager_id, expected_role=UserRole.SAFETY_MANAGER
        )
        # In a real implementation, we would also validate the site and crane exist and are available.

        assignment_data = SiteCraneAssignmentCreate(
            site_id=assignment_in.site_id,
            crane_id=assignment_in.crane_id,
            assigned_by=assignment_in.safety_manager_id,
            start_date=assignment_in.start_date,
            end_date=assignment_in.end_date,
        )
        return site_crane_assignment_repo.create(db, obj_in=assignment_data)

    def assign_driver_to_crane(self, db: Session, *, assignment_in: "AssignDriverIn") -> DriverAssignment:
        self.user_service.get_user_and_validate_role(
            db, user_id=assignment_in.driver_id, expected_role=UserRole.DRIVER
        )
        # Further validation would be needed here.
        assignment_data = DriverAssignmentCreate(
            site_crane_id=assignment_in.site_crane_id,
            driver_id=assignment_in.driver_id,
            start_date=assignment_in.start_date,
            end_date=assignment_in.end_date,
        )
        return driver_assignment_repo.create(db, obj_in=assignment_data)

class DocumentService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def create_document_request(self, db: Session, *, request_in: "DocRequestIn") -> DriverDocumentRequest:
        self.user_service.get_user_and_validate_role(
            db, user_id=request_in.requested_by_id, expected_role=UserRole.SAFETY_MANAGER
        )
        self.user_service.get_user_and_validate_role(
            db, user_id=request_in.driver_id, expected_role=UserRole.DRIVER
        )
        # In a real implementation, we would also validate the site exists.

        request_data = DocumentRequestCreate(**request_in.model_dump())
        return document_request_repo.create(db, obj_in=request_data)

    def submit_document_item(self, db: Session, *, item_in: "DocItemSubmitIn") -> DriverDocumentItem:
        # A real implementation would validate the request exists.
        ValidationService.validate_file_url(str(item_in.file_url))

        item_data = DocumentItemCreate(**item_in.model_dump())
        return document_item_repo.create(db, obj_in=item_data)

    def review_document_item(self, db: Session, *, review_in: "DocItemReviewIn") -> DriverDocumentItem:
        self.user_service.get_user_and_validate_role(
            db, user_id=review_in.reviewer_id, expected_role=UserRole.SAFETY_MANAGER
        )
        item = document_item_repo.get(db, id=review_in.item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Document item not found")

        update_data = DocumentItemUpdate(
            status=DocItemStatus.APPROVED if review_in.approve else DocItemStatus.REJECTED,
            reviewer_id=review_in.reviewer_id,
            reviewed_at=dt.datetime.utcnow(),
        )
        return document_item_repo.update(db, db_obj=item, obj_in=update_data)


class AttendanceService:
    def record_attendance(self, db: Session, *, attendance_in: "AttendanceIn") -> DriverAttendance:
        # Simplified for now. A real implementation would have more validation.
        attendance_data = AttendanceCreate(**attendance_in.model_dump())
        return attendance_repo.create(db, obj_in=attendance_data)

# Instantiate services
user_service = UserService()
site_service = SiteService(user_service=user_service)
crane_service = CraneService()
assignment_service = AssignmentService(user_service=user_service)
document_service = DocumentService(user_service=user_service)
attendance_service = AttendanceService()
