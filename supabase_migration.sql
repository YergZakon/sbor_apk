-- ============================================================================
-- SUPABASE MIGRATION SCRIPT
-- Farm Data System - PostgreSQL Schema
-- ============================================================================

-- Этот скрипт создает все таблицы, индексы, ограничения и триггеры
-- для работы системы в Supabase (PostgreSQL)

-- ============================================================================
-- 1. ФУНКЦИИ И ТРИГГЕРЫ
-- ============================================================================

-- Функция для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 2. ТАБЛИЦЫ АУТЕНТИФИКАЦИИ
-- ============================================================================

-- Пользователи
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(200),
    role VARCHAR(20) NOT NULL DEFAULT 'farmer' CHECK (role IN ('admin', 'farmer', 'viewer')),
    is_active BOOLEAN DEFAULT TRUE,
    farm_id INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_farm ON users(farm_id) WHERE farm_id IS NOT NULL;

-- Журнал аудита
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INTEGER,
    details TEXT,
    ip_address VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_created ON audit_logs(created_at);

-- ============================================================================
-- 3. ОСНОВНЫЕ ТАБЛИЦЫ
-- ============================================================================

-- Хозяйства
CREATE TABLE IF NOT EXISTS farms (
    id SERIAL PRIMARY KEY,
    bin VARCHAR(12) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    director_name VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    region VARCHAR(100),
    district VARCHAR(100),
    village VARCHAR(100),
    farm_type VARCHAR(50),
    founded_year INTEGER,
    total_area_ha NUMERIC(10,2),
    arable_area_ha NUMERIC(10,2),
    fallow_area_ha NUMERIC(10,2),
    pasture_area_ha NUMERIC(10,2),
    hayfield_area_ha NUMERIC(10,2),
    center_lat DOUBLE PRECISION,
    center_lon DOUBLE PRECISION,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT check_bin_length CHECK (char_length(bin) = 12),
    CONSTRAINT check_areas CHECK (
        total_area_ha >= 0 AND
        arable_area_ha >= 0 AND
        COALESCE(arable_area_ha, 0) <= COALESCE(total_area_ha, 0)
    )
);

CREATE INDEX idx_farms_bin ON farms(bin);
CREATE INDEX idx_farms_region ON farms(region);

-- Поля
CREATE TABLE IF NOT EXISTS fields (
    id SERIAL PRIMARY KEY,
    farm_id INTEGER NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    field_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100),
    cadastral_number VARCHAR(50),
    area_ha NUMERIC(10,2) NOT NULL CHECK (area_ha > 0),
    center_lat DOUBLE PRECISION,
    center_lon DOUBLE PRECISION,
    soil_type VARCHAR(100),
    soil_texture VARCHAR(50),
    ph_water NUMERIC(4,2),
    humus_pct NUMERIC(5,2),
    p2o5_mg_kg NUMERIC(10,2),
    k2o_mg_kg NUMERIC(10,2),
    relief VARCHAR(50),
    slope_degree NUMERIC(5,2),
    drainage VARCHAR(50),
    last_analysis_year INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_fields_farm ON fields(farm_id);
CREATE INDEX idx_fields_code ON fields(field_code);

