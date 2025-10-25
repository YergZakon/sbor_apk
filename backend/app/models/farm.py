"""
Farm model
"""
from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.orm import relationship
from .base import BaseModel


class Farm(BaseModel):
    """Farm/хозяйство model"""
    __tablename__ = "farms"

    bin = Column(String(12), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    director_name = Column(String(255))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    region = Column(String(100))  # Область
    district = Column(String(100))  # Район
    village = Column(String(100))  # Населенный пункт
    farm_type = Column(String(50))
    founded_year = Column(Integer)
    total_area_ha = Column(Float)
    arable_area_ha = Column(Float)
    fallow_area_ha = Column(Float)
    pasture_area_ha = Column(Float)
    hayfield_area_ha = Column(Float)
    center_lat = Column(Float)
    center_lon = Column(Float)

    # Relationships
    fields = relationship("Field", back_populates="farm", cascade="all, delete-orphan")
    users = relationship("User", back_populates="farm", foreign_keys="[User.farm_id]")
    user_farms = relationship("UserFarm", back_populates="farm", cascade="all, delete-orphan")
    operations = relationship("Operation", back_populates="farm")
