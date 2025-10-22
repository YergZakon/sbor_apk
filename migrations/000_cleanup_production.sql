-- ============================================================================
-- ОЧИСТКА PRODUCTION: Удаление всех данных кроме пользователей и хозяйств
-- Дата: 2025-10-22
-- ВНИМАНИЕ: Этот скрипт удалит ВСЕ операции, поля, экономические данные и т.д.
--          Будут сохранены только: users, farms, audit_logs
-- ============================================================================

-- ============================================================================
-- СОЗДАНИЕ РЕЗЕРВНОЙ КОПИИ ПЕРЕД УДАЛЕНИЕМ (рекомендуется!)
-- ============================================================================

-- ВЫПОЛНИТЕ ЭТО В SUPABASE DASHBOARD:
-- Database → Backups → Create Backup
-- Название: "pre_cleanup_backup_2025_10_22"

-- ============================================================================
-- ОТКЛЮЧЕНИЕ ПРОВЕРОК ВНЕШНИХ КЛЮЧЕЙ НА ВРЕМЯ ОЧИСТКИ
-- ============================================================================

SET session_replication_role = 'replica';

-- ============================================================================
-- 1. УДАЛЕНИЕ ДАННЫХ ИЗ СВЯЗАННЫХ ТАБЛИЦ (детали операций)
-- ============================================================================

-- Удаление деталей операций
TRUNCATE TABLE agrochemical_analyses CASCADE;
TRUNCATE TABLE harvest_data CASCADE;
TRUNCATE TABLE pesticide_applications CASCADE;
TRUNCATE TABLE fertilizer_applications CASCADE;
TRUNCATE TABLE sowing_details CASCADE;

-- Удаление мониторинга
TRUNCATE TABLE phytosanitary_monitoring CASCADE;

-- Удаление метеоданных
TRUNCATE TABLE weather_data CASCADE;

-- Удаление экономических данных
TRUNCATE TABLE economic_data CASCADE;

-- ============================================================================
-- 2. УДАЛЕНИЕ ОПЕРАЦИЙ
-- ============================================================================

TRUNCATE TABLE operations CASCADE;

-- ============================================================================
-- 3. УДАЛЕНИЕ ПОЛЕЙ
-- ============================================================================

TRUNCATE TABLE fields CASCADE;

-- ============================================================================
-- 4. УДАЛЕНИЕ ТЕХНИКИ (если таблицы существуют)
-- ============================================================================

-- Проверяем существование таблиц и удаляем данные
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'machinery') THEN
        TRUNCATE TABLE machinery CASCADE;
    END IF;

    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'implements') THEN
        TRUNCATE TABLE implements CASCADE;
    END IF;
END $$;

-- ============================================================================
-- 5. СБРОС ПОСЛЕДОВАТЕЛЬНОСТЕЙ (AUTO INCREMENT)
-- ============================================================================

-- Сброс ID для таблиц, которые будут заполняться заново
ALTER SEQUENCE IF EXISTS fields_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS operations_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS sowing_details_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS fertilizer_applications_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS pesticide_applications_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS harvest_data_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS agrochemical_analyses_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS phytosanitary_monitoring_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS weather_data_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS economic_data_id_seq RESTART WITH 1;

-- Сброс ID для новых таблиц (если существуют)
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_class WHERE relname = 'machinery_id_seq') THEN
        ALTER SEQUENCE machinery_id_seq RESTART WITH 1;
    END IF;

    IF EXISTS (SELECT FROM pg_class WHERE relname = 'implements_id_seq') THEN
        ALTER SEQUENCE implements_id_seq RESTART WITH 1;
    END IF;
END $$;

-- ============================================================================
-- ВКЛЮЧЕНИЕ ПРОВЕРОК ВНЕШНИХ КЛЮЧЕЙ
-- ============================================================================

SET session_replication_role = 'origin';

-- ============================================================================
-- ПРОВЕРКА РЕЗУЛЬТАТОВ
-- ============================================================================

-- Подсчет записей в сохраненных таблицах
DO $$
DECLARE
    users_count INTEGER;
    farms_count INTEGER;
    audit_count INTEGER;
    fields_count INTEGER;
    operations_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO users_count FROM users;
    SELECT COUNT(*) INTO farms_count FROM farms;
    SELECT COUNT(*) INTO audit_count FROM audit_logs;
    SELECT COUNT(*) INTO fields_count FROM fields;
    SELECT COUNT(*) INTO operations_count FROM operations;

    RAISE NOTICE '========================================';
    RAISE NOTICE 'РЕЗУЛЬТАТЫ ОЧИСТКИ:';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'СОХРАНЕНО:';
    RAISE NOTICE '  - Пользователей: %', users_count;
    RAISE NOTICE '  - Хозяйств: %', farms_count;
    RAISE NOTICE '  - Записей аудита: %', audit_count;
    RAISE NOTICE '========================================';
    RAISE NOTICE 'УДАЛЕНО (должно быть 0):';
    RAISE NOTICE '  - Полей: %', fields_count;
    RAISE NOTICE '  - Операций: %', operations_count;
    RAISE NOTICE '========================================';

    IF fields_count = 0 AND operations_count = 0 THEN
        RAISE NOTICE '✅ Очистка выполнена успешно!';
        RAISE NOTICE 'Можно применять миграцию 001_enhanced_operations.sql';
    ELSE
        RAISE WARNING '⚠️ Некоторые данные не были удалены!';
    END IF;
END $$;

-- ============================================================================
-- СПИСОК СОХРАНЕННЫХ ПОЛЬЗОВАТЕЛЕЙ И ХОЗЯЙСТВ
-- ============================================================================

-- Вывод сохраненных пользователей
SELECT
    id,
    username,
    full_name,
    role,
    farm_id,
    is_active
FROM users
ORDER BY id;

-- Вывод сохраненных хозяйств
SELECT
    id,
    bin,
    name,
    region,
    district,
    total_area_ha
FROM farms
ORDER BY id;

-- ============================================================================
-- ЗАВЕРШЕНИЕ
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'СЛЕДУЮЩИЙ ШАГ:';
    RAISE NOTICE 'Выполните миграцию 001_enhanced_operations.sql';
    RAISE NOTICE '========================================';
END $$;
