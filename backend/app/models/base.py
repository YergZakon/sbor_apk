"""
Base model class with common fields
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, func
from app.core.database import Base


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class BaseModel(Base, TimestampMixin):
    """Base model with id and timestamps"""
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
