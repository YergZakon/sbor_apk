"""
Field Pydantic schemas
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class FieldBase(BaseModel):
    """Base field schema"""
    name: Optional[str] = Field(None, max_length=100)
    cadastral_number: Optional[str] = Field(None, max_length=50)
    area_ha: float = Field(..., gt=0, description="Площадь поля в гектарах")
    center_lat: Optional[float] = Field(None, ge=-90, le=90)
    center_lon: Optional[float] = Field(None, ge=-180, le=180)
    soil_type: Optional[str] = Field(None, max_length=100)
    soil_texture: Optional[str] = Field(None, max_length=50)
    ph_water: Optional[float] = Field(None, ge=0, le=14)
    humus_pct: Optional[float] = Field(None, ge=0, le=100)
    p2o5_mg_kg: Optional[float] = Field(None, ge=0)
    k2o_mg_kg: Optional[float] = Field(None, ge=0)
    relief: Optional[str] = Field(None, max_length=50)
    slope_degree: Optional[float] = Field(None, ge=0, le=90)
    drainage: Optional[str] = Field(None, max_length=50)
    last_analysis_year: Optional[int] = Field(None, ge=1900, le=2100)


class FieldCreate(FieldBase):
    """Schema for creating a field"""
    farm_id: int


class FieldUpdate(BaseModel):
    """Schema for updating a field"""
    name: Optional[str] = None
    cadastral_number: Optional[str] = None
    area_ha: Optional[float] = Field(None, gt=0)
    center_lat: Optional[float] = None
    center_lon: Optional[float] = None
    soil_type: Optional[str] = None
    soil_texture: Optional[str] = None
    ph_water: Optional[float] = None
    humus_pct: Optional[float] = None
    p2o5_mg_kg: Optional[float] = None
    k2o_mg_kg: Optional[float] = None
    relief: Optional[str] = None
    slope_degree: Optional[float] = None
    drainage: Optional[str] = None
    last_analysis_year: Optional[int] = None


class FieldRead(FieldBase):
    """Schema for reading a field"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    farm_id: int
    field_code: str
    created_at: datetime


class FieldWithStats(FieldRead):
    """Field with operation statistics"""
    operations_count: int = 0
    last_operation_date: Optional[datetime] = None