-- Операции
CREATE TABLE IF NOT EXISTS operations (
    id SERIAL PRIMARY KEY,
    farm_id INTEGER NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    field_id INTEGER NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    operation_type VARCHAR(50) NOT NULL CHECK (
        operation_type IN ('sowing', 'fertilizing', 'spraying', 'harvest', 'soil_analysis', 'tillage', 'other')
    ),
    operation_date DATE NOT NULL,
    crop VARCHAR(100),
    variety VARCHAR(100),
    area_processed_ha NUMERIC(10,2),
    machine_id INTEGER,
    operator VARCHAR(100),
    weather_conditions TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_operations_farm ON operations(farm_id);
CREATE INDEX idx_operations_field ON operations(field_id);
CREATE INDEX idx_operations_date ON operations(operation_date);
CREATE INDEX idx_operations_farm_date ON operations(farm_id, operation_date);

-- Детали посева
CREATE TABLE IF NOT EXISTS sowing_details (
    id SERIAL PRIMARY KEY,
    operation_id INTEGER UNIQUE NOT NULL REFERENCES operations(id) ON DELETE CASCADE,
    crop VARCHAR(100) NOT NULL,
    variety VARCHAR(100),
    seeding_rate_kg_ha NUMERIC(10,2),
    seeding_depth_cm NUMERIC(5,2),
    row_spacing_cm NUMERIC(5,2),
    seed_treatment VARCHAR(100),
    soil_temp_c NUMERIC(5,2),
    soil_moisture_percent NUMERIC(5,2),
    total_seeds_kg NUMERIC(10,2)
);

CREATE INDEX idx_sowing_operation ON sowing_details(operation_id);

-- Внесение удобрений
CREATE TABLE IF NOT EXISTS fertilizer_applications (
    id SERIAL PRIMARY KEY,
    operation_id INTEGER NOT NULL REFERENCES operations(id) ON DELETE CASCADE,
    fertilizer_name VARCHAR(100) NOT NULL,
    fertilizer_type VARCHAR(50),
    rate_kg_ha NUMERIC(10,2),
    total_fertilizer_kg NUMERIC(10,2),
    n_content_percent NUMERIC(5,2),
    p_content_percent NUMERIC(5,2),
    k_content_percent NUMERIC(5,2),
    n_applied_kg NUMERIC(10,2),
    p_applied_kg NUMERIC(10,2),
    k_applied_kg NUMERIC(10,2),
    application_method VARCHAR(50),
    application_purpose VARCHAR(50)
);

CREATE INDEX idx_fertilizer_operation ON fertilizer_applications(operation_id);

-- Применение СЗР
CREATE TABLE IF NOT EXISTS pesticide_applications (
    id SERIAL PRIMARY KEY,
    operation_id INTEGER NOT NULL REFERENCES operations(id) ON DELETE CASCADE,
    pesticide_name VARCHAR(100) NOT NULL,
    pesticide_class VARCHAR(50),
    active_ingredient VARCHAR(200),
    rate_per_ha NUMERIC(10,2),
    total_product_used NUMERIC(10,2),
    water_rate_l_ha NUMERIC(10,2),
    application_method VARCHAR(50),
    treatment_target VARCHAR(100),
    growth_stage VARCHAR(100),
    temperature_c NUMERIC(5,2),
    wind_speed_ms NUMERIC(5,2),
    humidity_percent NUMERIC(5,2),
    waiting_period_days INTEGER
);

CREATE INDEX idx_pesticide_operation ON pesticide_applications(operation_id);

-- Данные уборки
CREATE TABLE IF NOT EXISTS harvest_data (
    id SERIAL PRIMARY KEY,
    operation_id INTEGER UNIQUE NOT NULL REFERENCES operations(id) ON DELETE CASCADE,
    crop VARCHAR(100),
    variety VARCHAR(100),
    yield_t_ha NUMERIC(10,2),
    total_yield_t NUMERIC(10,2),
    moisture_percent NUMERIC(5,2),
    protein_percent NUMERIC(5,2),
    gluten_percent NUMERIC(5,2),
    test_weight_g_l NUMERIC(10,2),
    falling_number INTEGER,
    weed_content_percent NUMERIC(5,2),
    oil_content_percent NUMERIC(5,2),
    quality_class INTEGER CHECK (quality_class BETWEEN 1 AND 5)
);

CREATE INDEX idx_harvest_operation ON harvest_data(operation_id);

-- Агрохимические анализы
CREATE TABLE IF NOT EXISTS agrochemical_analyses (
    id SERIAL PRIMARY KEY,
    operation_id INTEGER UNIQUE NOT NULL REFERENCES operations(id) ON DELETE CASCADE,
    sample_depth_cm INTEGER,
    sample_location VARCHAR(100),
    ph_water NUMERIC(4,2),
    ph_salt NUMERIC(4,2),
    humus_percent NUMERIC(5,2),
    nitrogen_total_percent NUMERIC(5,2),
    p2o5_mg_kg NUMERIC(10,2),
    k2o_mg_kg NUMERIC(10,2),
    mobile_s_mg_kg NUMERIC(10,2),
    no3_mg_kg NUMERIC(10,2),
    nh4_mg_kg NUMERIC(10,2),
    ec_ds_m NUMERIC(10,2),
    cec_cmol_kg NUMERIC(10,2),
    ca_mg_kg NUMERIC(10,2),
    mg_mg_kg NUMERIC(10,2),
    na_mg_kg NUMERIC(10,2),
    zn_mg_kg NUMERIC(10,2),
    cu_mg_kg NUMERIC(10,2),
    fe_mg_kg NUMERIC(10,2),
    mn_mg_kg NUMERIC(10,2),
    b_mg_kg NUMERIC(10,2),
    sand_pct NUMERIC(5,2),
    silt_pct NUMERIC(5,2),
    clay_pct NUMERIC(5,2),
    lab_name VARCHAR(200),
    analysis_method VARCHAR(100),
    notes TEXT
);

CREATE INDEX idx_agrochem_operation ON agrochemical_analyses(operation_id);

-- Экономические данные
CREATE TABLE IF NOT EXISTS economic_data (
    id SERIAL PRIMARY KEY,
    field_id INTEGER NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    crop VARCHAR(100),
    area_ha NUMERIC(10,2),
    seeds_cost_kzt_ha NUMERIC(12,2),
    fertilizers_cost_kzt_ha NUMERIC(12,2),
    pesticides_cost_kzt_ha NUMERIC(12,2),
    fuel_cost_kzt_ha NUMERIC(12,2),
    labor_cost_kzt_ha NUMERIC(12,2),
    other_costs_kzt_ha NUMERIC(12,2),
    total_costs_kzt_ha NUMERIC(12,2),
    yield_t_ha NUMERIC(10,2),
    selling_price_kzt_t NUMERIC(12,2),
    revenue_kzt_ha NUMERIC(12,2),
    profit_kzt_ha NUMERIC(12,2),
    profitability_pct NUMERIC(6,2),
    notes TEXT,
    CONSTRAINT uk_economic_data UNIQUE (field_id, year, crop)
);

CREATE INDEX idx_economic_field ON economic_data(field_id);
CREATE INDEX idx_economic_year ON economic_data(year);

-- Метеоданные
CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL PRIMARY KEY,
    farm_id INTEGER REFERENCES farms(id) ON DELETE CASCADE,
    datetime TIMESTAMPTZ NOT NULL,
    temp_air_c NUMERIC(5,2),
    temp_min_c NUMERIC(5,2),
    temp_max_c NUMERIC(5,2),
    precipitation_mm NUMERIC(10,2),
    humidity_pct NUMERIC(5,2),
    wind_speed_ms NUMERIC(5,2),
    wind_direction VARCHAR(20),
    solar_radiation_wm2 NUMERIC(10,2),
    pressure_hpa NUMERIC(10,2),
    temp_soil_5cm_c NUMERIC(5,2),
    temp_soil_10cm_c NUMERIC(5,2),
    soil_moisture_pct NUMERIC(5,2),
    evapotranspiration_mm NUMERIC(10,2),
    notes TEXT,
    CONSTRAINT uk_weather_data UNIQUE (farm_id, datetime)
);

