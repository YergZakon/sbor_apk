-- ============================================================================
-- ПРОВЕРКА ТЕКУЩЕГО СОСТОЯНИЯ БАЗЫ ДАННЫХ
-- Выполните этот скрипт, чтобы узнать, что уже есть в БД
-- ============================================================================

-- 1. Проверка существования новых таблиц
SELECT
    'Таблица существует: ' || table_name as status
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
    'machinery', 'implements',
    'desiccation_details', 'tillage_details',
    'irrigation_details', 'snow_retention_details', 'fallow_details'
)
ORDER BY table_name;

-- 2. Проверка новых полей в operations
SELECT
    'Поле существует в operations: ' || column_name as status
FROM information_schema.columns
WHERE table_name = 'operations'
AND column_name IN ('end_date', 'implement_id', 'work_speed_kmh', 'machine_year', 'implement_year')
ORDER BY column_name;

-- 3. Проверка новых полей в sowing_details
SELECT
    'Поле существует в sowing_details: ' || column_name as status
FROM information_schema.columns
WHERE table_name = 'sowing_details'
AND column_name IN ('seed_reproduction', 'seed_origin_country', 'combined_with_fertilizer',
                     'combined_fertilizer_name', 'combined_fertilizer_rate_kg_ha')
ORDER BY column_name;

-- 4. Проверка представлений
SELECT
    'Представление существует: ' || table_name as status
FROM information_schema.views
WHERE table_schema = 'public'
AND table_name IN ('operations_with_equipment', 'active_equipment')
ORDER BY table_name;

-- 5. Подсчет данных в основных таблицах
SELECT 'users' as table_name, COUNT(*) as records FROM users
UNION ALL
SELECT 'farms', COUNT(*) FROM farms
UNION ALL
SELECT 'fields', COUNT(*) FROM fields
UNION ALL
SELECT 'operations', COUNT(*) FROM operations
ORDER BY table_name;

-- 6. Проверка текущего CHECK constraint для operation_type
SELECT
    conname as constraint_name,
    pg_get_constraintdef(oid) as definition
FROM pg_constraint
WHERE conname = 'operations_operation_type_check';

-- 7. ИТОГОВЫЙ СТАТУС
DO $$
DECLARE
    machinery_exists BOOLEAN;
    implements_exists BOOLEAN;
    new_ops_fields_count INTEGER;
BEGIN
    -- Проверка таблиц
    SELECT EXISTS (
        SELECT FROM information_schema.tables
        WHERE table_name = 'machinery'
    ) INTO machinery_exists;

    SELECT EXISTS (
        SELECT FROM information_schema.tables
        WHERE table_name = 'implements'
    ) INTO implements_exists;

    -- Проверка новых полей в operations
    SELECT COUNT(*) INTO new_ops_fields_count
    FROM information_schema.columns
    WHERE table_name = 'operations'
    AND column_name IN ('end_date', 'implement_id', 'work_speed_kmh');

    RAISE NOTICE '========================================';
    RAISE NOTICE 'ТЕКУЩЕЕ СОСТОЯНИЕ БАЗЫ ДАННЫХ:';
    RAISE NOTICE '========================================';

    IF machinery_exists AND implements_exists AND new_ops_fields_count = 3 THEN
        RAISE NOTICE '✅ Миграция УЖЕ ПРИМЕНЕНА';
        RAISE NOTICE 'Таблицы machinery и implements существуют';
        RAISE NOTICE 'Новые поля в operations добавлены';
        RAISE NOTICE '';
        RAISE NOTICE 'СЛЕДУЮЩИЙ ШАГ: Обновление кода Python';
    ELSIF machinery_exists OR implements_exists OR new_ops_fields_count > 0 THEN
        RAISE NOTICE '⚠️ ЧАСТИЧНАЯ МИГРАЦИЯ';
        RAISE NOTICE 'Миграция применена не полностью!';
        RAISE NOTICE 'Таблица machinery: %', machinery_exists;
        RAISE NOTICE 'Таблица implements: %', implements_exists;
        RAISE NOTICE 'Новые поля в operations: %', new_ops_fields_count;
        RAISE NOTICE '';
        RAISE NOTICE 'РЕКОМЕНДАЦИЯ: Выполните откат и примените миграцию заново';
    ELSE
        RAISE NOTICE '📋 МИГРАЦИЯ НЕ ПРИМЕНЕНА';
        RAISE NOTICE 'База данных в исходном состоянии';
        RAISE NOTICE '';
        RAISE NOTICE 'СЛЕДУЮЩИЙ ШАГ:';
        RAISE NOTICE '1. Выполните 000_cleanup_production.sql';
        RAISE NOTICE '2. Выполните 001_enhanced_operations.sql';
    END IF;

    RAISE NOTICE '========================================';
END $$;
