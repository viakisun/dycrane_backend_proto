import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from server.database import get_db
from server.domain.schemas import (
    AssignCraneIn,
    AssignDriverIn,
    AssignmentResponse,
    AttendanceIn,
    AttendanceResponse,
    DriverAssignmentResponse,
)
from server.domain.services import assignment_service, attendance_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/crane", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED
)
def assign_crane(payload: AssignCraneIn, db: Session = Depends(get_db)):
    assignment = assignment_service.assign_crane_to_site(db=db, assignment_in=payload)
    return AssignmentResponse(assignment_id=assignment.id)


@router.post(
    "/driver",
    response_model=DriverAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def assign_driver(payload: AssignDriverIn, db: Session = Depends(get_db)):
    assignment = assignment_service.assign_driver_to_crane(db=db, assignment_in=payload)
    return DriverAssignmentResponse(driver_assignment_id=assignment.id)


@router.post(
    "/attendance",
    response_model=AttendanceResponse,
    status_code=status.HTTP_201_CREATED,
)
def record_attendance(payload: AttendanceIn, db: Session = Depends(get_db)):
    attendance = attendance_service.record_attendance(db=db, attendance_in=payload)
    return AttendanceResponse(attendance_id=attendance.id)