CREATE INDEX idx_weather_farm ON weather_data(farm_id);
CREATE INDEX idx_weather_datetime ON weather_data(datetime);

-- Техника
CREATE TABLE IF NOT EXISTS machinery (
    id SERIAL PRIMARY KEY,
    farm_id INTEGER NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    machine_type VARCHAR(100),
    brand VARCHAR(100),
    model VARCHAR(100),
    year INTEGER,
    registration_number VARCHAR(50),
    status VARCHAR(50),
    notes TEXT
);

CREATE INDEX idx_machinery_farm ON machinery(farm_id);

-- ============================================================================
-- 4. РАСШИРЕННЫЕ ТАБЛИЦЫ
-- ============================================================================

-- Фитосанитарный мониторинг
CREATE TABLE IF NOT EXISTS phytosanitary_monitoring (
    id SERIAL PRIMARY KEY,
    field_id INTEGER NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    inspection_date DATE NOT NULL,
    pest_type VARCHAR(50) NOT NULL CHECK (pest_type IN ('disease', 'pest', 'weed')),
    pest_name VARCHAR(200) NOT NULL,
    latin_name VARCHAR(200),
    severity_pct NUMERIC(5,2) CHECK (severity_pct BETWEEN 0 AND 100),
    prevalence_pct NUMERIC(5,2) CHECK (prevalence_pct BETWEEN 0 AND 100),
    intensity_score INTEGER CHECK (intensity_score BETWEEN 1 AND 5),
    threshold_exceeded BOOLEAN,
    crop_stage VARCHAR(100),
    control_measures TEXT,
    control_effectiveness_pct NUMERIC(5,2),
    photo_url VARCHAR(500),
    gps_lat DOUBLE PRECISION,
    gps_lon DOUBLE PRECISION,
    forecast TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_phyto_field ON phytosanitary_monitoring(field_id);
CREATE INDEX idx_phyto_date ON phytosanitary_monitoring(inspection_date);

-- GPS-треки
CREATE TABLE IF NOT EXISTS gps_tracks (
    id SERIAL PRIMARY KEY,
    datetime TIMESTAMPTZ NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    altitude_m NUMERIC(10,2),
    machine_id INTEGER REFERENCES machinery(id) ON DELETE CASCADE,
    operation_type VARCHAR(50),
    speed_kmh NUMERIC(5,2),
    heading_deg NUMERIC(5,2),
    field_id INTEGER REFERENCES fields(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_gps_datetime ON gps_tracks(datetime);
CREATE INDEX idx_gps_machine ON gps_tracks(machine_id, datetime);

-- Техническая оснащенность
CREATE TABLE IF NOT EXISTS machinery_equipment (
    id SERIAL PRIMARY KEY,
    machine_id INTEGER UNIQUE NOT NULL REFERENCES machinery(id) ON DELETE CASCADE,
    has_gps BOOLEAN DEFAULT FALSE,
    gps_type VARCHAR(50),
    accuracy_cm NUMERIC(5,2),
    gps_manufacturer VARCHAR(100),
    gps_model VARCHAR(100),
    has_autopilot BOOLEAN DEFAULT FALSE,
    rtk_station_type VARCHAR(50),
    rtk_operator VARCHAR(100),
    notes TEXT
);

CREATE INDEX idx_equipment_machine ON machinery_equipment(machine_id);

-- Спутниковые данные
CREATE TABLE IF NOT EXISTS satellite_data (
    id SERIAL PRIMARY KEY,
    field_id INTEGER NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    acquisition_date DATE NOT NULL,
    satellite_source VARCHAR(50),
    ndvi_mean NUMERIC(4,3) CHECK (ndvi_mean BETWEEN -1 AND 1),
    ndvi_min NUMERIC(4,3),
    ndvi_max NUMERIC(4,3),
    ndvi_std NUMERIC(4,3),
    evi_mean NUMERIC(4,3),
    cloud_cover_pct NUMERIC(5,2),
    resolution_m NUMERIC(5,2),
    image_quality VARCHAR(50),
    crop_stage VARCHAR(100),
    notes TEXT,
    CONSTRAINT uk_satellite_data UNIQUE (field_id, acquisition_date, satellite_source)
);

CREATE INDEX idx_satellite_field ON satellite_data(field_id);
CREATE INDEX idx_satellite_date ON satellite_data(acquisition_date);

-- ============================================================================
-- 5. СПРАВОЧНЫЕ ТАБЛИЦЫ
-- ============================================================================

-- Справочник культур
CREATE TABLE IF NOT EXISTS ref_crops (
    id SERIAL PRIMARY KEY,
    crop_name VARCHAR(100) UNIQUE NOT NULL,
    crop_type VARCHAR(50),
    typical_yield_min NUMERIC(10,2),
    typical_yield_max NUMERIC(10,2),
    seeding_rate_min NUMERIC(10,2),
    seeding_rate_max NUMERIC(10,2),
    seeding_depth_cm NUMERIC(5,2),
    row_spacing_cm NUMERIC(5,2)
);

-- Справочник удобрений
CREATE TABLE IF NOT EXISTS ref_fertilizers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    type VARCHAR(50),
    n_content NUMERIC(5,2),
    p2o5_content NUMERIC(5,2),
    k2o_content NUMERIC(5,2),
    s_content NUMERIC(5,2)
);

-- Справочник СЗР
CREATE TABLE IF NOT EXISTS ref_pesticides (
    id SERIAL PRIMARY KEY,
    trade_name VARCHAR(100) UNIQUE NOT NULL,
    active_ingredient VARCHAR(200),
    pesticide_class VARCHAR(50),
    typical_dose_min NUMERIC(10,2),
    typical_dose_max NUMERIC(10,2),
    dose_unit VARCHAR(20)
);

-- ============================================================================
-- 6. ВНЕШНИЙ КЛЮЧ users.farm_id (добавляется после создания farms)
-- ============================================================================

ALTER TABLE users
ADD CONSTRAINT fk_users_farm
FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE SET NULL;

-- ============================================================================
-- 7. ТРИГГЕРЫ ДЛЯ updated_at
-- ============================================================================

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_farms_updated_at
    BEFORE UPDATE ON farms
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 8. ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Включаем RLS для всех таблиц
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE farms ENABLE ROW LEVEL SECURITY;
ALTER TABLE fields ENABLE ROW LEVEL SECURITY;
ALTER TABLE operations ENABLE ROW LEVEL SECURITY;
ALTER TABLE sowing_details ENABLE ROW LEVEL SECURITY;
ALTER TABLE fertilizer_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE pesticide_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE harvest_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE agrochemical_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE economic_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE weather_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE machinery ENABLE ROW LEVEL SECURITY;
ALTER TABLE phytosanitary_monitoring ENABLE ROW LEVEL SECURITY;
ALTER TABLE gps_tracks ENABLE ROW LEVEL SECURITY;
ALTER TABLE machinery_equipment ENABLE ROW LEVEL SECURITY;
ALTER TABLE satellite_data ENABLE ROW LEVEL SECURITY;

-- Политики для администраторов (видят все)
CREATE POLICY admin_all_farms ON farms
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid()::integer
            AND users.role = 'admin'
        )
    );

