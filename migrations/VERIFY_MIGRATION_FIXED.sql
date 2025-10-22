-- ============================================================================
-- ПРОВЕРКА УСПЕШНОСТИ МИГРАЦИИ (ИСПРАВЛЕННАЯ ВЕРСИЯ)
-- ============================================================================

-- 1. НОВЫЕ ТАБЛИЦЫ
SELECT
    '✅ НОВЫЕ ТАБЛИЦЫ:' as check_category,
    '' as table_name,
    '' as status
UNION ALL
SELECT
    '',
    table_name,
    '✅ Существует'
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
    'machinery', 'implements', 'desiccation_details',
    'tillage_details', 'irrigation_details',
    'snow_retention_details', 'fallow_details'
);

-- 2. НОВЫЕ ПОЛЯ В OPERATIONS
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

-- 3. НОВЫЕ ПОЛЯ В SOWING_DETAILS
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

-- 4. НОВЫЕ ПОЛЯ В ECONOMIC_DATA
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

-- 5. ПРЕДСТАВЛЕНИЯ
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

-- 6. СТРУКТУРА ТАБЛИЦЫ MACHINERY
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

-- 7. СТРУКТУРА ТАБЛИЦЫ IMPLEMENTS
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

-- 8. ИНДЕКСЫ НА MACHINERY
SELECT
    '✅ ИНДЕКСЫ НА ТАБЛИЦЕ MACHINERY:' as info,
    indexname as index_name
FROM pg_indexes
WHERE tablename = 'machinery'
AND schemaname = 'public';

-- 9. ИНДЕКСЫ НА IMPLEMENTS
SELECT
    '✅ ИНДЕКСЫ НА ТАБЛИЦЕ IMPLEMENTS:' as info,
    indexname as index_name
FROM pg_indexes
WHERE tablename = 'implements'
AND schemaname = 'public';

-- 10. ВНЕШНИЕ КЛЮЧИ
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
-- ИТОГОВЫЙ ОТЧЕТ С УПРОЩЕННОЙ ЛОГИКОЙ
-- ============================================================================

DO $$
DECLARE
    tables_count INTEGER;
    ops_fields_count INTEGER;
    sowing_fields_count INTEGER;
    economic_fields_count INTEGER;
    views_count INTEGER;
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

    -- Подсчет новых полей в economic_data
    SELECT COUNT(*) INTO economic_fields_count
    FROM information_schema.columns
    WHERE table_name = 'economic_data'
    AND column_name IN ('field_rental_cost', 'field_rental_period', 'machinery_rental_cost',
                         'machinery_rental_type', 'rented_machinery_description');

    -- Подсчет представлений
    SELECT COUNT(*) INTO views_count
    FROM information_schema.views
    WHERE table_schema = 'public'
    AND table_name IN ('operations_with_equipment', 'active_equipment');

    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'ИТОГОВЫЙ ОТЧЕТ О МИГРАЦИИ';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE '📊 СТАТИСТИКА:';
    RAISE NOTICE '  Новые таблицы: % / 7 %', tables_count,
        CASE WHEN tables_count = 7 THEN '✅' ELSE '❌' END;
    RAISE NOTICE '  Новые поля в operations: % / 5 %', ops_fields_count,
        CASE WHEN ops_fields_count = 5 THEN '✅' ELSE '❌' END;
    RAISE NOTICE '  Новые поля в sowing_details: % / 5 %', sowing_fields_count,
        CASE WHEN sowing_fields_count = 5 THEN '✅' ELSE '❌' END;
    RAISE NOTICE '  Новые поля в economic_data: % / 5 %', economic_fields_count,
        CASE WHEN economic_fields_count = 5 THEN '✅' ELSE '❌' END;
    RAISE NOTICE '  Представления: % / 2 %', views_count,
        CASE WHEN views_count = 2 THEN '✅' ELSE '❌' END;
    RAISE NOTICE '';

    IF tables_count = 7 AND
       ops_fields_count = 5 AND
       sowing_fields_count = 5 AND
       economic_fields_count = 5 AND
       views_count = 2 THEN
        RAISE NOTICE '🎉 МИГРАЦИЯ ПОЛНОСТЬЮ УСПЕШНА!';
        RAISE NOTICE '';
        RAISE NOTICE '✅ Создано:';
        RAISE NOTICE '   - 7 новых таблиц (machinery, implements, 5 detail tables)';
        RAISE NOTICE '   - 5 новых полей в operations';
        RAISE NOTICE '   - 5 новых полей в sowing_details';
        RAISE NOTICE '   - 5 новых полей в economic_data';
        RAISE NOTICE '   - 2 представления (operations_with_equipment, active_equipment)';
        RAISE NOTICE '';
        RAISE NOTICE '📋 СЛЕДУЮЩИЙ ШАГ:';
        RAISE NOTICE '   ✅ database.py - модели обновлены';
        RAISE NOTICE '   ⏳ Создание страницы управления техникой (Equipment.py)';
        RAISE NOTICE '   ⏳ Обновление форм операций (Sowing, Fertilizers, Pesticides, Harvest)';
    ELSE
        RAISE WARNING '⚠️ МИГРАЦИЯ ВЫПОЛНЕНА С ПРЕДУПРЕЖДЕНИЯМИ';
        RAISE WARNING '   Проверьте детали выше.';
    END IF;

    RAISE NOTICE '========================================';
    RAISE NOTICE '';
END $$;
