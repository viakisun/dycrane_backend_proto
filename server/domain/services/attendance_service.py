import logging

from sqlalchemy.orm import Session

from server.domain.models import DriverAttendance
from server.domain.repositories import attendance_repo
from server.domain.schemas import AttendanceCreate, AttendanceIn

logger = logging.getLogger(__name__)


class AttendanceService:
    def record_attendance(
        self, db: Session, *, attendance_in: AttendanceIn
    ) -> DriverAttendance:
        # Simplified for now. A real implementation would have more validation.
        attendance_data = AttendanceCreate(**attendance_in.model_dump())
        return attendance_repo.create(db, obj_in=attendance_data)


attendance_service = AttendanceService()
