"""
Operation models
"""
from sqlalchemy import Column, Integer, String, Float, Date, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel


class Operation(BaseModel):
    """Operation model - main operations table"""
    __tablename__ = "operations"

    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False, index=True)
    field_id = Column(Integer, ForeignKey("fields.id", ondelete="CASCADE"), nullable=False, index=True)
    operation_type = Column(String(50), nullable=False, index=True)
    # sowing, fertilizing, spraying, harvest, soil_analysis,
    # desiccation, tillage, irrigation, snow_retention, fallow
    operation_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date)
    crop = Column(String(100))
    variety = Column(String(100))
    area_processed_ha = Column(Float)
    machine_id = Column(Integer, ForeignKey("machinery.id"))
    implement_id = Column(Integer, ForeignKey("implements.id"))
    machine_year = Column(Integer)
    implement_year = Column(Integer)
    work_speed_kmh = Column(Float)
    operator = Column(String(100))
    weather_conditions = Column(Text)
    notes = Column(Text)

    # Relationships
    farm = relationship("Farm", back_populates="operations")
    field = relationship("Field", back_populates="operations")
    machinery = relationship("Machinery", foreign_keys=[machine_id])
    implement = relationship("Implement", foreign_keys=[implement_id])

    # Operation details (one-to-one relationships)
    sowing_details = relationship("SowingDetail", back_populates="operation", uselist=False, cascade="all, delete-orphan")
    fertilizer_applications = relationship("FertilizerApplication", back_populates="operation", cascade="all, delete-orphan")
    pesticide_applications = relationship("PesticideApplication", back_populates="operation", cascade="all, delete-orphan")
    harvest_data = relationship("HarvestData", back_populates="operation", uselist=False, cascade="all, delete-orphan")
    agrochemical_analysis = relationship("AgrochemicalAnalysis", back_populates="operation", uselist=False, cascade="all, delete-orphan")
    desiccation_details = relationship("DesiccationDetails", back_populates="operation", uselist=False, cascade="all, delete-orphan")
    tillage_details = relationship("TillageDetails", back_populates="operation", uselist=False, cascade="all, delete-orphan")
    irrigation_details = relationship("IrrigationDetails", back_populates="operation", uselist=False, cascade="all, delete-orphan")
    snow_retention_details = relationship("SnowRetentionDetails", back_populates="operation", uselist=False, cascade="all, delete-orphan")
    fallow_details = relationship("FallowDetails", back_populates="operation", uselist=False, cascade="all, delete-orphan")


class SowingDetail(BaseModel):
    """Sowing operation details"""
    __tablename__ = "sowing_details"

    operation_id = Column(Integer, ForeignKey("operations.id", ondelete="CASCADE"), nullable=False, unique=True)
    crop = Column(String(100), nullable=False)
    variety = Column(String(100))
    seeding_rate_kg_ha = Column(Float)
    seeding_depth_cm = Column(Float)
    row_spacing_cm = Column(Float)
    seed_treatment = Column(String(100))
    soil_temp_c = Column(Float)
    soil_moisture_percent = Column(Float)
    total_seeds_kg = Column(Float)
    seed_reproduction = Column(String(50))
    seed_origin_country = Column(String(100))
    combined_with_fertilizer = Column(Boolean, default=False)
    combined_fertilizer_name = Column(String(200))
    combined_fertilizer_rate_kg_ha = Column(Float)

    # Relationships
    operation = relationship("Operation", back_populates="sowing_details")


class FertilizerApplication(BaseModel):
    """Fertilizer application details"""
    __tablename__ = "fertilizer_applications"

    operation_id = Column(Integer, ForeignKey("operations.id", ondelete="CASCADE"), nullable=False)
    fertilizer_name = Column(String(100), nullable=False)
    fertilizer_type = Column(String(50))
    rate_kg_ha = Column(Float)
    total_fertilizer_kg = Column(Float)
    n_content_percent = Column(Float)
    p_content_percent = Column(Float)
    k_content_percent = Column(Float)
    n_applied_kg = Column(Float)
    p_applied_kg = Column(Float)
    k_applied_kg = Column(Float)
    application_method = Column(String(50))
    application_purpose = Column(String(50))

    # Relationships
    operation = relationship("Operation", back_populates="fertilizer_applications")


