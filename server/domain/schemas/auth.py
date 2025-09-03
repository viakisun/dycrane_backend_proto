from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

# TODO(strict): This file will need to be updated for strict mode,
# especially regarding token contents and capabilities.


class LoginRequest(BaseModel):
    """Schema for user login request."""

    email: EmailStr
    password: str = Field(..., min_length=8)


class UserIdentity(BaseModel):
    """Represents the user's identity included in the login response."""

    id: str
    email: EmailStr
    name: Optional[str] = None
    roles: List[str]


class LoginResponse(BaseModel):
    """
    Schema for the response after a successful login.
    This structure is designed to be compatible with OAuth2-like flows.
    """

    access_token: str
    refresh_token: Optional[str] = None
    expires_in: int = 3600
    token_type: str = "Bearer"
    user: UserIdentity
    capabilities: Optional[dict] = None
    server_time: datetime = Field(default_factory=datetime.utcnow)
