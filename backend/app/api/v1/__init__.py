"""
API v1 routes
"""
from fastapi import APIRouter
from . import auth, farms, fields

# Create API v1 router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(farms.router, prefix="/farms", tags=["farms"])
api_router.include_router(fields.router, prefix="/fields", tags=["fields"])

__all__ = ["api_router"]
