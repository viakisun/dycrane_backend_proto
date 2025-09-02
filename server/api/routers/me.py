from typing import Dict, List, Any

from fastapi import APIRouter, Depends, status

from server.auth.context import get_current_user
from server.auth.schemas import CurrentUserSchema

router = APIRouter()


@router.get(
    "",
    response_model=CurrentUserSchema,
    summary="Get Current User Profile",
    description="""
    Retrieves the profile of the currently authenticated user.

    The user is identified via the `Authorization` header.
    """,
)
async def get_me(current_user: CurrentUserSchema = Depends(get_current_user)):
    """
    Returns the current user's profile information.
    In the future, this will be enriched with data from the database.
    """
    # TODO(strict): Enrich user model with details from the database.
    # - e.g., `user.org_ids = ops.users.get_org_ids(user.id)`
    # - Consider adding an ETag for caching, as this data changes infrequently.
    return current_user


@router.get(
    "/permissions",
    response_model=Dict[str, List[str]],
    summary="Get User Permissions",
    description="""
    Retrieves the permissions (scopes) for the current user based on their roles.

    **DEV Mode Behavior**:
    - This endpoint returns a hardcoded map of roles to permissions.
    - It is intended for the client to determine UI visibility.
    """,
)
async def get_my_permissions(current_user: CurrentUserSchema = Depends(get_current_user)):
    """
    Returns a list of permission scopes for the current user.
    In DEV mode, this is a hardcoded dictionary.
    """
    # TODO(strict): Replace with a proper permissions service.
    # - This should query a policy engine or database table that defines
    #   role-to-permission mappings.
    # - e.g., `return permission_service.get_scopes_for_roles(user.roles)`
    dev_permissions_map = {
        "DRIVER": ["site.read", "assignment.read"],
        "OWNER": ["crane.read", "assignment.read", "maintenance.read"],
        "SAFETY_MANAGER": [
            "site.read",
            "crane.assign",
            "driver.assign",
            "request.review",
        ],
    }

    user_permissions = []
    for role in current_user.roles:
        user_permissions.extend(dev_permissions_map.get(role, []))

    return {"scopes": sorted(list(set(user_permissions)))}


@router.get(
    "/bootstrap",
    response_model=Dict[str, Any],
    summary="Get UI Bootstrap Data",
    description="""
    Retrieves essential data needed by the client application immediately after login.

    This can include things like unread notification counts, recent tasks, etc.
    to quickly populate the main UI layout.

    **DEV Mode Behavior**:
    - Returns a hardcoded dictionary with zero-values.
    """,
)
async def get_bootstrap_data(current_user: CurrentUserSchema = Depends(get_current_user)):
    """
    Returns a bootstrap payload for the client UI.
    In DEV mode, this is a hardcoded dictionary.
    """
    # TODO: Replace with real data queries.
    # - `notifications_unread = notification_service.get_unread_count(user.id)`
    # - `recent_task_ids = task_service.get_recent_tasks(user.id, limit=5)`
    return {
        "notifications_unread": 0,
        "recent_task_ids": [],
    }
