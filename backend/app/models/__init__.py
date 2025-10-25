"""
SQLAlchemy models
Import all models here to ensure they are registered with SQLAlchemy
"""
from app.core.database import Base

# Import all models
from .user import User, UserFarm, AuditLog
from .farm import Farm
from .field import Field
from .equipment import Machinery, Implement
from .operation import (
    Operation,
    SowingDetail,
    FertilizerApplication,
    PesticideApplication,
    HarvestData,
    AgrochemicalAnalysis,
    DesiccationDetails,
    TillageDetails,
    IrrigationDetails,
    SnowRetentionDetails,
    FallowDetails,
)

# Export all models
__all__ = [
    "Base",
    "User",
    "UserFarm",
    "AuditLog",
    "Farm",
    "Field",
    "Machinery",
    "Implement",
    "Operation",
    "SowingDetail",
    "FertilizerApplication",
    "PesticideApplication",
    "HarvestData",
    "AgrochemicalAnalysis",
    "DesiccationDetails",
    "TillageDetails",
    "IrrigationDetails",
    "SnowRetentionDetails",
    "FallowDetails",
]
