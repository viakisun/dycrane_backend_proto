from typing import Optional
from pydantic import BaseModel
from .enums import UserRole

# ========= USER SCHEMAS =========


class UserBase(BaseModel):
    email: Optional[str] = None
    is_active: Optional[bool] = True
    name: Optional[str] = None
    role: Optional[UserRole] = None


class UserCreate(UserBase):
    email: str
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


# Schemas for the /me endpoints
# These are distinct from the basic User schemas as they represent
# the data for the currently authenticated user.

from typing import List

class User(BaseModel):
    """Schema for user details returned by /api/v1/me"""
    id: str
    email: Optional[str] = None
    name: Optional[str] = None
    roles: List[str] = []
    org_ids: List[str] = []
    is_active: bool = True

class Permissions(BaseModel):
    """Schema for user permissions returned by /api/v1/me/permissions"""
    scopes: List[str] = []

class Bootstrap(BaseModel):
    """Schema for initial application bootstrap data"""
    notifications_unread: int = 0
    recent_task_ids: List[str] = []
