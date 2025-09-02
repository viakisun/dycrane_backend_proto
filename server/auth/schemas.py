from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserLoginSchema(BaseModel):
    """Schema for user login request."""
    email: EmailStr
    password: str = Field(..., min_length=8)


class CurrentUserSchema(BaseModel):
    """
    Schema for the current user's identity.
    Represents the user object available in the request context.
    """
    id: str
    roles: List[str] = []
    email: Optional[EmailStr] = None
    name: Optional[str] = None


class TokenResponseSchema(BaseModel):
    """Schema for the response after a successful login."""
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: int = 3600
    token_type: str = "Bearer"
    user: CurrentUserSchema
    capabilities: Optional[dict] = None
    server_time: datetime
