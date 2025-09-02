import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from server.database import get_db
from server.domain.schemas import AssignCraneIn, AssignmentResponse
from server.domain.services import assignment_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
def create_crane_assignment_endpoint(
    payload: AssignCraneIn, db: Session = Depends(get_db)
):
    """
    Create a new crane assignment to a site.
    """
    assignment = assignment_service.assign_crane_to_site(db=db, assignment_in=payload)
    return AssignmentResponse(assignment_id=assignment.id)
