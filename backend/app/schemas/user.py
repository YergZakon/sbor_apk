"""
User Pydantic schemas
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# Base schemas
class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=200)


# Create schemas
class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=8)
    role: str = Field(default="farmer", pattern="^(admin|farmer|viewer)$")


class UserRegister(BaseModel):
    """Schema for user registration"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


# Update schemas
class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = Field(None, pattern="^(admin|farmer|viewer)$")
    is_active: Optional[bool] = None


class UserUpdatePassword(BaseModel):
    """Schema for updating password"""
    current_password: str
    new_password: str = Field(..., min_length=8)


# Response schemas
class UserRead(UserBase):
    """Schema for reading a user"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    is_active: bool
    farm_id: Optional[int] = None
    created_at: datetime
    last_login: Optional[datetime] = None


class UserInDB(UserRead):
    """User schema with hashed password (internal use)"""
    hashed_password: str


# User-Farm relationship schemas
class UserFarmBase(BaseModel):
    """Base user-farm relationship schema"""
    user_id: int
    farm_id: int
    role: str = Field(default="viewer", pattern="^(admin|manager|viewer)$")
    is_primary: bool = False


class UserFarmCreate(UserFarmBase):
    """Schema for creating user-farm relationship"""
    pass


class UserFarmUpdate(BaseModel):
    """Schema for updating user-farm relationship"""
    role: Optional[str] = Field(None, pattern="^(admin|manager|viewer)$")
    is_primary: Optional[bool] = None


class UserFarmRead(UserFarmBase):
    """Schema for reading user-farm relationship"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


# Authentication schemas
class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: int  # user_id
    exp: datetime
    type: str  # "access" or "refresh"
