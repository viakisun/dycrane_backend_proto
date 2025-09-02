from functools import wraps
from typing import List

from fastapi import Depends, HTTPException, status

from server.auth.context import get_current_user
from server.auth.schemas import CurrentUserSchema
from server.config import settings


class RoleChecker:
    """
    Dependency to check if the current user has at least one of the required roles.
    """

    def __init__(self, required_roles: List[str]):
        self.required_roles = set(required_roles)

    def __call__(self, user: CurrentUserSchema = Depends(get_current_user)):
        """
        Callable that performs the role check.
        """
        if settings.AUTH_MODE != "dev":
            # TODO(strict): Replace with a proper RBAC check.
            # - This should involve checking a permissions service or a database table
            #   that maps roles to specific permissions (e.g., 'crane:read', 'site:create').
            # - The check should be based on permissions, not just roles.
            raise NotImplementedError("Strict RBAC mode is not yet implemented.")

        # --- DEV Mode Logic ---
        user_roles = set(user.roles)
        if not self.required_roles.intersection(user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"User does not have the required roles. "
                    f"Required: {list(self.required_roles)}, User has: {list(user_roles)}"
                ),
            )


# This is the factory for the dependency.
# It will be used in path operations like: `Depends(require_roles(["ADMIN"]))`
require_roles = RoleChecker
