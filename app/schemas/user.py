from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: UUID
    is_active: bool
    is_superuser: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True
