import datetime as dt
import logging

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from server.domain.models import DriverAssignment, SiteCraneAssignment
from server.domain.repositories import (
    driver_assignment_repo,
    site_crane_assignment_repo,
)
from server.domain.schemas import (
    AssignCraneIn,
    AssignDriverIn,
    DriverAssignmentCreate,
    SiteCraneAssignmentCreate,
    UserRole,
)

from .user_service import UserService, user_service

logger = logging.getLogger(__name__)


class AssignmentService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def assign_crane_to_site(
        self, db: Session, *, assignment_in: AssignCraneIn
    ) -> SiteCraneAssignment:
        self.user_service.get_user_and_validate_role(
            db,
            user_id=assignment_in.safety_manager_id,
            expected_role=UserRole.SAFETY_MANAGER,
        )

        overlapping_assignment = (
            db.query(SiteCraneAssignment)
            .filter(
                SiteCraneAssignment.crane_id == assignment_in.crane_id,
                assignment_in.start_date
                <= func.coalesce(SiteCraneAssignment.end_date, dt.date.max),
                (assignment_in.end_date or dt.date.max)
                >= SiteCraneAssignment.start_date,
            )
            .first()
        )

        if overlapping_assignment:
            message = (
                f"Crane {assignment_in.crane_id} is already assigned "
                "during the requested period."
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": message,
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

        assignment_data = DriverAssignmentCreate(
            site_crane_id=assignment_in.site_crane_id,
            driver_id=assignment_in.driver_id,
            start_date=assignment_in.start_date,
            end_date=assignment_in.end_date,
        )
        return driver_assignment_repo.create(db, obj_in=assignment_data)


assignment_service = AssignmentService(user_service=user_service)
