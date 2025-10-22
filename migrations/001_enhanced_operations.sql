-- ============================================================================
-- МИГРАЦИЯ: Расширение функциональности операций и оборудования
-- Версия: 001
-- Дата: 2025-10-22
-- Описание: Добавление новых полей для операций, разделение техники и агрегатов,
--          новые типы операций (обработка почвы, десикация, орошение, пары, снегозадержание)
-- ============================================================================

-- ============================================================================
-- 1. СОЗДАНИЕ ТАБЛИЦ ТЕХНИКИ И АГРЕГАТОВ
-- ============================================================================

-- Таблица техники (трактора, комбайны, самоходные опрыскиватели, дроны)
CREATE TABLE IF NOT EXISTS machinery (
    id SERIAL PRIMARY KEY,
    farm_id INTEGER NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    machinery_type VARCHAR(50) NOT NULL CHECK (machinery_type IN (
        'tractor', 'combine', 'self_propelled_sprayer', 'drone', 'irrigation_system', 'other'
    )),
    brand VARCHAR(100),
    model VARCHAR(100) NOT NULL,
    year INTEGER,
    registration_number VARCHAR(50),
    engine_power_hp FLOAT,
    fuel_type VARCHAR(50) CHECK (fuel_type IN ('diesel', 'gasoline', 'electric', 'hybrid', 'gas')),
    purchase_date DATE,
    purchase_price DECIMAL(12, 2),
    current_value DECIMAL(12, 2),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'repair', 'sold', 'rented_out', 'rented_in')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_machinery_farm_model UNIQUE (farm_id, brand, model, year, registration_number)
);

CREATE INDEX idx_machinery_farm ON machinery(farm_id);
CREATE INDEX idx_machinery_type ON machinery(machinery_type);
CREATE INDEX idx_machinery_status ON machinery(status);

COMMENT ON TABLE machinery IS 'Техника хозяйства: трактора, комбайны, самоходные опрыскиватели, дроны';
COMMENT ON COLUMN machinery.machinery_type IS 'Тип техники: tractor, combine, self_propelled_sprayer, drone, irrigation_system';
COMMENT ON COLUMN machinery.status IS 'Статус: active, repair, sold, rented_out, rented_in';

-- Таблица агрегатов (сеялки, бороны, культиваторы, прицепные опрыскиватели)
CREATE TABLE IF NOT EXISTS implements (
    id SERIAL PRIMARY KEY,
    farm_id INTEGER NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    implement_type VARCHAR(50) NOT NULL CHECK (implement_type IN (
        'seeder', 'planter', 'plow', 'cultivator', 'harrow', 'disc',
        'deep_loosener', 'roller', 'sprayer_trailer', 'fertilizer_spreader',
        'stubble_breaker', 'snow_plow', 'other'
    )),
    brand VARCHAR(100),
    model VARCHAR(100) NOT NULL,
    year INTEGER,
    working_width_m FLOAT,
    purchase_date DATE,
    purchase_price DECIMAL(12, 2),
    current_value DECIMAL(12, 2),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'repair', 'sold', 'rented_out', 'rented_in')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_implement_farm_model UNIQUE (farm_id, brand, model, year)
);

CREATE INDEX idx_implements_farm ON implements(farm_id);
CREATE INDEX idx_implements_type ON implements(implement_type);
CREATE INDEX idx_implements_status ON implements(status);

COMMENT ON TABLE implements IS 'Агрегаты хозяйства: сеялки, бороны, культиваторы, прицепные опрыскиватели';
COMMENT ON COLUMN implements.implement_type IS 'Тип агрегата: seeder, planter, plow, cultivator, harrow, disc, sprayer_trailer и т.д.';

-- ============================================================================
-- 2. РАСШИРЕНИЕ ТАБЛИЦЫ OPERATIONS
-- ============================================================================

-- Добавление новых полей в таблицу operations
ALTER TABLE operations ADD COLUMN IF NOT EXISTS end_date DATE;
ALTER TABLE operations ADD COLUMN IF NOT EXISTS implement_id INTEGER REFERENCES implements(id) ON DELETE SET NULL;
ALTER TABLE operations ADD COLUMN IF NOT EXISTS machine_year INTEGER;
ALTER TABLE operations ADD COLUMN IF NOT EXISTS implement_year INTEGER;
ALTER TABLE operations ADD COLUMN IF NOT EXISTS work_speed_kmh FLOAT;

