-- ============================================================================
-- SUPABASE DATABASE IMPROVEMENTS
-- Скрипт для добавления недостающих ограничений, индексов и улучшений
-- ============================================================================

-- Этот скрипт добавляет:
-- 1. Уникальные ключи (UNIQUE constraints)
-- 2. Составные уникальные ключи для предотвращения дубликатов
-- 3. Индексы для производительности
-- 4. CHECK constraints для валидации данных
-- 5. Триггеры для автоматического обновления updated_at

-- ============================================================================
-- 1. ДОБАВЛЕНИЕ УНИКАЛЬНЫХ КЛЮЧЕЙ
-- ============================================================================

-- КРИТИЧЕСКИ ВАЖНО: БИН должен быть уникальным!
ALTER TABLE farms
ADD CONSTRAINT farms_bin_unique UNIQUE (bin);

-- Уникальность username и email
ALTER TABLE users
ADD CONSTRAINT users_username_unique UNIQUE (username);

ALTER TABLE users
ADD CONSTRAINT users_email_unique UNIQUE (email);

-- Уникальность кода поля
ALTER TABLE fields
ADD CONSTRAINT fields_field_code_unique UNIQUE (field_code);

-- ============================================================================
-- 2. СОСТАВНЫЕ УНИКАЛЬНЫЕ КЛЮЧИ (предотвращение дубликатов)
-- ============================================================================

-- Экономические данные: одна запись на поле/год/культуру
ALTER TABLE economic_data
ADD CONSTRAINT uk_economic_data UNIQUE (field_id, year, crop);

-- Погодные данные: одна запись на хозяйство/время
ALTER TABLE weather_data
ADD CONSTRAINT uk_weather_data UNIQUE (farm_id, datetime);

-- Спутниковые данные: одна запись на поле/дату/источник
ALTER TABLE satellite_data
ADD CONSTRAINT uk_satellite_data UNIQUE (field_id, acquisition_date, satellite_source);

-- ONE-TO-ONE связь: одна техническая оснащенность на машину
ALTER TABLE machinery_equipment
ADD CONSTRAINT uk_machinery_equipment UNIQUE (machine_id);

-- ONE-TO-ONE связь: одна операция посева
ALTER TABLE sowing_details
ADD CONSTRAINT uk_sowing_operation UNIQUE (operation_id);

-- ONE-TO-ONE связь: одна операция уборки
ALTER TABLE harvest_data
ADD CONSTRAINT uk_harvest_operation UNIQUE (operation_id);

-- ONE-TO-ONE связь: один агрохимический анализ на операцию
ALTER TABLE agrochemical_analyses
ADD CONSTRAINT uk_agrochem_operation UNIQUE (operation_id);

-- ============================================================================
-- 3. ИНДЕКСЫ ДЛЯ ПРОИЗВОДИТЕЛЬНОСТИ
-- ============================================================================

-- Индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_users_farm ON users(farm_id) WHERE farm_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

CREATE INDEX IF NOT EXISTS idx_farms_bin ON farms(bin);
CREATE INDEX IF NOT EXISTS idx_farms_region ON farms(region);

CREATE INDEX IF NOT EXISTS idx_fields_farm ON fields(farm_id);
CREATE INDEX IF NOT EXISTS idx_fields_code ON fields(field_code);

-- Индексы для операций (частые запросы)
CREATE INDEX IF NOT EXISTS idx_operations_farm ON operations(farm_id);
CREATE INDEX IF NOT EXISTS idx_operations_field ON operations(field_id);
CREATE INDEX IF NOT EXISTS idx_operations_date ON operations(operation_date);
CREATE INDEX IF NOT EXISTS idx_operations_farm_date ON operations(farm_id, operation_date);
CREATE INDEX IF NOT EXISTS idx_operations_type ON operations(operation_type);

-- Индексы для связанных таблиц операций
CREATE INDEX IF NOT EXISTS idx_sowing_operation ON sowing_details(operation_id);
CREATE INDEX IF NOT EXISTS idx_fertilizer_operation ON fertilizer_applications(operation_id);
CREATE INDEX IF NOT EXISTS idx_pesticide_operation ON pesticide_applications(operation_id);
CREATE INDEX IF NOT EXISTS idx_harvest_operation ON harvest_data(operation_id);
CREATE INDEX IF NOT EXISTS idx_agrochem_operation ON agrochemical_analyses(operation_id);

