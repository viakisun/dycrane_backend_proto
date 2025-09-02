import datetime as dt
import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session

from server.domain.models import DriverDocumentItem, DriverDocumentRequest
from server.domain.repositories import document_item_repo, document_request_repo
from server.domain.schemas import (
    DocItemReviewIn,
    DocItemStatus,
    DocItemSubmitIn,
    DocRequestIn,
    DocumentItemCreate,
    DocumentItemUpdate,
    DocumentRequestCreate,
    UserRole,
)

from .user_service import UserService, user_service

logger = logging.getLogger(__name__)


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

        request_data = DocumentRequestCreate(**request_in.model_dump())
        return document_request_repo.create(db, obj_in=request_data)

    def submit_document_item(
        self, db: Session, *, item_in: DocItemSubmitIn
    ) -> DriverDocumentItem:
        item_data_for_repo = DocumentItemCreate(
            request_id=item_in.request_id,
            doc_type=item_in.doc_type,
            file_url=str(item_in.file_url),
        )
        return document_item_repo.create(db, obj_in=item_data_for_repo)

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


document_service = DocumentService(user_service=user_service)
