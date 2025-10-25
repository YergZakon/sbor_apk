"""
User and authentication models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import BaseModel, TimestampMixin
from app.core.database import Base


class User(BaseModel):
    """User model"""
    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200))
    role = Column(String(20), nullable=False, default="farmer")  # admin, farmer, viewer
    is_active = Column(Boolean, default=True, nullable=False)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=True)  # Legacy: single farm
    last_login = Column(DateTime)

    # Relationships
    farm = relationship("Farm", back_populates="users", foreign_keys=[farm_id])
    user_farms = relationship("UserFarm", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")


class UserFarm(Base, TimestampMixin):
    """Many-to-many relationship between users and farms"""
    __tablename__ = "user_farms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), default="viewer", nullable=False)  # admin, manager, viewer
    is_primary = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="user_farms")
    farm = relationship("Farm", back_populates="user_farms")

    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'farm_id', name='uq_user_farm'),
    )


class AuditLog(Base, TimestampMixin):
    """Audit log for user actions"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(100), nullable=False)  # login, logout, create, update, delete
    entity_type = Column(String(50))  # farm, field, operation, etc.
    entity_id = Column(Integer)
    details = Column(String)  # JSON details
    ip_address = Column(String(50))

    # Relationships
    user = relationship("User", back_populates="audit_logs")
