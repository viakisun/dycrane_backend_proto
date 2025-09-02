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
