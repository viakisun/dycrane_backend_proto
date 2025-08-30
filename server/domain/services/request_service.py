import logging

from sqlalchemy import func
from sqlalchemy.orm import Session

from server.domain.models import Request
from server.domain.repositories import user_repo
from server.domain.schemas import (
    RequestCreate,
    RequestStatus,
    RequestUpdate,
    UserRole,
)

logger = logging.getLogger(__name__)


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


request_service = RequestService()
