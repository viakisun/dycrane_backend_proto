import logging
from typing import List, Optional

from fastapi import Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from server.config import settings

logger = logging.getLogger(__name__)


class UserContext(BaseModel):
    """
    Schema for the current user's context, extracted from a request.
    In DEV mode, this is derived from headers.
    In strict mode, this would be derived from a validated JWT.
    """

    id: str
    roles: List[str]
    email: Optional[str] = None
    name: Optional[str] = None
    org_ids: List[str] = Field(default_factory=list)


def get_current_user(request: Request) -> UserContext:
    """
    FastAPI dependency to extract the current user context.

    In 'dev' mode, it constructs a user context from special headers.
    In 'strict' mode, it will be replaced with JWT validation.
    """
    if settings.AUTH_MODE != "dev":
        # TODO(strict): Implement JWT decoding and validation here.
        # This includes fetching the public key, verifying the signature,
        # checking expiration, and extracting user claims.
        logger.error("Strict mode authentication not implemented yet.")
        raise NotImplementedError("Strict mode authentication must be implemented.")

    # --- DEV Mode Implementation ---
    auth_header = request.headers.get("Authorization")
    dev_user_id = request.headers.get("X-Dev-User")
    dev_roles_str = request.headers.get("X-Dev-Roles")

    user_id: Optional[str] = None
    roles: List[str] = []

    if auth_header and auth_header.lower().startswith("bearer dev:"):
        try:
            parts = auth_header.split(":", 2)
            if len(parts) == 3:
                _, user_id, roles_csv = parts
                roles = [role.strip() for role in roles_csv.split(",") if role.strip()]
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid 'dev' bearer token format. Expected: 'dev:user_id:role1,role2'.",
            )
    elif dev_user_id:
        user_id = dev_user_id
        if dev_roles_str:
            roles = [
                role.strip().upper()
                for role in dev_roles_str.split("|")
                if role.strip()
            ]

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Provide 'Authorization: Bearer dev:...' or 'X-Dev-User' header in DEV mode.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # TODO(strict): In strict mode, user details (email, name) should be fetched
    # from the database (ops.users) based on the user_id from the JWT.
    # For now, we use dummy data.
    return UserContext(
        id=user_id,
        roles=roles,
        email=f"{user_id.split('-')[0]}@example.dev",
        name=f"Dev User {user_id}",
    )


# For convenience, create a dependency instance
current_user = Depends(get_current_user)
