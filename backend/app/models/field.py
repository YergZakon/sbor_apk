"""
Field model
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class Field(BaseModel):
    """Field/поле model"""
    __tablename__ = "fields"

    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    field_code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100))
    cadastral_number = Column(String(50))
    area_ha = Column(Float, nullable=False)
    center_lat = Column(Float)
    center_lon = Column(Float)
    soil_type = Column(String(100))
    soil_texture = Column(String(50))
    ph_water = Column(Float)
    humus_pct = Column(Float)
    p2o5_mg_kg = Column(Float)
    k2o_mg_kg = Column(Float)
    relief = Column(String(50))
    slope_degree = Column(Float)
    drainage = Column(String(50))
    last_analysis_year = Column(Integer)

    # Relationships
    farm = relationship("Farm", back_populates="fields")
    operations = relationship("Operation", back_populates="field", cascade="all, delete-orphan")