-- Обновление ссылки на технику
ALTER TABLE operations ALTER COLUMN machine_id TYPE INTEGER;
ALTER TABLE operations ADD CONSTRAINT fk_operations_machinery
    FOREIGN KEY (machine_id) REFERENCES machinery(id) ON DELETE SET NULL;

-- Индексы для новых полей
CREATE INDEX IF NOT EXISTS idx_operations_end_date ON operations(end_date);
CREATE INDEX IF NOT EXISTS idx_operations_implement ON operations(implement_id);

-- Комментарии
COMMENT ON COLUMN operations.end_date IS 'Дата окончания операции';
COMMENT ON COLUMN operations.implement_id IS 'ID агрегата из таблицы implements';
COMMENT ON COLUMN operations.machine_year IS 'Год выпуска техники';
COMMENT ON COLUMN operations.implement_year IS 'Год выпуска агрегата';
COMMENT ON COLUMN operations.work_speed_kmh IS 'Скорость работы, км/ч';

-- ============================================================================
-- 3. РАСШИРЕНИЕ ТАБЛИЦЫ SOWING_DETAILS (Посев)
-- ============================================================================

ALTER TABLE sowing_details ADD COLUMN IF NOT EXISTS seed_reproduction VARCHAR(50);
ALTER TABLE sowing_details ADD COLUMN IF NOT EXISTS seed_origin_country VARCHAR(100);
ALTER TABLE sowing_details ADD COLUMN IF NOT EXISTS combined_with_fertilizer BOOLEAN DEFAULT FALSE;
ALTER TABLE sowing_details ADD COLUMN IF NOT EXISTS combined_fertilizer_name VARCHAR(100);
ALTER TABLE sowing_details ADD COLUMN IF NOT EXISTS combined_fertilizer_rate_kg_ha FLOAT;

COMMENT ON COLUMN sowing_details.seed_reproduction IS 'Репродукция семян: элита, первая, вторая, третья и т.д.';
COMMENT ON COLUMN sowing_details.seed_origin_country IS 'Страна производства семян';
COMMENT ON COLUMN sowing_details.combined_with_fertilizer IS 'Комбинированный посев с внесением удобрений';
COMMENT ON COLUMN sowing_details.combined_fertilizer_name IS 'Название удобрения при комбинированном посеве';
COMMENT ON COLUMN sowing_details.combined_fertilizer_rate_kg_ha IS 'Норма удобрения при комбинированном посеве, кг/га';

-- ============================================================================
-- 4. НОВЫЕ ТАБЛИЦЫ ДЛЯ ДОПОЛНИТЕЛЬНЫХ ОПЕРАЦИЙ
-- ============================================================================

-- 4.1 Десикация
CREATE TABLE IF NOT EXISTS desiccation_details (
    id SERIAL PRIMARY KEY,
    operation_id INTEGER NOT NULL REFERENCES operations(id) ON DELETE CASCADE,
    product_name VARCHAR(200) NOT NULL,
    active_ingredient VARCHAR(200),
    rate_per_ha FLOAT,
    water_rate_l_ha FLOAT,
    growth_stage VARCHAR(100),
    target_moisture_percent FLOAT,
    temperature_c FLOAT,
    wind_speed_ms FLOAT,
    humidity_percent FLOAT,
    CONSTRAINT unique_desiccation_operation UNIQUE (operation_id)
);

CREATE INDEX idx_desiccation_operation ON desiccation_details(operation_id);

COMMENT ON TABLE desiccation_details IS 'Детали десикации (предуборочное подсушивание)';
COMMENT ON COLUMN desiccation_details.target_moisture_percent IS 'Целевая влажность зерна, %';

