import hashlib
import logging
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union, cast

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from server.domain.models import (
    DriverAttendance,
    Base,
    Crane,
    DriverAssignment,
    DriverDocumentItem,
    DriverDocumentRequest,
    Site,
    SiteCraneAssignment,
    User,
)
from server.domain.schemas import (
    AttendanceCreate,
    AttendanceUpdate,
    CraneCreate,
    CraneStatus,
    CraneUpdate,
    DocumentItemCreate,
    DocumentItemUpdate,
    DocumentRequestCreate,
    DocumentRequestUpdate,
    DriverAssignmentCreate,
    DriverAssignmentUpdate,
    SiteCraneAssignmentCreate,
    SiteCraneAssignmentUpdate,
    SiteCreate,
    SiteUpdate,
    UserCreate,
    UserUpdate,
)

# Define custom types for SQLAlchemy models and Pydantic schemas
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

logger = logging.getLogger(__name__)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base class for data repositories.
    Provides generic CRUD operations for a given SQLAlchemy model.
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initializes the repository with a specific SQLAlchemy model.

        Args:
            model: The SQLAlchemy model class.
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        Retrieves a record by its ID.

        Args:
            db: The database session.
            id: The ID of the record to retrieve.

        Returns:
            The model instance if found, otherwise None.
        """
        logger.debug(f"Getting {self.model.__name__} with id: {id}")
        return cast(
            Optional[ModelType],
            db.query(self.model).filter(self.model.id == id).first(),
        )

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Retrieves multiple records with pagination.

        Args:
            db: The database session.
            skip: The number of records to skip.
            limit: The maximum number of records to return.

        Returns:
            A list of model instances.
        """
        logger.debug(
            f"Getting multiple {self.model.__name__} with skip: {skip}, limit: {limit}"
        )
        return cast(List[ModelType], db.query(self.model).offset(skip).limit(limit).all())

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Creates a new record in the database.

        Args:
            db: The database session.
            obj_in: The Pydantic schema with the data to create.

        Returns:
            The newly created model instance.
        """
        logger.debug(f"Creating new {self.model.__name__}")
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        try:
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Created new {self.model.__name__} with id: {db_obj.id}")
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error on create: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {e}"
            )

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """
        Updates an existing record in the database.

        Args:
            db: The database session.
            db_obj: The existing model instance to update.
            obj_in: The Pydantic schema or dict with the data to update.

        Returns:
            The updated model instance.
        """
        logger.debug(f"Updating {self.model.__name__} with id: {db_obj.id}")
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        logger.info(f"Updated {self.model.__name__} with id: {db_obj.id}")
        return db_obj

    def remove(self, db: Session, *, id: Any) -> ModelType:
        """
        Removes a record from the database by its ID.

        Args:
            db: The database session.
            id: The ID of the record to remove.

        Returns:
            The removed model instance.
        """
        logger.debug(f"Removing {self.model.__name__} with id: {id}")
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        logger.info(f"Removed {self.model.__name__} with id: {id}")
        return cast(ModelType, obj)


# Example of a specific repository
class SiteRepository(BaseRepository[Site, SiteCreate, SiteUpdate]):
    def get_multi_for_user(
        self, db: Session, *, user_id: Optional[str] = None
    ) -> List[Site]:
        """
        Retrieves multiple sites, optionally filtered by a user involved.
        A simple implementation might just check the 'requested_by_id'.
        A more complex one would check assignments for owners/drivers.
        """
        query = db.query(self.model)
        if user_id:
            # For now, we only filter by the user who requested the site.
            query = query.filter(self.model.requested_by_id == user_id)
        return cast(List[Site], query.all())


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        # A real implementation would use a proper password hashing library like passlib
        hashed_password = hashlib.sha256(obj_in.password.encode()).hexdigest()
        create_data = obj_in.model_dump(exclude={"password"})
        create_data["hashed_password"] = hashed_password

        db_obj = self.model(**create_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return cast(Optional[User], db.query(User).filter(User.email == email).first())


class CraneRepository(BaseRepository[Crane, CraneCreate, CraneUpdate]):
    def get_by_owner(
        self, db: Session, *, owner_org_id: str, status: Optional[CraneStatus] = None
    ) -> List[Crane]:
        query = db.query(Crane).filter(Crane.owner_org_id == owner_org_id)
        if status:
            query = query.filter(Crane.status == status)
        return cast(List[Crane], query.all())


class SiteCraneAssignmentRepository(
    BaseRepository[
        SiteCraneAssignment, SiteCraneAssignmentCreate, SiteCraneAssignmentUpdate
    ]
):
    pass


class DriverAssignmentRepository(
    BaseRepository[DriverAssignment, DriverAssignmentCreate, DriverAssignmentUpdate]
):
    pass


class DocumentRequestRepository(
    BaseRepository[
        DriverDocumentRequest, DocumentRequestCreate, DocumentRequestUpdate
    ]
):
    pass


class DocumentItemRepository(
    BaseRepository[DriverDocumentItem, DocumentItemCreate, DocumentItemUpdate]
):
    pass


class AttendanceRepository(
    BaseRepository[DriverAttendance, AttendanceCreate, AttendanceUpdate]
):
    pass


site_repo = SiteRepository(Site)
user_repo = UserRepository(User)
crane_repo = CraneRepository(Crane)
site_crane_assignment_repo = SiteCraneAssignmentRepository(SiteCraneAssignment)
driver_assignment_repo = DriverAssignmentRepository(DriverAssignment)
document_request_repo = DocumentRequestRepository(DriverDocumentRequest)
document_item_repo = DocumentItemRepository(DriverDocumentItem)
attendance_repo = AttendanceRepository(DriverAttendance)
