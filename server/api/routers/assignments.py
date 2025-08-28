import logging
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from server.database import get_db
from server.domain.schemas import (
    AssignCraneIn,
    AssignDriverIn,
    AssignmentResponse,
    DriverAssignmentResponse,
    AttendanceIn,
    AttendanceResponse,
)
from server.domain.services import StoredProcedureService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/crane", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
def assign_crane(payload: AssignCraneIn, db: Session = Depends(get_db)):
    logger.info(f"Assigning crane {payload.crane_id} to site {payload.site_id}")

    assignment_id = StoredProcedureService.execute_returning_id(
        db,
        "ops.sp_assign_crane",
        {
            "p_site_id": payload.site_id,
            "p_crane_id": payload.crane_id,
            "p_safety_manager_id": payload.safety_manager_id,
            "p_start_date": payload.start_date,
            "p_end_date": payload.end_date
        }
    )

    db.commit()
    logger.info(f"Crane assignment created: {assignment_id}")
    return AssignmentResponse(assignment_id=assignment_id)


@router.post("/driver", response_model=DriverAssignmentResponse, status_code=status.HTTP_201_CREATED)
def assign_driver(payload: AssignDriverIn, db: Session = Depends(get_db)):
    logger.info(f"Assigning driver {payload.driver_id} to site-crane {payload.site_crane_id}")

    assignment_id = StoredProcedureService.execute_returning_id(
        db,
        "ops.sp_assign_driver",
        {
            "p_site_crane_id": payload.site_crane_id,
            "p_driver_id": payload.driver_id,
            "p_start_date": payload.start_date,
            "p_end_date": payload.end_date
        }
    )

    db.commit()
    logger.info(f"Driver assignment created: {assignment_id}")
    return DriverAssignmentResponse(driver_assignment_id=assignment_id)


@router.post("/attendance", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
def record_attendance(payload: AttendanceIn, db: Session = Depends(get_db)):
    logger.info(f"Recording attendance for assignment {payload.driver_assignment_id} on {payload.work_date}")

    attendance_id = StoredProcedureService.execute_returning_id(
        db,
        "ops.sp_record_attendance",
        {
            "p_driver_assignment_id": payload.driver_assignment_id,
            "p_work_date": payload.work_date,
            "p_check_in_at": payload.check_in_at,
            "p_check_out_at": payload.check_out_at
        }
    )

    db.commit()
    logger.info(f"Attendance recorded: {attendance_id}")
    return AttendanceResponse(attendance_id=attendance_id)