-- 4.2 Обработка почвы
CREATE TABLE IF NOT EXISTS tillage_details (
    id SERIAL PRIMARY KEY,
    operation_id INTEGER NOT NULL REFERENCES operations(id) ON DELETE CASCADE,
    tillage_type VARCHAR(50) NOT NULL CHECK (tillage_type IN (
        'plowing', 'cultivation', 'harrowing', 'stubble_breaking',
        'discing', 'deep_loosening', 'rolling'
    )),
    depth_cm FLOAT,
    tillage_purpose VARCHAR(50) CHECK (tillage_purpose IN (
        'pre_sowing', 'post_harvest', 'weed_control', 'moisture_retention', 'fallow'
    )),
    CONSTRAINT unique_tillage_operation UNIQUE (operation_id)
);

CREATE INDEX idx_tillage_operation ON tillage_details(operation_id);
CREATE INDEX idx_tillage_type ON tillage_details(tillage_type);

COMMENT ON TABLE tillage_details IS 'Детали обработки почвы';
COMMENT ON COLUMN tillage_details.tillage_type IS 'Тип обработки: вспашка, культивация, боронование, лущение, дискование, глубокорыхление, каткование';
COMMENT ON COLUMN tillage_details.depth_cm IS 'Глубина обработки, см';

-- 4.3 Орошение
CREATE TABLE IF NOT EXISTS irrigation_details (
    id SERIAL PRIMARY KEY,
    operation_id INTEGER NOT NULL REFERENCES operations(id) ON DELETE CASCADE,
    irrigation_type VARCHAR(50) CHECK (irrigation_type IN (
        'sprinkler', 'drip', 'furrow', 'flood', 'center_pivot'
    )),
    water_volume_m3 FLOAT,
    water_rate_m3_ha FLOAT,
    water_source VARCHAR(100),
    soil_moisture_before_percent FLOAT,
    soil_moisture_after_percent FLOAT,
    water_quality VARCHAR(50),
    CONSTRAINT unique_irrigation_operation UNIQUE (operation_id)
);

CREATE INDEX idx_irrigation_operation ON irrigation_details(operation_id);

COMMENT ON TABLE irrigation_details IS 'Детали орошения';
COMMENT ON COLUMN irrigation_details.irrigation_type IS 'Тип орошения: дождевание, капельное, по бороздам, затопление, круговое';
COMMENT ON COLUMN irrigation_details.water_volume_m3 IS 'Общий объем воды, м3';
COMMENT ON COLUMN irrigation_details.water_rate_m3_ha IS 'Норма полива, м3/га';

-- 4.4 Снегозадержание
CREATE TABLE IF NOT EXISTS snow_retention_details (
    id SERIAL PRIMARY KEY,
    operation_id INTEGER NOT NULL REFERENCES operations(id) ON DELETE CASCADE,
    method VARCHAR(50) CHECK (method IN ('snow_plowing', 'barriers', 'vegetation')),
    snow_depth_before_cm FLOAT,
    snow_depth_after_cm FLOAT,
    coverage_percent FLOAT,
    CONSTRAINT unique_snow_retention_operation UNIQUE (operation_id)
);

CREATE INDEX idx_snow_retention_operation ON snow_retention_details(operation_id);

COMMENT ON TABLE snow_retention_details IS 'Детали снегозадержания';
COMMENT ON COLUMN snow_retention_details.method IS 'Метод: снегопахание, барьеры, растительность';

-- 4.5 Пары
CREATE TABLE IF NOT EXISTS fallow_details (
    id SERIAL PRIMARY KEY,
    operation_id INTEGER NOT NULL REFERENCES operations(id) ON DELETE CASCADE,
    fallow_type VARCHAR(50) CHECK (fallow_type IN ('black', 'early', 'green', 'cultivated')),
    processing_depth_cm FLOAT,
    weed_control_performed BOOLEAN DEFAULT FALSE,
    purpose TEXT,
    CONSTRAINT unique_fallow_operation UNIQUE (operation_id)
);

CREATE INDEX idx_fallow_operation ON fallow_details(operation_id);

COMMENT ON TABLE fallow_details IS 'Детали обработки паров';
COMMENT ON COLUMN fallow_details.fallow_type IS 'Тип пара: черный, ранний, зеленый, обрабатываемый';

-- ============================================================================
-- 5. РАСШИРЕНИЕ ТАБЛИЦЫ ECONOMIC_DATA (Аренда)
-- ============================================================================

