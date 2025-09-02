import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Response

from server.auth.context import get_current_user
from server.auth.schemas import (
    CurrentUserSchema,
    TokenResponseSchema,
    UserLoginSchema,
)
from server.core.time import get_utc_now

router = APIRouter()


@router.post(
    "/login",
    response_model=TokenResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="""
    Authenticates a user and returns an access token.

    **DEV Mode Behavior**:
    - This endpoint does **not** validate the password.
    - It assigns roles based on the email address prefix:
      - `driver*@...` -> `DRIVER`
      - `owner*@...` -> `OWNER`
      - `safety*@...` -> `SAFETY_MANAGER`
      - Other emails get no roles.
    - The `access_token` is a dummy string for development use.
    """,
)
async def login(form_data: UserLoginSchema):
    """
    Handles user login. In DEV mode, this is a stub that assigns roles
    based on email patterns.
    """
    # TODO(strict): Replace with actual password verification.
    # - Hash the provided password with a salt.
    # - Compare it against the stored hash in the database.
    # - Implement rate limiting to prevent brute-force attacks.

    email_prefix = form_data.email.split("@")[0].lower()
    roles: List[str] = []
    if email_prefix.startswith("driver"):
        roles = ["DRIVER"]
    elif email_prefix.startswith("owner"):
        roles = ["OWNER"]
    elif email_prefix.startswith("safety"):
        roles = ["SAFETY_MANAGER"]

    # Generate a dummy user object
    user_id = str(uuid.uuid4())
    user = CurrentUserSchema(
        id=user_id,
        email=form_data.email,
        name=f"Dev {email_prefix.capitalize()}",
        roles=roles,
    )

    # Generate a dummy access token
    # Format: "dev:{user_id}:{roles_csv}"
    roles_csv = ",".join(user.roles)
    access_token = f"dev:{user.id}:{roles_csv}"

    return TokenResponseSchema(
        access_token=access_token,
        user=user,
        server_time=get_utc_now(),
    )


@router.post(
    "/refresh",
    response_model=TokenResponseSchema,
    summary="Refresh Access Token",
    description="""
    Obtains a new access token using the current valid token.

    **DEV Mode Behavior**:
    - This endpoint takes the existing `dev` token, parses it, and issues a new one.
    - It does not use a refresh token.
    """,
)
async def refresh_token(current_user: CurrentUserSchema = Depends(get_current_user)):
    """
    In DEV mode, this endpoint re-issues a new dummy access token
    for the currently authenticated user.
    """
    # TODO(strict): Implement proper refresh token logic.
    # - The request should contain a 'refresh_token'.
    # - Validate the refresh token against a database of issued tokens.
    # - Ensure the refresh token has not been revoked or expired.
    # - Issue a new, short-lived access token.
    # - Implement refresh token rotation for security.

    # Re-generate a dummy access token
    roles_csv = ",".join(current_user.roles)
    new_access_token = f"dev:{current_user.id}:{roles_csv}"

    return TokenResponseSchema(
        access_token=new_access_token,
        user=current_user,
        server_time=get_utc_now(),
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="User Logout",
    description="""
    Logs the user out.

    **DEV Mode Behavior**:
    - This endpoint does nothing and simply returns a 204 No Content response.
    """,
)
async def logout():
    """
    In DEV mode, this is a dummy endpoint. In strict mode, it would
    invalidate the user's session or refresh token.
    """
    # TODO(strict): Implement server-side token invalidation.
    # - Add the 'jti' (JWT ID) of the refresh token to a denylist (e.g., Redis)
    #   with an expiration equal to the token's remaining validity.
    # - The `get_current_user` dependency would then need to check this denylist.
    return Response(status_code=status.HTTP_204_NO_CONTENT)
