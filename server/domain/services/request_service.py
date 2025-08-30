import logging
from sqlalchemy.orm import Session
from server.domain.models import Request
from server.domain.schemas import RequestCreate, RequestUpdate, RequestStatus, UserRole
from server.utils.auth import get_user_by_id

logger = logging.getLogger(__name__)


def create_request(db: Session, request_in: RequestCreate) -> Request:
    """Creates a new generic request."""
    # Basic validation
    requester = get_user_by_id(db, request_in.requester_id)
    if not requester:
        raise ValueError("Requester not found")

    logger.info(f"Creating new {request_in.type} request by user {requester.id}")

    new_request = Request(
        type=request_in.type,
        requester_id=request_in.requester_id,
        target_entity_id=request_in.target_entity_id,
        related_entity_id=request_in.related_entity_id,
        notes=request_in.notes,
        status=RequestStatus.PENDING
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    logger.info(f"Successfully created request {new_request.id}")
    return new_request


def respond_to_request(db: Session, request_id: str, response_in: RequestUpdate) -> Request:
    """Approves or rejects a request."""
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise ValueError("Request not found")

    if request.status != RequestStatus.PENDING:
        raise ValueError(f"Request {request_id} is not in PENDING state")

    approver = get_user_by_id(db, response_in.approver_id)
    if not approver or approver.role != UserRole.OWNER:
        # This logic should be more robust, checking against the crane's owner
        raise ValueError("Invalid approver or insufficient permissions")

    logger.info(f"User {approver.id} responding to request {request.id} with status {response_in.status}")

    request.status = response_in.status
    request.approver_id = response_in.approver_id
    request.notes = response_in.notes
    request.responded_at = func.now()

    db.commit()
    db.refresh(request)

    # Here you would typically trigger side effects,
    # e.g., creating a site_crane_assignment if approved.
    # This is omitted for now.

    logger.info(f"Successfully responded to request {request.id}")
    return request
