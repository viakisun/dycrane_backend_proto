from fastapi import APIRouter, Depends

from server.auth.context import UserContext, get_current_user
from server.domain.schemas.user import Bootstrap, Permissions, User

router = APIRouter()


@router.get("", response_model=User)
async def read_current_user(current_user: UserContext = Depends(get_current_user)):
    """
    Get the profile of the currently authenticated user.
    TODO(strict): Enrich user profile with details from the database
    (e.g., ops.users, user_orgs) to include organization info.
    """
    return User(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        roles=current_user.roles,
        org_ids=current_user.org_ids,
        is_active=True,
    )


@router.get("/permissions", response_model=Permissions)
async def read_current_user_permissions(
    current_user: UserContext = Depends(get_current_user),
):
    """
    Get the permissions (scopes) for the currently authenticated user.
    DEV: This is a simple hardcoded role-to-scope mapping.
    TODO(strict): Replace with a proper policy/permissions service that
    can map roles and user attributes to a fine-grained list of scopes.
    """
    # DEV mode: Hardcoded role -> scope mapping
    scope_map = {
        "DRIVER": ["site:read", "assignment:read"],
        "OWNER": ["crane:read", "assignment:read", "maintenance:read"],
        "SAFETY_MANAGER": [
            "site:read",
            "crane:assign",
            "driver:assign",
            "request:review",
        ],
    }

    user_scopes = set()
    for role in current_user.roles:
        user_scopes.update(scope_map.get(role, []))

    return Permissions(scopes=list(user_scopes))


@router.get("/bootstrap", response_model=Bootstrap)
async def get_bootstrap_data(current_user: UserContext = Depends(get_current_user)):
    """
    Get initial data needed for the application UI shell.
    DEV: Returns static dummy data.
    TODO(strict): Implement real queries to get unread notification counts,
    recent tasks, etc.
    """
    return Bootstrap(notifications_unread=0, recent_task_ids=[])
