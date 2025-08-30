import datetime as dt
import logging
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from server.domain.models import (
    Crane,
    DriverAssignment,
    DriverAttendance,
    DriverDocumentItem,
    DriverDocumentRequest,
    Org,
    Request,
    Site,
    SiteCraneAssignment,
    User,
    UserOrg,
    CraneModel,
)
from server.domain.repositories import (
    attendance_repo,
    crane_repo,
    crane_model_repo,
    document_item_repo,
    document_request_repo,
    driver_assignment_repo,
    site_crane_assignment_repo,
    site_repo,
    user_repo,
)
from server.domain.schemas import (
    AssignCraneIn,
    AssignDriverIn,
    AttendanceCreate,
    AttendanceIn,
    CraneStatus,
    DocItemReviewIn,
    DocItemStatus,
    DocItemSubmitIn,
    DocRequestIn,
    DocumentItemCreate,
    DocumentItemUpdate,
    DocumentRequestCreate,
    DriverAssignmentCreate,
    OrgType,
    OwnerStatsOut,
    RequestCreate,
    RequestStatus,
    RequestType,
    RequestUpdate,
    SiteCraneAssignmentCreate,
    SiteCreate,
    SiteStatus,
    UserRole,
)

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
        logger.info(
            "User %s validated for role %s", user_id, expected_role.value
        )
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

    def approve_site(self, db: Session, *, site_id: str, approved_by_id: str) -> Site:
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


class CraneService:
    def list_owner_cranes(
        self,
        db: Session,
        *,
        owner_org_id: str,
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


class AssignmentService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def assign_crane_to_site(
        self, db: Session, *, assignment_in: AssignCraneIn
    ) -> SiteCraneAssignment:
        # Simplified for now. A real implementation would have more validation.
        self.user_service.get_user_and_validate_role(
            db,
            user_id=assignment_in.safety_manager_id,
            expected_role=UserRole.SAFETY_MANAGER,
        )
        # In a real implementation, we would also validate the site and
        # crane exist and are available.

        # Add validation for overlapping assignments
        overlapping_assignment = (
            db.query(SiteCraneAssignment)
            .filter(
                SiteCraneAssignment.crane_id == assignment_in.crane_id,
                # The new assignment's start is before or at the same time the existing one ends
                assignment_in.start_date <= (SiteCraneAssignment.end_date or dt.date.max),
                # The new assignment's end is after or at the same time the existing one starts
                (assignment_in.end_date or dt.date.max) >= SiteCraneAssignment.start_date,
            )
            .first()
        )

        if overlapping_assignment:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": f"Crane {assignment_in.crane_id} is already assigned during the requested period.",
                    "assignment_id": overlapping_assignment.id,
                },
            )

        assignment_data = SiteCraneAssignmentCreate(
            site_id=assignment_in.site_id,
            crane_id=assignment_in.crane_id,
            assigned_by=assignment_in.safety_manager_id,
            start_date=assignment_in.start_date,
            end_date=assignment_in.end_date,
        )
        return site_crane_assignment_repo.create(db, obj_in=assignment_data)

    def assign_driver_to_crane(
        self, db: Session, *, assignment_in: AssignDriverIn
    ) -> DriverAssignment:
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

    def create_document_request(
        self, db: Session, *, request_in: DocRequestIn
    ) -> DriverDocumentRequest:
        self.user_service.get_user_and_validate_role(
            db,
            user_id=request_in.requested_by_id,
            expected_role=UserRole.SAFETY_MANAGER,
        )
        self.user_service.get_user_and_validate_role(
            db, user_id=request_in.driver_id, expected_role=UserRole.DRIVER
        )
        # In a real implementation, we would also validate the site exists.

        request_data = DocumentRequestCreate(**request_in.model_dump())
        return document_request_repo.create(db, obj_in=request_data)

    def submit_document_item(
        self, db: Session, *, item_in: DocItemSubmitIn
    ) -> DriverDocumentItem:
        # A real implementation would validate the request exists and that the
        # file_url is a valid, accessible URL.
        # For now, we are skipping the validation.
        item_data = DocumentItemCreate(**item_in.model_dump())
        return document_item_repo.create(db, obj_in=item_data)

    def review_document_item(
        self, db: Session, *, review_in: DocItemReviewIn
    ) -> DriverDocumentItem:
        self.user_service.get_user_and_validate_role(
            db, user_id=review_in.reviewer_id, expected_role=UserRole.SAFETY_MANAGER
        )
        item = document_item_repo.get(db, id=review_in.item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Document item not found")

        update_data = DocumentItemUpdate(
            status=DocItemStatus.APPROVED
            if review_in.approve
            else DocItemStatus.REJECTED,
            reviewer_id=review_in.reviewer_id,
            reviewed_at=dt.datetime.utcnow(),
        )
        return document_item_repo.update(db, db_obj=item, obj_in=update_data)


class AttendanceService:
    def record_attendance(
        self, db: Session, *, attendance_in: AttendanceIn
    ) -> DriverAttendance:
        # Simplified for now. A real implementation would have more validation.
        attendance_data = AttendanceCreate(**attendance_in.model_dump())
        return attendance_repo.create(db, obj_in=attendance_data)


class RequestService:
    def create_request(self, db: Session, request_in: RequestCreate) -> Request:
        requester = user_repo.get(db, id=request_in.requester_id)
        if not requester:
            raise ValueError("Requester not found")
        new_request = Request(**request_in.model_dump(), status=RequestStatus.PENDING)
        db.add(new_request)
        db.commit()
        db.refresh(new_request)
        return new_request

    def respond_to_request(
        self, db: Session, request_id: str, response_in: RequestUpdate
    ) -> Request:
        request = db.query(Request).filter(Request.id == request_id).first()
        if not request:
            raise ValueError("Request not found")
        if request.status != RequestStatus.PENDING:
            raise ValueError(f"Request {request_id} is not in PENDING state")
        approver = user_repo.get(db, id=response_in.approver_id)
        if not approver or approver.role != UserRole.OWNER:
            raise ValueError("Invalid approver or insufficient permissions")

        request.status = response_in.status
        request.approver_id = response_in.approver_id
        request.notes = response_in.notes
        request.responded_at = func.now()
        db.commit()
        db.refresh(request)
        return request


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


class CraneModelService:
    def get_models(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[CraneModel]:
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

# Instantiate services
user_service = UserService()
site_service = SiteService(user_service=user_service)
crane_service = CraneService()
assignment_service = AssignmentService(user_service=user_service)
document_service = DocumentService(user_service=user_service)
attendance_service = AttendanceService()
request_service = RequestService()
owner_service = OwnerService()
crane_model_service = CraneModelService()
