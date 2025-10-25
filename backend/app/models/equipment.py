"""
Equipment models (Machinery and Implements)
"""
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class Machinery(BaseModel):
    """Machinery model - tractors, combines, sprayers"""
    __tablename__ = "machinery"

    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    machinery_type = Column(String(50), nullable=False)
    # tractor, combine, self_propelled_sprayer, grain_truck
    brand = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    year = Column(Integer)
    engine_power_hp = Column(Integer)
    fuel_type = Column(String(50))
    fuel_consumption_l_ha = Column(Float)
    purchase_date = Column(Date)
    purchase_price = Column(Float)
    current_value = Column(Float)
    status = Column(String(20), default="active")  # active, maintenance, retired
    notes = Column(String)

    # Relationships
    farm = relationship("Farm")


class Implement(BaseModel):
    """Implements model - seeders, plows, cultivators, etc."""
    __tablename__ = "implements"

    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    implement_type = Column(String(50), nullable=False)
    # seeder, planter, plow, cultivator, harrow, disc,
    # deep_loosener, roller, sprayer_trailer, fertilizer_spreader,
    # stubble_breaker, snow_plow, header, mower, baler, other
    brand = Column(String(100))
    model = Column(String(100))
    year = Column(Integer)
    working_width_m = Column(Float)
    purchase_date = Column(Date)
    purchase_price = Column(Float)
    current_value = Column(Float)
    status = Column(String(20), default="active")
    notes = Column(String)

    # Relationships
    farm = relationship("Farm")
