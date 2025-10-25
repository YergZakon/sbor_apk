"""
Farm Pydantic schemas
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class FarmBase(BaseModel):
    """Base farm schema"""
    bin: str = Field(..., min_length=12, max_length=12, description="БИН хозяйства")
    name: str = Field(..., max_length=255)
    director_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = None
    address: Optional[str] = None
    region: Optional[str] = Field(None, max_length=100)
    district: Optional[str] = Field(None, max_length=100)
    village: Optional[str] = Field(None, max_length=100)
    farm_type: Optional[str] = Field(None, max_length=50)
    founded_year: Optional[int] = Field(None, ge=1900, le=2100)


class FarmCreate(FarmBase):
    """Schema for creating a farm"""
    total_area_ha: Optional[float] = Field(None, ge=0)
    arable_area_ha: Optional[float] = Field(None, ge=0)
    fallow_area_ha: Optional[float] = Field(None, ge=0)
    pasture_area_ha: Optional[float] = Field(None, ge=0)
    hayfield_area_ha: Optional[float] = Field(None, ge=0)
    center_lat: Optional[float] = Field(None, ge=-90, le=90)
    center_lon: Optional[float] = Field(None, ge=-180, le=180)


class FarmUpdate(BaseModel):
    """Schema for updating a farm"""
    name: Optional[str] = Field(None, max_length=255)
    director_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    region: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None
    farm_type: Optional[str] = None
    founded_year: Optional[int] = None
    total_area_ha: Optional[float] = Field(None, ge=0)
    arable_area_ha: Optional[float] = Field(None, ge=0)
    fallow_area_ha: Optional[float] = Field(None, ge=0)
    pasture_area_ha: Optional[float] = Field(None, ge=0)
    hayfield_area_ha: Optional[float] = Field(None, ge=0)
    center_lat: Optional[float] = None
    center_lon: Optional[float] = None


class FarmRead(FarmBase):
    """Schema for reading a farm"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    total_area_ha: Optional[float] = None
    arable_area_ha: Optional[float] = None
    fallow_area_ha: Optional[float] = None
    pasture_area_ha: Optional[float] = None
    hayfield_area_ha: Optional[float] = None
    center_lat: Optional[float] = None
    center_lon: Optional[float] = None
    created_at: datetime
    updated_at: datetime


class FarmWithStats(FarmRead):
    """Farm with statistics"""
    fields_count: int = 0
    total_field_area: float = 0.0
    operations_count: int = 0
