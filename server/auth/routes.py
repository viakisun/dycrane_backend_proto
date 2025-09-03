import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Response, status, Depends, HTTPException
from sqlalchemy.orm import Session

from server.auth.context import UserContext, get_current_user
from server.core.security import create_dev_access_token
from server.database import get_db
from server.domain.repositories import user_repo
from server.domain.schemas.auth import (
    LoginRequest,
    LoginResponse,
    UserIdentity,
)

router = APIRouter()


# TODO(strict): Add rate limiting to login endpoints.
# TODO(strict): Add password hash verification (e.g., argon2).
@router.post("/login", response_model=LoginResponse)
async def login_for_access_token(
    request: LoginRequest, db: Session = Depends(get_db)
):
    """
    Authenticates a user and returns an access token.
    - Looks up the user by email.
    - In this version, password is not checked.
    - If user is found and active, generates a DEV access token.
    """
    user = user_repo.get_by_email(db, email=request.email)

    if not user or not user.is_active:
        # Note: It's good practice to use a generic error message
        # to avoid leaking information about which accounts exist.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # The user's role from the DB is an enum, so we get its value.
    # The token expects a list of roles, so we wrap it in a list.
    roles = [user.role.value]

    user_identity = UserIdentity(
        id=user.id, email=user.email, name=user.name, roles=roles
    )

    access_token = create_dev_access_token(user_id=user.id, roles=roles)

    return LoginResponse(
        access_token=access_token,
        user=user_identity,
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
