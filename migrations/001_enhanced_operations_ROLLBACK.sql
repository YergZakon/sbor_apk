-- ============================================================================
-- ОТКАТ МИГРАЦИИ: 001_enhanced_operations.sql
-- Версия: 001
-- Дата: 2025-10-22
-- Описание: Откат изменений миграции enhanced_operations
-- ВНИМАНИЕ: Этот скрипт удалит все данные, добавленные в новые таблицы!
-- ============================================================================

-- ============================================================================
-- 1. УДАЛЕНИЕ ПРЕДСТАВЛЕНИЙ
-- ============================================================================

DROP VIEW IF EXISTS active_equipment CASCADE;
DROP VIEW IF EXISTS operations_with_equipment CASCADE;

-- ============================================================================
-- 2. УДАЛЕНИЕ ТРИГГЕРОВ
-- ============================================================================

-- Удаление триггеров только если таблицы существуют
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'machinery') THEN
        DROP TRIGGER IF EXISTS update_machinery_updated_at ON machinery;
    END IF;

    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'implements') THEN
        DROP TRIGGER IF EXISTS update_implements_updated_at ON implements;
    END IF;
END $$;

-- ============================================================================
-- 3. ОТКАТ ИЗМЕНЕНИЙ В ECONOMIC_DATA
-- ============================================================================

ALTER TABLE economic_data DROP COLUMN IF EXISTS field_rental_cost;
ALTER TABLE economic_data DROP COLUMN IF EXISTS field_rental_period;
ALTER TABLE economic_data DROP COLUMN IF EXISTS machinery_rental_cost;
ALTER TABLE economic_data DROP COLUMN IF EXISTS machinery_rental_type;
ALTER TABLE economic_data DROP COLUMN IF EXISTS rented_machinery_description;

-- ============================================================================
-- 4. УДАЛЕНИЕ ТАБЛИЦ ДЕТАЛЕЙ НОВЫХ ОПЕРАЦИЙ
-- ============================================================================

DROP TABLE IF EXISTS fallow_details CASCADE;
DROP TABLE IF EXISTS snow_retention_details CASCADE;
DROP TABLE IF EXISTS irrigation_details CASCADE;
DROP TABLE IF EXISTS tillage_details CASCADE;
DROP TABLE IF EXISTS desiccation_details CASCADE;

-- ============================================================================
-- 5. ОТКАТ ИЗМЕНЕНИЙ В SOWING_DETAILS
-- ============================================================================

ALTER TABLE sowing_details DROP COLUMN IF EXISTS seed_reproduction;
ALTER TABLE sowing_details DROP COLUMN IF EXISTS seed_origin_country;
ALTER TABLE sowing_details DROP COLUMN IF EXISTS combined_with_fertilizer;
ALTER TABLE sowing_details DROP COLUMN IF EXISTS combined_fertilizer_name;
ALTER TABLE sowing_details DROP COLUMN IF EXISTS combined_fertilizer_rate_kg_ha;

-- ============================================================================
-- 6. ОТКАТ ИЗМЕНЕНИЙ В OPERATIONS
-- ============================================================================

-- Удаление внешних ключей
ALTER TABLE operations DROP CONSTRAINT IF EXISTS fk_operations_machinery;
ALTER TABLE operations DROP CONSTRAINT IF EXISTS operations_operation_type_check;

-- Удаление новых полей
ALTER TABLE operations DROP COLUMN IF EXISTS end_date;
ALTER TABLE operations DROP COLUMN IF EXISTS implement_id;
ALTER TABLE operations DROP COLUMN IF EXISTS machine_year;
ALTER TABLE operations DROP COLUMN IF EXISTS implement_year;
ALTER TABLE operations DROP COLUMN IF EXISTS work_speed_kmh;

-- Восстановление старого CHECK constraint для operation_type
ALTER TABLE operations ADD CONSTRAINT operations_operation_type_check CHECK (
    operation_type IN (
        'sowing', 'fertilizing', 'spraying', 'harvest', 'soil_analysis'
    )
);

-- ============================================================================
-- 7. УДАЛЕНИЕ ТАБЛИЦ ТЕХНИКИ И АГРЕГАТОВ
-- ============================================================================

DROP TABLE IF EXISTS implements CASCADE;
DROP TABLE IF EXISTS machinery CASCADE;

-- ============================================================================
-- ЗАВЕРШЕНИЕ ОТКАТА
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE 'Откат миграции 001_enhanced_operations.sql успешно выполнен';
    RAISE NOTICE 'Удалены все новые таблицы и поля';
    RAISE NOTICE 'База данных возвращена к предыдущему состоянию';
END $$;
