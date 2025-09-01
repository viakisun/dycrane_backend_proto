import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from server.database import get_db
from server.domain.schemas import AttendanceIn, AttendanceResponse
from server.domain.services import attendance_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "",
    response_model=AttendanceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_attendance_endpoint(payload: AttendanceIn, db: Session = Depends(get_db)):
    """
    Record a new attendance entry for a driver.
    """
    attendance = attendance_service.record_attendance(db=db, attendance_in=payload)
    return AttendanceResponse(attendance_id=attendance.id)
