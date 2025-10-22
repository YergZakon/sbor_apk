"""
Database models and connection management
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, Boolean, Text, ForeignKey, func
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./farm_data.db")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============================================================================
# AUTHENTICATION & AUTHORIZATION
# ============================================================================

class User(Base):
    """Пользователь системы"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200))
    role = Column(String(20), nullable=False, default="farmer")  # admin, farmer, viewer
    is_active = Column(Boolean, default=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=True)  # Привязка к хозяйству
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)

    # Relationships
    farm = relationship("Farm", back_populates="users", foreign_keys=[farm_id])


class AuditLog(Base):
    """Журнал действий пользователей"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(100), nullable=False)  # login, logout, create, update, delete
    entity_type = Column(String(50))  # farm, field, operation, etc.
    entity_id = Column(Integer)
    details = Column(Text)  # JSON с деталями
    ip_address = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())


# ============================================================================
# ОСНОВНЫЕ ТАБЛИЦЫ
# ============================================================================

class Farm(Base):
    """Хозяйство"""
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    bin = Column(String(12), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    director_name = Column(String(255))  # ФИО руководителя
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    region = Column(String(100))  # Область
    district = Column(String(100))  # Район
    village = Column(String(100))  # Населенный пункт
    farm_type = Column(String(50))
    founded_year = Column(Integer)
    total_area_ha = Column(Float)  # Общая площадь
    arable_area_ha = Column(Float)  # Пашня
    fallow_area_ha = Column(Float)  # Залежь
    pasture_area_ha = Column(Float)  # Пастбища
    hayfield_area_ha = Column(Float)  # Сенокосы
    center_lat = Column(Float)
    center_lon = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    fields = relationship("Field", back_populates="farm")
    users = relationship("User", back_populates="farm", foreign_keys="[User.farm_id]")


class Field(Base):
    """Поле"""
    __tablename__ = "fields"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
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
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    farm = relationship("Farm", back_populates="fields")
    operations = relationship("Operation", back_populates="field")


class Operation(Base):
    """Операция (посев, обработка, уборка)"""
    __tablename__ = "operations"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)  # Добавлено farm_id
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False)
    operation_type = Column(String(50), nullable=False)  # sowing, fertilizing, spraying, harvest, soil_analysis, desiccation, tillage, irrigation, snow_retention, fallow
    operation_date = Column(Date, nullable=False)
    end_date = Column(Date)  # Дата окончания операции (для многодневных работ)
    crop = Column(String(100))
    variety = Column(String(100))
    area_processed_ha = Column(Float)  # Переименовано для консистентности
    machine_id = Column(Integer, ForeignKey("machinery.id"))  # Техника (трактор, комбайн, опрыскиватель)
    implement_id = Column(Integer, ForeignKey("implements.id"))  # Агрегат (сеялка, культиватор, борона)
    machine_year = Column(Integer)  # Год выпуска техники
    implement_year = Column(Integer)  # Год выпуска агрегата
    work_speed_kmh = Column(Float)  # Рабочая скорость км/ч
    operator = Column(String(100))
    weather_conditions = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    field = relationship("Field", back_populates="operations")
    machinery = relationship("Machinery", foreign_keys=[machine_id])
    implement = relationship("Implements", foreign_keys=[implement_id])
    sowing_details = relationship("SowingDetail", back_populates="operation", uselist=False)
    fertilizer_applications = relationship("FertilizerApplication", back_populates="operation")
    pesticide_applications = relationship("PesticideApplication", back_populates="operation")
    harvest_data = relationship("HarvestData", back_populates="operation", uselist=False)
    agrochemical_analysis = relationship("AgrochemicalAnalysis", back_populates="operation", uselist=False)
    desiccation_details = relationship("DesiccationDetails", back_populates="operation", uselist=False)
    tillage_details = relationship("TillageDetails", back_populates="operation", uselist=False)
    irrigation_details = relationship("IrrigationDetails", back_populates="operation", uselist=False)
    snow_retention_details = relationship("SnowRetentionDetails", back_populates="operation", uselist=False)
    fallow_details = relationship("FallowDetails", back_populates="operation", uselist=False)


class SowingDetail(Base):
    """Детали посева"""
    __tablename__ = "sowing_details"

    id = Column(Integer, primary_key=True, index=True)
    operation_id = Column(Integer, ForeignKey("operations.id"), nullable=False)
    crop = Column(String(100), nullable=False)  # Культура
    variety = Column(String(100))  # Сорт
    seeding_rate_kg_ha = Column(Float)  # Норма высева
    seeding_depth_cm = Column(Float)  # Глубина заделки
    row_spacing_cm = Column(Float)  # Междурядье
    seed_treatment = Column(String(100))  # Протравитель
    soil_temp_c = Column(Float)  # Температура почвы
    soil_moisture_percent = Column(Float)  # Влажность почвы
    total_seeds_kg = Column(Float)  # Всего семян
    seed_reproduction = Column(String(50))  # Репродукция семян (элита, 1-я, 2-я и т.д.)
    seed_origin_country = Column(String(100))  # Страна происхождения семян
    combined_with_fertilizer = Column(Boolean, default=False)  # Совмещенный посев с удобрениями
    combined_fertilizer_name = Column(String(200))  # Название удобрения при совмещенном посеве
    combined_fertilizer_rate_kg_ha = Column(Float)  # Норма удобрения при совмещенном посеве

    # Relationships
    operation = relationship("Operation", back_populates="sowing_details")


class FertilizerApplication(Base):
    """Внесение удобрений"""
    __tablename__ = "fertilizer_applications"

    id = Column(Integer, primary_key=True, index=True)
    operation_id = Column(Integer, ForeignKey("operations.id"), nullable=False)
    fertilizer_name = Column(String(100), nullable=False)
    fertilizer_type = Column(String(50))  # Категория
    rate_kg_ha = Column(Float)  # Норма физ. веса
    total_fertilizer_kg = Column(Float)  # Всего удобрений
    n_content_percent = Column(Float)  # Содержание N %
    p_content_percent = Column(Float)  # Содержание P %
    k_content_percent = Column(Float)  # Содержание K %
    n_applied_kg = Column(Float)  # Внесено N д.в.
    p_applied_kg = Column(Float)  # Внесено P д.в.
    k_applied_kg = Column(Float)  # Внесено K д.в.
    application_method = Column(String(50))  # Способ внесения
    application_purpose = Column(String(50))  # Цель внесения

    # Relationships
    operation = relationship("Operation", back_populates="fertilizer_applications")


class PesticideApplication(Base):
    """Применение СЗР"""
    __tablename__ = "pesticide_applications"

    id = Column(Integer, primary_key=True, index=True)
    operation_id = Column(Integer, ForeignKey("operations.id"), nullable=False)
    pesticide_name = Column(String(100), nullable=False)
    pesticide_class = Column(String(50))  # Класс препарата
    active_ingredient = Column(String(200))  # Действующее вещество
    rate_per_ha = Column(Float)  # Норма расхода на га
    total_product_used = Column(Float)  # Всего использовано
    water_rate_l_ha = Column(Float)  # Расход воды л/га
    application_method = Column(String(50))  # Способ применения
    treatment_target = Column(String(100))  # Цель обработки
    growth_stage = Column(String(100))  # Фаза развития
    temperature_c = Column(Float)  # Температура воздуха
    wind_speed_ms = Column(Float)  # Скорость ветра
    humidity_percent = Column(Float)  # Влажность
    waiting_period_days = Column(Integer)  # Срок ожидания

    # Relationships
    operation = relationship("Operation", back_populates="pesticide_applications")


class HarvestData(Base):
    """Данные уборки"""
    __tablename__ = "harvest_data"

    id = Column(Integer, primary_key=True, index=True)
    operation_id = Column(Integer, ForeignKey("operations.id"), nullable=False)
    crop = Column(String(100))  # Культура
    variety = Column(String(100))  # Сорт
    yield_t_ha = Column(Float)  # Урожайность т/га
    total_yield_t = Column(Float)  # Валовой сбор
    moisture_percent = Column(Float)  # Влажность
    protein_percent = Column(Float)  # Белок
    gluten_percent = Column(Float)  # Клейковина
    test_weight_g_l = Column(Float)  # Натура
    falling_number = Column(Integer)  # Число падения
    weed_content_percent = Column(Float)  # Засоренность
    oil_content_percent = Column(Float)  # Масличность
    quality_class = Column(Integer)  # Класс качества

    # Relationships
    operation = relationship("Operation", back_populates="harvest_data")


class AgrochemicalAnalysis(Base):
    """Агрохимические анализы"""
    __tablename__ = "agrochemical_analyses"

    id = Column(Integer, primary_key=True, index=True)
    operation_id = Column(Integer, ForeignKey("operations.id"), nullable=False)  # Связь с операцией
    sample_depth_cm = Column(Integer)  # Глубина отбора
    sample_location = Column(String(100))
    ph_water = Column(Float)
    ph_salt = Column(Float)  # pH солевой (вместо ph_kcl)
    humus_percent = Column(Float)  # Гумус (переименовано)
    nitrogen_total_percent = Column(Float)  # Азот общий
    p2o5_mg_kg = Column(Float)
    k2o_mg_kg = Column(Float)
    mobile_s_mg_kg = Column(Float)  # Сера подвижная
    no3_mg_kg = Column(Float)
    nh4_mg_kg = Column(Float)
    ec_ds_m = Column(Float)
    cec_cmol_kg = Column(Float)
    ca_mg_kg = Column(Float)
    mg_mg_kg = Column(Float)
    na_mg_kg = Column(Float)  # Натрий
    zn_mg_kg = Column(Float)
    cu_mg_kg = Column(Float)
    fe_mg_kg = Column(Float)
    mn_mg_kg = Column(Float)
    b_mg_kg = Column(Float)
    sand_pct = Column(Float)
    silt_pct = Column(Float)
    clay_pct = Column(Float)
    lab_name = Column(String(200))
    analysis_method = Column(String(100))
    notes = Column(Text)

    # Relationships
    operation = relationship("Operation", back_populates="agrochemical_analysis")


class EconomicData(Base):
    """Экономические данные"""
    __tablename__ = "economic_data"

    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False)
    year = Column(Integer, nullable=False)
    crop = Column(String(100))
    area_ha = Column(Float)
    seeds_cost_kzt_ha = Column(Float)
    fertilizers_cost_kzt_ha = Column(Float)
    pesticides_cost_kzt_ha = Column(Float)
    fuel_cost_kzt_ha = Column(Float)
    labor_cost_kzt_ha = Column(Float)
    other_costs_kzt_ha = Column(Float)
    total_costs_kzt_ha = Column(Float)
    yield_t_ha = Column(Float)
    selling_price_kzt_t = Column(Float)
    revenue_kzt_ha = Column(Float)
    profit_kzt_ha = Column(Float)
    profitability_pct = Column(Float)
    field_rental_cost = Column(Float)  # Стоимость аренды поля
    field_rental_period = Column(String(50))  # Период аренды (год, сезон, месяц)
    machinery_rental_cost = Column(Float)  # Стоимость аренды техники
    machinery_rental_type = Column(String(50))  # Тип аренды техники (за час, за день, за га)
    rented_machinery_description = Column(Text)  # Описание арендованной техники
    notes = Column(Text)


class WeatherData(Base):
    """Метеоданные"""
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    datetime = Column(DateTime, nullable=False)
    temp_air_c = Column(Float)
    temp_min_c = Column(Float)
    temp_max_c = Column(Float)
    precipitation_mm = Column(Float)
    humidity_pct = Column(Float)
    wind_speed_ms = Column(Float)
    wind_direction = Column(String(20))
    solar_radiation_wm2 = Column(Float)
    pressure_hpa = Column(Float)
    temp_soil_5cm_c = Column(Float)
    temp_soil_10cm_c = Column(Float)
    soil_moisture_pct = Column(Float)
    evapotranspiration_mm = Column(Float)
    notes = Column(Text)


class Machinery(Base):
    """Техника (трактора, комбайны, самоходные опрыскиватели, дроны)"""
    __tablename__ = "machinery"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    machinery_type = Column(String(50), nullable=False)  # tractor, combine, self_propelled_sprayer, drone, irrigation_system, other
    brand = Column(String(100))
    model = Column(String(100), nullable=False)
    year = Column(Integer)
    registration_number = Column(String(50))
    engine_power_hp = Column(Float)
    fuel_type = Column(String(50))  # diesel, gasoline, electric, hybrid, gas
    purchase_date = Column(Date)
    purchase_price = Column(Float)
    current_value = Column(Float)
    status = Column(String(20), default='active')  # active, repair, sold, rented_out, rented_in
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Implements(Base):
    """Агрегаты (сеялки, бороны, культиваторы, прицепные опрыскиватели)"""
    __tablename__ = "implements"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    implement_type = Column(String(50), nullable=False)  # seeder, planter, plow, cultivator, harrow, disc, deep_loosener, roller, sprayer_trailer, fertilizer_spreader, stubble_breaker, snow_plow, other
    brand = Column(String(100))
    model = Column(String(100), nullable=False)
    year = Column(Integer)
    working_width_m = Column(Float)
    purchase_date = Column(Date)
    purchase_price = Column(Float)
    current_value = Column(Float)
    status = Column(String(20), default='active')  # active, repair, sold, rented_out, rented_in
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# ============================================================================
# НОВЫЕ ТАБЛИЦЫ
# ============================================================================

class PhytosanitaryMonitoring(Base):
    """Фитосанитарный мониторинг (болезни, вредители, сорняки)"""
    __tablename__ = "phytosanitary_monitoring"

    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False)
    inspection_date = Column(Date, nullable=False)
    pest_type = Column(String(50), nullable=False)  # disease, pest, weed
    pest_name = Column(String(200), nullable=False)
    latin_name = Column(String(200))
    severity_pct = Column(Float)  # 0-100 степень поражения
    prevalence_pct = Column(Float)  # 0-100 распространенность
    intensity_score = Column(Integer)  # 1-5 баллы
    threshold_exceeded = Column(Boolean)
    crop_stage = Column(String(100))
    control_measures = Column(Text)
    control_effectiveness_pct = Column(Float)
    photo_url = Column(String(500))
    gps_lat = Column(Float)
    gps_lon = Column(Float)
    forecast = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class GPSTrack(Base):
    """GPS-треки техники"""
    __tablename__ = "gps_tracks"

    id = Column(Integer, primary_key=True, index=True)
    datetime = Column(DateTime, nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude_m = Column(Float)
    machine_id = Column(Integer, ForeignKey("machinery.id"))
    operation_type = Column(String(50))
    speed_kmh = Column(Float)
    heading_deg = Column(Float)
    field_id = Column(Integer, ForeignKey("fields.id"))
    created_at = Column(DateTime, server_default=func.now())


class MachineryEquipment(Base):
    """Техническая оснащенность (GPS, RTK, автопилот)"""
    __tablename__ = "machinery_equipment"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machinery.id"), nullable=False)
    has_gps = Column(Boolean, default=False)
    gps_type = Column(String(50))  # RTK/DGPS/Standard
    accuracy_cm = Column(Float)
    gps_manufacturer = Column(String(100))
    gps_model = Column(String(100))
    has_autopilot = Column(Boolean, default=False)
    rtk_station_type = Column(String(50))  # Local/Network/None
    rtk_operator = Column(String(100))
    notes = Column(Text)

    # Relationships
    machine = relationship("Machinery", back_populates="equipment")


class SatelliteData(Base):
    """Спутниковые данные (NDVI, EVI)"""
    __tablename__ = "satellite_data"

    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False)
    acquisition_date = Column(Date, nullable=False, index=True)
    satellite_source = Column(String(50))  # Sentinel-2/Landsat/PlanetScope
    ndvi_mean = Column(Float)  # -1 to 1
    ndvi_min = Column(Float)
    ndvi_max = Column(Float)
    ndvi_std = Column(Float)
    evi_mean = Column(Float)
    cloud_cover_pct = Column(Float)
    resolution_m = Column(Float)
    image_quality = Column(String(50))
    crop_stage = Column(String(100))
    notes = Column(Text)


# ============================================================================
# ДЕТАЛИ НОВЫХ ТИПОВ ОПЕРАЦИЙ
# ============================================================================

class DesiccationDetails(Base):
    """Детали десикации (предуборочное подсушивание)"""
    __tablename__ = "desiccation_details"

    id = Column(Integer, primary_key=True, index=True)
    operation_id = Column(Integer, ForeignKey("operations.id"), nullable=False, unique=True)
    product_name = Column(String(200), nullable=False)
    active_ingredient = Column(String(200))
    rate_per_ha = Column(Float)
    water_rate_l_ha = Column(Float)
    growth_stage = Column(String(100))
    target_moisture_percent = Column(Float)
    temperature_c = Column(Float)
    wind_speed_ms = Column(Float)
    humidity_percent = Column(Float)

    # Relationships
    operation = relationship("Operation", backref="desiccation_details")


class TillageDetails(Base):
    """Детали обработки почвы"""
    __tablename__ = "tillage_details"

    id = Column(Integer, primary_key=True, index=True)
    operation_id = Column(Integer, ForeignKey("operations.id"), nullable=False, unique=True)
    tillage_type = Column(String(50), nullable=False)  # plowing, cultivation, harrowing, stubble_breaking, discing, deep_loosening, rolling
    depth_cm = Column(Float)
    tillage_purpose = Column(String(50))  # pre_sowing, post_harvest, weed_control, moisture_retention, fallow

    # Relationships
    operation = relationship("Operation", backref="tillage_details")


class IrrigationDetails(Base):
    """Детали орошения"""
    __tablename__ = "irrigation_details"

    id = Column(Integer, primary_key=True, index=True)
    operation_id = Column(Integer, ForeignKey("operations.id"), nullable=False, unique=True)
    irrigation_type = Column(String(50))  # sprinkler, drip, furrow, flood, center_pivot
    water_volume_m3 = Column(Float)
    water_rate_m3_ha = Column(Float)
    water_source = Column(String(100))
    soil_moisture_before_percent = Column(Float)
    soil_moisture_after_percent = Column(Float)
    water_quality = Column(String(50))

    # Relationships
    operation = relationship("Operation", backref="irrigation_details")


class SnowRetentionDetails(Base):
    """Детали снегозадержания"""
    __tablename__ = "snow_retention_details"

    id = Column(Integer, primary_key=True, index=True)
    operation_id = Column(Integer, ForeignKey("operations.id"), nullable=False, unique=True)
    method = Column(String(50))  # snow_plowing, barriers, vegetation
    snow_depth_before_cm = Column(Float)
    snow_depth_after_cm = Column(Float)
    coverage_percent = Column(Float)

    # Relationships
    operation = relationship("Operation", backref="snow_retention_details")


class FallowDetails(Base):
    """Детали обработки паров"""
    __tablename__ = "fallow_details"

    id = Column(Integer, primary_key=True, index=True)
    operation_id = Column(Integer, ForeignKey("operations.id"), nullable=False, unique=True)
    fallow_type = Column(String(50))  # black, early, green, cultivated
    processing_depth_cm = Column(Float)
    weed_control_performed = Column(Boolean, default=False)
    purpose = Column(Text)

    # Relationships
    operation = relationship("Operation", backref="fallow_details")


# ============================================================================
# СПРАВОЧНЫЕ ТАБЛИЦЫ
# ============================================================================

class RefCrop(Base):
    """Справочник культур"""
    __tablename__ = "ref_crops"

    id = Column(Integer, primary_key=True, index=True)
    crop_name = Column(String(100), nullable=False, unique=True)
    crop_type = Column(String(50))
    typical_yield_min = Column(Float)
    typical_yield_max = Column(Float)
    seeding_rate_min = Column(Float)
    seeding_rate_max = Column(Float)
    seeding_depth_cm = Column(Float)
    row_spacing_cm = Column(Float)


class RefFertilizer(Base):
    """Справочник удобрений"""
    __tablename__ = "ref_fertilizers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    type = Column(String(50))
    n_content = Column(Float)
    p2o5_content = Column(Float)
    k2o_content = Column(Float)
    s_content = Column(Float)


class RefPesticide(Base):
    """Справочник СЗР"""
    __tablename__ = "ref_pesticides"

    id = Column(Integer, primary_key=True, index=True)
    trade_name = Column(String(100), nullable=False)
    active_ingredient = Column(String(200))
    pesticide_class = Column(String(50))
    typical_dose_min = Column(Float)
    typical_dose_max = Column(Float)
    dose_unit = Column(String(20))


# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

def init_db():
    """Инициализация базы данных"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Получение сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    print("Creating database tables...")
    init_db()
    print("Database initialized successfully!")