-- Политики для фермеров (видят только свое хозяйство)
CREATE POLICY farmer_own_farm ON farms
    FOR SELECT USING (
        id = (
            SELECT farm_id FROM users WHERE users.id = auth.uid()::integer
        )
    );

-- Аналогичные политики для других таблиц
CREATE POLICY admin_all_fields ON fields
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid()::integer
            AND users.role = 'admin'
        )
    );

CREATE POLICY farmer_own_fields ON fields
    FOR SELECT USING (
        farm_id = (
            SELECT farm_id FROM users WHERE users.id = auth.uid()::integer
        )
    );

-- ============================================================================
-- 9. ПРЕДСТАВЛЕНИЯ (VIEWS) ДЛЯ УДОБСТВА
-- ============================================================================

-- Представление для полной информации о полях с хозяйством
CREATE OR REPLACE VIEW v_fields_with_farms AS
SELECT
    f.id,
    f.field_code,
    f.name AS field_name,
    f.area_ha,
    f.farm_id,
    fm.name AS farm_name,
    fm.bin AS farm_bin,
    fm.region,
    fm.district
FROM fields f
JOIN farms fm ON f.farm_id = fm.id;

-- Представление для операций с деталями
CREATE OR REPLACE VIEW v_operations_summary AS
SELECT
    o.id,
    o.operation_date,
    o.operation_type,
    o.crop,
    f.field_code,
    f.name AS field_name,
    fm.name AS farm_name,
    o.area_processed_ha
FROM operations o
JOIN fields f ON o.field_id = f.id
JOIN farms fm ON o.farm_id = fm.id;

-- ============================================================================
-- 10. КОММЕНТАРИИ К ТАБЛИЦАМ (для документации)
-- ============================================================================

COMMENT ON TABLE users IS 'Пользователи системы (фермеры, администраторы, просмотрщики)';
COMMENT ON TABLE farms IS 'Хозяйства (фермы) - центральная таблица системы';
COMMENT ON TABLE fields IS 'Поля хозяйств с почвенными характеристиками';
COMMENT ON TABLE operations IS 'Сельскохозяйственные операции (посев, обработка, уборка)';
COMMENT ON TABLE audit_logs IS 'Журнал аудита всех действий пользователей';

-- ============================================================================
-- СКРИПТ ЗАВЕРШЕН
-- ============================================================================

-- Для применения этого скрипта в Supabase:
-- 1. Зайдите в Supabase Dashboard
-- 2. Перейдите в SQL Editor
-- 3. Скопируйте и выполните этот скрипт
-- 4. Проверьте создание таблиц в Table Editor
-- 5. Обновите DATABASE_URL в вашем .env файле
