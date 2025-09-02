import logging
from typing import List, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from server.auth.schemas import CurrentUserSchema
from server.config import settings

logger = logging.getLogger(__name__)

# This is a placeholder for a real OAuth2 flow.
# In DEV mode, we won't use it directly but it helps OpenAPI docs.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(
    request: Request, token: Optional[str] = Depends(oauth2_scheme)
) -> CurrentUserSchema:
    """
    FastAPI dependency to get the current user from the request.

    In 'dev' mode, it uses special headers.
    In 'strict' mode, it will decode a JWT.
    """
    if settings.AUTH_MODE != "dev":
        # TODO(strict): Replace with JWT decoding and validation.
        # - Decode the token using a public key.
        # - Validate claims (iss, aud, exp).
        # - Fetch user details from DB based on 'sub' claim.
        # - Check for token revocation in a blacklist (e.g., Redis).
        raise NotImplementedError("Strict authentication mode is not yet implemented.")

    # --- DEV Mode Logic ---
    if not settings.DEV_AUTH_BYPASS:
        # If bypass is disabled, even in dev mode we might want to enforce some checks.
        # For now, we just proceed if bypass is enabled.
        logger.warning("DEV_AUTH_BYPASS is false, but no alternative dev auth is set up.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Auth bypass is disabled.",
        )

    user_id: Optional[str] = None
    roles: List[str] = []

    # 1. Check "Authorization: Bearer dev:..." header
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.lower().startswith("bearer dev:"):
        try:
            parts = auth_header.split(":", 2)
            if len(parts) == 3:
                user_id = parts[1]
                roles = parts[2].split(",")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid 'dev' bearer token format. Expected 'dev:user_id:role1,role2'.",
            )

    # 2. Check X-Dev-User and X-Dev-Roles headers as a fallback
    elif request.headers.get("x-dev-user"):
        user_id = request.headers.get("x-dev-user")
        roles_str = request.headers.get("x-dev-roles", "")
        if roles_str:
            roles = roles_str.replace(",", "|").split("|")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Provide 'Authorization: Bearer dev:...' or 'X-Dev-User' header in DEV mode.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # TODO(strict): Fetch user details (email, name) from the database (e.g., ops.users).
    # For now, use dummy data.
    return CurrentUserSchema(
        id=user_id,
        roles=[role.strip().upper() for role in roles if role.strip()],
        email=f"{user_id}@example.dev",
        name=f"Dev User {user_id}",
    )
