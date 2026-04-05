from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=128, description="Full display name of the user")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    role: UserRole = UserRole.CUSTOMER

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