-- Индексы для экономических и погодных данных
CREATE INDEX IF NOT EXISTS idx_economic_field ON economic_data(field_id);
CREATE INDEX IF NOT EXISTS idx_economic_year ON economic_data(year);

CREATE INDEX IF NOT EXISTS idx_weather_farm ON weather_data(farm_id);
CREATE INDEX IF NOT EXISTS idx_weather_datetime ON weather_data(datetime);

-- Индексы для GPS-треков (большая таблица)
CREATE INDEX IF NOT EXISTS idx_gps_datetime ON gps_tracks(datetime);
CREATE INDEX IF NOT EXISTS idx_gps_machine_datetime ON gps_tracks(machine_id, datetime);
CREATE INDEX IF NOT EXISTS idx_gps_field ON gps_tracks(field_id) WHERE field_id IS NOT NULL;

-- Индексы для фитосанитарного мониторинга
CREATE INDEX IF NOT EXISTS idx_phyto_field ON phytosanitary_monitoring(field_id);
CREATE INDEX IF NOT EXISTS idx_phyto_date ON phytosanitary_monitoring(inspection_date);
CREATE INDEX IF NOT EXISTS idx_phyto_type ON phytosanitary_monitoring(pest_type);

-- Индексы для спутниковых данных
CREATE INDEX IF NOT EXISTS idx_satellite_field ON satellite_data(field_id);
CREATE INDEX IF NOT EXISTS idx_satellite_date ON satellite_data(acquisition_date);

-- Индексы для техники
CREATE INDEX IF NOT EXISTS idx_machinery_farm ON machinery(farm_id);
CREATE INDEX IF NOT EXISTS idx_equipment_machine ON machinery_equipment(machine_id);

-- Индексы для аудита
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_logs(entity_type, entity_id);

-- ============================================================================
-- 4. CHECK CONSTRAINTS (валидация данных)
-- ============================================================================

-- Валидация БИН (12 цифр)
ALTER TABLE farms
ADD CONSTRAINT check_bin_length CHECK (char_length(bin) = 12);

-- Валидация площадей
ALTER TABLE farms
ADD CONSTRAINT check_farms_areas CHECK (
    total_area_ha >= 0 AND
    arable_area_ha >= 0 AND
    COALESCE(arable_area_ha, 0) <= COALESCE(total_area_ha, 0)
);

ALTER TABLE fields
ADD CONSTRAINT check_field_area CHECK (area_ha > 0);

-- Валидация роли пользователя
ALTER TABLE users
ADD CONSTRAINT check_user_role CHECK (role IN ('admin', 'farmer', 'viewer'));

-- Валидация типа операции
ALTER TABLE operations
ADD CONSTRAINT check_operation_type CHECK (
    operation_type IN ('sowing', 'fertilizing', 'spraying', 'harvest', 'soil_analysis', 'tillage', 'other')
);

-- Валидация типа вредителя
ALTER TABLE phytosanitary_monitoring
ADD CONSTRAINT check_pest_type CHECK (pest_type IN ('disease', 'pest', 'weed'));

-- Валидация процентов (0-100)
ALTER TABLE phytosanitary_monitoring
ADD CONSTRAINT check_severity CHECK (severity_pct BETWEEN 0 AND 100);

ALTER TABLE phytosanitary_monitoring
ADD CONSTRAINT check_prevalence CHECK (prevalence_pct BETWEEN 0 AND 100);

-- Валидация интенсивности (1-5 баллов)
ALTER TABLE phytosanitary_monitoring
ADD CONSTRAINT check_intensity CHECK (intensity_score BETWEEN 1 AND 5);

-- Валидация класса качества (1-5)
ALTER TABLE harvest_data
ADD CONSTRAINT check_quality_class CHECK (quality_class BETWEEN 1 AND 5);

-- Валидация NDVI (-1 to 1)
ALTER TABLE satellite_data
ADD CONSTRAINT check_ndvi_mean CHECK (ndvi_mean BETWEEN -1 AND 1);

-- ============================================================================
-- 5. ФУНКЦИИ И ТРИГГЕРЫ ДЛЯ updated_at
-- ============================================================================

-- Функция для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггеры для таблиц с updated_at
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_farms_updated_at ON farms;
CREATE TRIGGER update_farms_updated_at
    BEFORE UPDATE ON farms
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 6. CASCADE DELETE (каскадное удаление)
-- ============================================================================

-- Убедимся, что внешние ключи настроены правильно с CASCADE DELETE