ALTER TABLE economic_data ADD COLUMN IF NOT EXISTS field_rental_cost DECIMAL(12, 2);
ALTER TABLE economic_data ADD COLUMN IF NOT EXISTS field_rental_period VARCHAR(50);
ALTER TABLE economic_data ADD COLUMN IF NOT EXISTS machinery_rental_cost DECIMAL(12, 2);
ALTER TABLE economic_data ADD COLUMN IF NOT EXISTS machinery_rental_type VARCHAR(50);
ALTER TABLE economic_data ADD COLUMN IF NOT EXISTS rented_machinery_description TEXT;

COMMENT ON COLUMN economic_data.field_rental_cost IS 'Стоимость аренды поля';
COMMENT ON COLUMN economic_data.field_rental_period IS 'Период аренды: сезон, год, месяц';
COMMENT ON COLUMN economic_data.machinery_rental_cost IS 'Стоимость аренды техники';
COMMENT ON COLUMN economic_data.machinery_rental_type IS 'Тип аренды техники: почасовая, посменная, посезонная';

-- ============================================================================
-- 6. ОБНОВЛЕНИЕ OPERATION_TYPE
-- ============================================================================

-- Добавление новых типов операций (если используется CHECK constraint)
-- Если CHECK уже существует, нужно его пересоздать
ALTER TABLE operations DROP CONSTRAINT IF EXISTS operations_operation_type_check;

ALTER TABLE operations ADD CONSTRAINT operations_operation_type_check CHECK (
    operation_type IN (
        'sowing', 'fertilizing', 'spraying', 'harvest', 'soil_analysis',
        'desiccation', 'tillage', 'irrigation', 'snow_retention', 'fallow'
    )
);

-- ============================================================================
-- 7. ТРИГГЕРЫ ДЛЯ АВТОМАТИЧЕСКОГО ОБНОВЛЕНИЯ UPDATED_AT
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггеры для новых таблиц
DROP TRIGGER IF EXISTS update_machinery_updated_at ON machinery;
CREATE TRIGGER update_machinery_updated_at
    BEFORE UPDATE ON machinery
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_implements_updated_at ON implements;
CREATE TRIGGER update_implements_updated_at
    BEFORE UPDATE ON implements
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 8. ПРЕДСТАВЛЕНИЯ ДЛЯ УДОБСТВА РАБОТЫ
-- ============================================================================

-- Полное представление операций с деталями техники
CREATE OR REPLACE VIEW operations_with_equipment AS
SELECT
    o.*,
    m.brand as machine_brand,
    m.model as machine_model,
    m.machinery_type,
    i.brand as implement_brand,
    i.model as implement_model,
    i.implement_type,
    f.name as field_name,
    f.field_code
FROM operations o
LEFT JOIN machinery m ON o.machine_id = m.id
LEFT JOIN implements i ON o.implement_id = i.id
LEFT JOIN fields f ON o.field_id = f.id;

COMMENT ON VIEW operations_with_equipment IS 'Операции с информацией о технике и агрегатах';

-- Активная техника хозяйства
CREATE OR REPLACE VIEW active_equipment AS
SELECT
    farm_id,
    'machinery' as equipment_type,
    machinery_type as type,
    brand,
    model,
    year,
    status
FROM machinery
WHERE status = 'active'
UNION ALL
SELECT
    farm_id,
    'implement' as equipment_type,
    implement_type as type,
    brand,
    model,
    year,
    status
FROM implements
WHERE status = 'active';

COMMENT ON VIEW active_equipment IS 'Вся активная техника и агрегаты';

-- ============================================================================
-- 9. ДАННЫЕ ПО УМОЛЧАНИЮ (СПРАВОЧНИКИ)
-- ============================================================================

-- Можно добавить начальные данные для справочников, если нужно

-- ============================================================================
-- ЗАВЕРШЕНИЕ МИГРАЦИИ
-- ============================================================================

-- Проверка результатов
DO $$
BEGIN
    RAISE NOTICE 'Миграция 001_enhanced_operations.sql успешно выполнена';
    RAISE NOTICE 'Создано таблиц: machinery, implements, desiccation_details, tillage_details, irrigation_details, snow_retention_details, fallow_details';
    RAISE NOTICE 'Обновлено таблиц: operations, sowing_details, economic_data';
    RAISE NOTICE 'Создано представлений: operations_with_equipment, active_equipment';
END $$;
