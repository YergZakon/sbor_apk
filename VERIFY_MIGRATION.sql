-- ============================================================================
-- ПРОВЕРКА УСПЕШНОСТИ МИГРАЦИИ
-- Выполните этот скрипт, чтобы убедиться, что все создано правильно
-- ============================================================================

-- ============================================================================
-- 1. ПРОВЕРКА НОВЫХ ТАБЛИЦ
-- ============================================================================

SELECT
    '✅ НОВЫЕ ТАБЛИЦЫ:' as check_category,
    '' as table_name,
    '' as status
UNION ALL
SELECT
    '',
    table_name,
    CASE
        WHEN table_name IN ('machinery', 'implements', 'desiccation_details',
                           'tillage_details', 'irrigation_details',
                           'snow_retention_details', 'fallow_details')
        THEN '✅ Существует'
        ELSE '❌ Не найдена'
    END
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
    'machinery', 'implements', 'desiccation_details',
    'tillage_details', 'irrigation_details',
    'snow_retention_details', 'fallow_details'
);

-- ============================================================================
-- 2. ПРОВЕРКА НОВЫХ ПОЛЕЙ В OPERATIONS
-- ============================================================================

SELECT
    '✅ НОВЫЕ ПОЛЯ В OPERATIONS:' as check_category,
    '' as column_name,
    '' as data_type,
    '' as status
UNION ALL
SELECT
    '',
    column_name,
    data_type,
    '✅ Добавлено'
FROM information_schema.columns
WHERE table_name = 'operations'
AND column_name IN ('end_date', 'implement_id', 'machine_year', 'implement_year', 'work_speed_kmh');

-- ============================================================================
-- 3. ПРОВЕРКА НОВЫХ ПОЛЕЙ В SOWING_DETAILS
-- ============================================================================

SELECT
    '✅ НОВЫЕ ПОЛЯ В SOWING_DETAILS:' as check_category,
    '' as column_name,
    '' as data_type,
    '' as status
UNION ALL
SELECT
    '',
    column_name,
    data_type,
    '✅ Добавлено'
FROM information_schema.columns
WHERE table_name = 'sowing_details'
AND column_name IN ('seed_reproduction', 'seed_origin_country', 'combined_with_fertilizer',
                     'combined_fertilizer_name', 'combined_fertilizer_rate_kg_ha');

-- ============================================================================
-- 4. ПРОВЕРКА НОВЫХ ПОЛЕЙ В ECONOMIC_DATA
-- ============================================================================

SELECT
    '✅ НОВЫЕ ПОЛЯ В ECONOMIC_DATA:' as check_category,
    '' as column_name,
    '' as data_type,
    '' as status
UNION ALL
SELECT
    '',
    column_name,
    data_type,
    '✅ Добавлено'
FROM information_schema.columns
WHERE table_name = 'economic_data'
AND column_name IN ('field_rental_cost', 'field_rental_period', 'machinery_rental_cost',
                     'machinery_rental_type', 'rented_machinery_description');

-- ============================================================================
-- 5. ПРОВЕРКА ТИПОВ ОПЕРАЦИЙ
-- ============================================================================

