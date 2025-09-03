import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Response, status, Depends

from server.auth.context import UserContext, get_current_user
from server.core.security import create_dev_access_token
from server.domain.schemas.auth import (
    LoginRequest,
    LoginResponse,
    UserIdentity,
)

router = APIRouter()

# TODO(strict): Add rate limiting to login endpoints.
# TODO(strict): Add password hash verification (e.g., argon2).
@router.post("/login", response_model=LoginResponse)
async def login_for_access_token(request: LoginRequest):
    """
    DEV mode login. Generates a dummy token based on email patterns.
    """
    email_prefix = request.email.split("@")[0]
    roles = ["USER"]  # Default role
    if "driver" in email_prefix:
        roles = ["DRIVER"]
    elif "owner" in email_prefix:
        roles = ["OWNER"]
    elif "safety" in email_prefix:
        roles = ["SAFETY_MANAGER"]

    # TODO(strict): In strict mode, user_id would come from a database lookup.
    user_id = str(uuid.uuid4())
    user = UserIdentity(id=user_id, email=request.email, name=f"Dev User", roles=roles)

    access_token = create_dev_access_token(user_id=user.id, roles=user.roles)

    return LoginResponse(
        access_token=access_token,
        user=user,
        server_time=datetime.now(timezone.utc),
    )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_access_token(current_user: UserContext = Depends(get_current_user)):
    """
    DEV mode token refresh. Issues a new dummy access token.
    TODO(strict): Implement actual refresh token validation and rotation.
    """
    access_token = create_dev_access_token(
        user_id=current_user.id, roles=current_user.roles
    )
    user_identity = UserIdentity(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        roles=current_user.roles,
    )
    return LoginResponse(
        access_token=access_token,
        user=user_identity,
        server_time=datetime.now(timezone.utc),
    )


@router.post("/logout")
async def logout():
    """
    DEV mode logout. Returns 204 No Content.
    TODO(strict): Implement server-side session/token invalidation (e.g., jti blocklist).
    """
    return Response(status_code=status.HTTP_204_NO_CONTENT)
