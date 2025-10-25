"""
Pydantic schemas for API request/response
"""
from .user import (
    UserBase,
    UserCreate,
    UserRegister,
    UserUpdate,
    UserUpdatePassword,
    UserRead,
    UserInDB,
    UserFarmBase,
    UserFarmCreate,
    UserFarmUpdate,
    UserFarmRead,
    Token,
    TokenPayload,
)
from .farm import (
    FarmBase,
    FarmCreate,
    FarmUpdate,
    FarmRead,
    FarmWithStats,
)
from .field import (
    FieldBase,
    FieldCreate,
    FieldUpdate,
    FieldRead,
    FieldWithStats,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserRegister",
    "UserUpdate",
    "UserUpdatePassword",
    "UserRead",
    "UserInDB",
    "UserFarmBase",
    "UserFarmCreate",
    "UserFarmUpdate",
    "UserFarmRead",
    "Token",
    "TokenPayload",
    # Farm schemas
    "FarmBase",
    "FarmCreate",
    "FarmUpdate",
    "FarmRead",
    "FarmWithStats",
    # Field schemas
    "FieldBase",
    "FieldCreate",
    "FieldUpdate",
    "FieldRead",
    "FieldWithStats",
]
