import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from server.database import get_db
from server.domain.schemas import AssignDriverIn, DriverAssignmentResponse
from server.domain.services import assignment_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=DriverAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_driver_assignment_endpoint(
    payload: AssignDriverIn, db: Session = Depends(get_db)
):
    """
    Assign a driver to a site-crane combination.
    """
    assignment = assignment_service.assign_driver_to_crane(db=db, assignment_in=payload)
    return DriverAssignmentResponse(driver_assignment_id=assignment.id)