SELECT
    '✅ ТИПЫ ОПЕРАЦИЙ (должно быть 10):' as info,
    UNNEST(
        string_to_array(
            replace(replace(replace(
                pg_get_constraintdef(oid),
                'CHECK ((operation_type)::text = ANY ((ARRAY[', ''
            ), '])))', ''), '''::character varying', ''),
            ', '
        )
    ) AS operation_type
FROM pg_constraint
WHERE conname = 'operations_operation_type_check';

-- ============================================================================
-- 6. ПРОВЕРКА ПРЕДСТАВЛЕНИЙ
-- ============================================================================

SELECT
    '✅ ПРЕДСТАВЛЕНИЯ:' as check_category,
    '' as view_name,
    '' as status
UNION ALL
SELECT
    '',
    table_name,
    '✅ Создано'
FROM information_schema.views
WHERE table_schema = 'public'
AND table_name IN ('operations_with_equipment', 'active_equipment');

-- ============================================================================
-- 7. ПРОВЕРКА ИНДЕКСОВ НА НОВЫХ ТАБЛИЦАХ
-- ============================================================================

SELECT
    '✅ ИНДЕКСЫ НА ТАБЛИЦЕ MACHINERY:' as info,
    indexname as index_name
FROM pg_indexes
WHERE tablename = 'machinery'
AND schemaname = 'public';

SELECT
    '✅ ИНДЕКСЫ НА ТАБЛИЦЕ IMPLEMENTS:' as info,
    indexname as index_name
FROM pg_indexes
WHERE tablename = 'implements'
AND schemaname = 'public';

-- ============================================================================
-- 8. ПРОВЕРКА ВНЕШНИХ КЛЮЧЕЙ
-- ============================================================================

SELECT
    '✅ ВНЕШНИЕ КЛЮЧИ:' as check_category,
    '' as constraint_name,
    '' as table_name,
    '' as column_name,
    '' as referenced_table
UNION ALL
SELECT
    '',
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS referenced_table
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
AND tc.table_name IN ('machinery', 'implements', 'operations',
                      'desiccation_details', 'tillage_details',
                      'irrigation_details', 'snow_retention_details', 'fallow_details');

-- ============================================================================
-- 9. СТРУКТУРА ТАБЛИЦЫ MACHINERY
-- ============================================================================

SELECT
    '✅ СТРУКТУРА ТАБЛИЦЫ MACHINERY:' as info,
    '' as column_name,
    '' as data_type,
    '' as is_nullable
UNION ALL
SELECT
    '',
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'machinery';

-- ============================================================================
-- 10. СТРУКТУРА ТАБЛИЦЫ IMPLEMENTS
-- ============================================================================

SELECT
    '✅ СТРУКТУРА ТАБЛИЦЫ IMPLEMENTS:' as info,
    '' as column_name,
    '' as data_type,
    '' as is_nullable
UNION ALL
SELECT
    '',
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'implements';

-- ============================================================================
-- ИТОГОВЫЙ ОТЧЕТ
-- ============================================================================

DO $$
DECLARE
    tables_count INTEGER;
    expected_tables INTEGER := 7;
    ops_fields_count INTEGER;
    expected_ops_fields INTEGER := 5;
    sowing_fields_count INTEGER;
    expected_sowing_fields INTEGER := 5;
    views_count INTEGER;
    expected_views INTEGER := 2;
    operation_types_count INTEGER;
    expected_types INTEGER := 10;
BEGIN
    -- Подсчет новых таблиц
    SELECT COUNT(*) INTO tables_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name IN ('machinery', 'implements', 'desiccation_details',
                       'tillage_details', 'irrigation_details',
                       'snow_retention_details', 'fallow_details');

    -- Подсчет новых полей в operations
    SELECT COUNT(*) INTO ops_fields_count
    FROM information_schema.columns
    WHERE table_name = 'operations'
    AND column_name IN ('end_date', 'implement_id', 'machine_year', 'implement_year', 'work_speed_kmh');

    -- Подсчет новых полей в sowing_details
    SELECT COUNT(*) INTO sowing_fields_count
    FROM information_schema.columns
    WHERE table_name = 'sowing_details'
    AND column_name IN ('seed_reproduction', 'seed_origin_country', 'combined_with_fertilizer',
                         'combined_fertilizer_name', 'combined_fertilizer_rate_kg_ha');

    -- Подсчет представлений
    SELECT COUNT(*) INTO views_count
    FROM information_schema.views
    WHERE table_schema = 'public'
    AND table_name IN ('operations_with_equipment', 'active_equipment');

    -- Подсчет типов операций
    SELECT array_length(
        string_to_array(
            replace(replace(replace(
                pg_get_constraintdef(oid),
                'CHECK ((operation_type)::text = ANY ((ARRAY[', ''
            ), '])))', ''), '''::character varying', ''),
            ', '
        ), 1
    ) INTO operation_types_count
    FROM pg_constraint
    WHERE conname = 'operations_operation_type_check';

    RAISE NOTICE '========================================';
    RAISE NOTICE 'ИТОГОВЫЙ ОТЧЕТ О МИГРАЦИИ';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE '📊 СТАТИСТИКА:';
    RAISE NOTICE '  Новые таблицы: % / % %', tables_count, expected_tables,
        CASE WHEN tables_count = expected_tables THEN '✅' ELSE '❌' END;
    RAISE NOTICE '  Новые поля в operations: % / % %', ops_fields_count, expected_ops_fields,
        CASE WHEN ops_fields_count = expected_ops_fields THEN '✅' ELSE '❌' END;
    RAISE NOTICE '  Новые поля в sowing_details: % / % %', sowing_fields_count, expected_sowing_fields,
        CASE WHEN sowing_fields_count = expected_sowing_fields THEN '✅' ELSE '❌' END;
    RAISE NOTICE '  Представления: % / % %', views_count, expected_views,
        CASE WHEN views_count = expected_views THEN '✅' ELSE '❌' END;
    RAISE NOTICE '  Типы операций: % / % %', operation_types_count, expected_types,
        CASE WHEN operation_types_count = expected_types THEN '✅' ELSE '❌' END;
    RAISE NOTICE '';

    IF tables_count = expected_tables AND
       ops_fields_count = expected_ops_fields AND
       sowing_fields_count = expected_sowing_fields AND
       views_count = expected_views AND
       operation_types_count = expected_types THEN
        RAISE NOTICE '🎉 МИГРАЦИЯ ПОЛНОСТЬЮ УСПЕШНА!';
        RAISE NOTICE '   Все таблицы, поля и представления созданы правильно';
        RAISE NOTICE '';
        RAISE NOTICE '📋 СЛЕДУЮЩИЙ ШАГ:';
        RAISE NOTICE '   Обновление кода Python (database.py, создание страниц)';
    ELSE
        RAISE WARNING '⚠️ МИГРАЦИЯ ВЫПОЛНЕНА С ПРЕДУПРЕЖДЕНИЯМИ';
        RAISE WARNING '   Некоторые объекты не созданы. Проверьте детали выше.';
    END IF;

    RAISE NOTICE '========================================';
END $$;
