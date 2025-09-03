from typing import List, Set

from fastapi import Depends, HTTPException, status

from server.auth.context import UserContext, get_current_user


class RoleChecker:
    """
    Dependency class to check for user roles.
    This allows the dependency to be created with parameters (*roles).
    """

    def __init__(self, required_roles: List[str]):
        self.required_roles: Set[str] = set(required_roles)

    def __call__(self, user: UserContext = Depends(get_current_user)) -> UserContext:
        """
        Checks if the current user has any of the required roles.

        In DEV mode, this is a simple role name check.
        TODO(strict): In strict mode, this should be replaced with a proper
        RBAC system that checks permissions/scopes against a policy service
        or database table, not just simple role names.
        """
        user_roles = set(user.roles)
        if not self.required_roles.intersection(user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"User does not have required roles. "
                    f"Required: {list(self.required_roles)}, "
                    f"User has: {list(user_roles)}"
                ),
            )
        return user


# A more readable alias for the dependency factory
require_roles = RoleChecker
