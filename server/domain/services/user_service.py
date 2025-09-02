import logging
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from server.domain.models import User
from server.domain.repositories import user_repo
from server.domain.schemas import UserRole

logger = logging.getLogger(__name__)


class UserService:
    def get_user_and_validate_role(
        self, db: Session, *, user_id: str, expected_role: UserRole
    ) -> User:
        """
        Retrieves a user by ID and validates their role.
        """
        logger.debug(f"Validating user {user_id} for role {expected_role.value}")
        user = user_repo.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User {user_id} is inactive",
            )
        if user.role != expected_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User must have role {expected_role.value}, but has {user.role.value}",
            )
        logger.info(
            "User %s validated for role %s", user_id, expected_role.value
        )
        return user


user_service = UserService()