-- Users -> Farms (SET NULL при удалении хозяйства)
ALTER TABLE users
DROP CONSTRAINT IF EXISTS users_farm_id_fkey,
ADD CONSTRAINT users_farm_id_fkey
    FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE SET NULL;

-- Fields -> Farms (CASCADE при удалении хозяйства)
ALTER TABLE fields
DROP CONSTRAINT IF EXISTS fields_farm_id_fkey,
ADD CONSTRAINT fields_farm_id_fkey
    FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE;

-- Operations -> Farms (CASCADE)
ALTER TABLE operations
DROP CONSTRAINT IF EXISTS operations_farm_id_fkey,
ADD CONSTRAINT operations_farm_id_fkey
    FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE;

-- Operations -> Fields (CASCADE)
ALTER TABLE operations
DROP CONSTRAINT IF EXISTS operations_field_id_fkey,
ADD CONSTRAINT operations_field_id_fkey
    FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE CASCADE;

-- Sowing details -> Operations (CASCADE)
ALTER TABLE sowing_details
DROP CONSTRAINT IF EXISTS sowing_details_operation_id_fkey,
ADD CONSTRAINT sowing_details_operation_id_fkey
    FOREIGN KEY (operation_id) REFERENCES operations(id) ON DELETE CASCADE;

-- Fertilizer applications -> Operations (CASCADE)
ALTER TABLE fertilizer_applications
DROP CONSTRAINT IF EXISTS fertilizer_applications_operation_id_fkey,
ADD CONSTRAINT fertilizer_applications_operation_id_fkey
    FOREIGN KEY (operation_id) REFERENCES operations(id) ON DELETE CASCADE;

-- Pesticide applications -> Operations (CASCADE)
ALTER TABLE pesticide_applications
DROP CONSTRAINT IF EXISTS pesticide_applications_operation_id_fkey,
ADD CONSTRAINT pesticide_applications_operation_id_fkey
    FOREIGN KEY (operation_id) REFERENCES operations(id) ON DELETE CASCADE;

-- Harvest data -> Operations (CASCADE)
ALTER TABLE harvest_data
DROP CONSTRAINT IF EXISTS harvest_data_operation_id_fkey,
ADD CONSTRAINT harvest_data_operation_id_fkey
    FOREIGN KEY (operation_id) REFERENCES operations(id) ON DELETE CASCADE;

-- Agrochemical analyses -> Operations (CASCADE)
ALTER TABLE agrochemical_analyses
DROP CONSTRAINT IF EXISTS agrochemical_analyses_operation_id_fkey,
ADD CONSTRAINT agrochemical_analyses_operation_id_fkey
    FOREIGN KEY (operation_id) REFERENCES operations(id) ON DELETE CASCADE;

-- Economic data -> Fields (CASCADE)
ALTER TABLE economic_data
DROP CONSTRAINT IF EXISTS economic_data_field_id_fkey,
ADD CONSTRAINT economic_data_field_id_fkey
    FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE CASCADE;

-- Weather data -> Farms (CASCADE)
ALTER TABLE weather_data
DROP CONSTRAINT IF EXISTS weather_data_farm_id_fkey,
ADD CONSTRAINT weather_data_farm_id_fkey
    FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE;

-- Machinery -> Farms (CASCADE)
ALTER TABLE machinery
DROP CONSTRAINT IF EXISTS machinery_farm_id_fkey,
ADD CONSTRAINT machinery_farm_id_fkey
    FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE;

-- Machinery equipment -> Machinery (CASCADE)
ALTER TABLE machinery_equipment
DROP CONSTRAINT IF EXISTS machinery_equipment_machine_id_fkey,
ADD CONSTRAINT machinery_equipment_machine_id_fkey
    FOREIGN KEY (machine_id) REFERENCES machinery(id) ON DELETE CASCADE;

-- GPS tracks -> Machinery (CASCADE)
ALTER TABLE gps_tracks
DROP CONSTRAINT IF EXISTS gps_tracks_machine_id_fkey,
ADD CONSTRAINT gps_tracks_machine_id_fkey
    FOREIGN KEY (machine_id) REFERENCES machinery(id) ON DELETE CASCADE;

-- GPS tracks -> Fields (SET NULL)
ALTER TABLE gps_tracks
DROP CONSTRAINT IF EXISTS gps_tracks_field_id_fkey,
ADD CONSTRAINT gps_tracks_field_id_fkey
    FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE SET NULL;

