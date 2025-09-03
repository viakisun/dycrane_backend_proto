# TODO(strict): This file should be expanded with real security helpers
# (password hashing, JWT creation/decoding) in strict mode.

from typing import List


def create_dev_access_token(user_id: str, roles: List[str]) -> str:
    """
    Creates a dummy access token for DEV mode.
    Format: "dev:{user_id}:{role1,role2,...}"
    """
    roles_csv = ",".join(roles)
    return f"dev:{user_id}:{roles_csv}"