class PesticideApplication(BaseModel):
    """Pesticide application details"""
    __tablename__ = "pesticide_applications"

    operation_id = Column(Integer, ForeignKey("operations.id", ondelete="CASCADE"), nullable=False)
    pesticide_name = Column(String(100), nullable=False)
    pesticide_class = Column(String(50))
    active_ingredient = Column(String(200))
    rate_per_ha = Column(Float)
    total_product_used = Column(Float)
    water_rate_l_ha = Column(Float)
    application_method = Column(String(50))
    target_pest = Column(String(200))
    growth_stage = Column(String(100))
    wind_speed_ms = Column(Float)
    air_temp_c = Column(Float)
    waiting_period_days = Column(Integer)

    # Relationships
    operation = relationship("Operation", back_populates="pesticide_applications")


class HarvestData(BaseModel):
    """Harvest operation data"""
    __tablename__ = "harvest_data"

    operation_id = Column(Integer, ForeignKey("operations.id", ondelete="CASCADE"), nullable=False, unique=True)
    yield_t_ha = Column(Float)
    total_yield_t = Column(Float)
    moisture_percent = Column(Float)
    protein_percent = Column(Float)
    gluten_percent = Column(Float)
    grain_quality_class = Column(Integer)
    test_weight_g_l = Column(Float)
    impurities_percent = Column(Float)
    storage_location = Column(String(200))

    # Relationships
    operation = relationship("Operation", back_populates="harvest_data")


class AgrochemicalAnalysis(BaseModel):
    """Soil agrochemical analysis"""
    __tablename__ = "agrochemical_analyses"

    operation_id = Column(Integer, ForeignKey("operations.id", ondelete="CASCADE"), nullable=False, unique=True)
    analysis_date = Column(Date)
    lab_name = Column(String(200))
    ph_water = Column(Float)
    humus_percent = Column(Float)
    n_total_percent = Column(Float)
    p2o5_mg_kg = Column(Float)
    k2o_mg_kg = Column(Float)
    soil_texture = Column(String(50))
    sample_depth_cm = Column(Integer)
    recommendations = Column(Text)

    # Relationships
    operation = relationship("Operation", back_populates="agrochemical_analysis")


class DesiccationDetails(BaseModel):
    """Desiccation operation details"""
    __tablename__ = "desiccation_details"

    operation_id = Column(Integer, ForeignKey("operations.id", ondelete="CASCADE"), nullable=False, unique=True)
    product_name = Column(String(100))
    active_ingredient = Column(String(200))
    rate_l_ha = Column(Float)
    water_rate_l_ha = Column(Float)
    crop_moisture_before = Column(Float)
    days_before_harvest = Column(Integer)
    application_method = Column(String(100))

    # Relationships
    operation = relationship("Operation", back_populates="desiccation_details")


class TillageDetails(BaseModel):
    """Tillage operation details"""
    __tablename__ = "tillage_details"

    operation_id = Column(Integer, ForeignKey("operations.id", ondelete="CASCADE"), nullable=False, unique=True)
    tillage_type = Column(String(100))
    depth_cm = Column(Float)
    soil_moisture = Column(String(50))
    previous_crop = Column(String(100))

    # Relationships
    operation = relationship("Operation", back_populates="tillage_details")


class IrrigationDetails(BaseModel):
    """Irrigation operation details"""
    __tablename__ = "irrigation_details"

    operation_id = Column(Integer, ForeignKey("operations.id", ondelete="CASCADE"), nullable=False, unique=True)
    water_amount_mm = Column(Float)
    irrigation_method = Column(String(100))
    water_source = Column(String(100))
    soil_moisture_before = Column(Float)

    # Relationships
    operation = relationship("Operation", back_populates="irrigation_details")


class SnowRetentionDetails(BaseModel):
    """Snow retention operation details"""
    __tablename__ = "snow_retention_details"

    operation_id = Column(Integer, ForeignKey("operations.id", ondelete="CASCADE"), nullable=False, unique=True)
    method = Column(String(100))
    snow_depth_cm = Column(Float)
    number_of_passes = Column(Integer)

    # Relationships
    operation = relationship("Operation", back_populates="snow_retention_details")


class FallowDetails(BaseModel):
    """Fallow operation details"""
    __tablename__ = "fallow_details"

    operation_id = Column(Integer, ForeignKey("operations.id", ondelete="CASCADE"), nullable=False, unique=True)
    fallow_type = Column(String(100))
    treatment_type = Column(String(100))
    number_of_treatments = Column(Integer)

    # Relationships
    operation = relationship("Operation", back_populates="fallow_details")