-- Phytosanitary monitoring -> Fields (CASCADE)
ALTER TABLE phytosanitary_monitoring
DROP CONSTRAINT IF EXISTS phytosanitary_monitoring_field_id_fkey,
ADD CONSTRAINT phytosanitary_monitoring_field_id_fkey
    FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE CASCADE;

-- Satellite data -> Fields (CASCADE)
ALTER TABLE satellite_data
DROP CONSTRAINT IF EXISTS satellite_data_field_id_fkey,
ADD CONSTRAINT satellite_data_field_id_fkey
    FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE CASCADE;

-- Audit logs -> Users (CASCADE)
ALTER TABLE audit_logs
DROP CONSTRAINT IF EXISTS audit_logs_user_id_fkey,
ADD CONSTRAINT audit_logs_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- ============================================================================
-- 7. ПОЛЕЗНЫЕ ПРЕДСТАВЛЕНИЯ (VIEWS)
-- ============================================================================

-- Представление: Полная информация о полях с хозяйством
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
    fm.district,
    fm.village
FROM fields f
JOIN farms fm ON f.farm_id = fm.id;

-- Представление: Сводка по операциям
CREATE OR REPLACE VIEW v_operations_summary AS
SELECT
    o.id,
    o.operation_date,
    o.operation_type,
    o.crop,
    o.variety,
    o.area_processed_ha,
    f.field_code,
    f.name AS field_name,
    fm.name AS farm_name,
    fm.bin AS farm_bin
FROM operations o
JOIN fields f ON o.field_id = f.id
JOIN farms fm ON o.farm_id = fm.id
ORDER BY o.operation_date DESC;

-- Представление: Пользователи с хозяйствами
CREATE OR REPLACE VIEW v_users_with_farms AS
SELECT
    u.id,
    u.username,
    u.email,
    u.full_name,
    u.role,
    u.is_active,
    u.farm_id,
    f.name AS farm_name,
    f.bin AS farm_bin,
    f.region AS farm_region
FROM users u
LEFT JOIN farms f ON u.farm_id = f.id;

-- Представление: Статистика по хозяйствам
CREATE OR REPLACE VIEW v_farm_statistics AS
SELECT
    f.id,
    f.bin,
    f.name,
    f.region,
    f.total_area_ha,
    COUNT(DISTINCT fd.id) AS fields_count,
    COUNT(DISTINCT o.id) AS operations_count,
    COUNT(DISTINCT u.id) AS users_count,
    MAX(o.operation_date) AS last_operation_date
FROM farms f
LEFT JOIN fields fd ON f.id = fd.farm_id
LEFT JOIN operations o ON f.id = o.farm_id
LEFT JOIN users u ON f.id = u.farm_id
GROUP BY f.id, f.bin, f.name, f.region, f.total_area_ha;

-- ============================================================================
-- 8. КОММЕНТАРИИ К ТАБЛИЦАМ (документация)
-- ============================================================================

COMMENT ON TABLE users IS 'Пользователи системы (admin/farmer/viewer)';
COMMENT ON TABLE farms IS 'Хозяйства (центральная таблица) - уникальный БИН';
COMMENT ON TABLE fields IS 'Поля хозяйств с почвенными характеристиками';
COMMENT ON TABLE operations IS 'Сельскохозяйственные операции';
COMMENT ON TABLE audit_logs IS 'Журнал аудита всех действий';

COMMENT ON COLUMN farms.bin IS 'БИН/ИИН хозяйства (12 цифр, уникальный)';
COMMENT ON COLUMN users.farm_id IS 'Привязка пользователя к хозяйству';
COMMENT ON COLUMN fields.field_code IS 'Уникальный код поля в системе';

-- ============================================================================
-- СКРИПТ ЗАВЕРШЕН
-- ============================================================================

-- Для применения:
-- 1. Откройте Supabase SQL Editor
-- 2. Скопируйте и выполните этот скрипт
-- 3. Проверьте результат в Table Editor

-- ВАЖНО: Если таблицы уже содержат данные, некоторые ограничения
-- могут не примениться. В этом случае сначала очистите дубликаты:

-- Пример проверки дубликатов БИН:
-- SELECT bin, COUNT(*) FROM farms GROUP BY bin HAVING COUNT(*) > 1;

-- Пример удаления дубликатов (ОСТОРОЖНО!):
-- DELETE FROM farms WHERE id NOT IN (
--     SELECT MIN(id) FROM farms GROUP BY bin
-- );
