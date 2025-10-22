-- ============================================================================
-- ОТЛАДОЧНАЯ ПРОВЕРКА МИГРАЦИИ
-- Проверяем каждый элемент по отдельности
-- ============================================================================

-- 1. Проверка таблиц
SELECT '1. ПРОВЕРКА ТАБЛИЦ:' as step;
SELECT
    table_name,
    CASE
        WHEN table_name IN ('machinery', 'implements', 'desiccation_details',
                           'tillage_details', 'irrigation_details',
                           'snow_retention_details', 'fallow_details')
        THEN '✅ OK'
        ELSE '❌ MISSING'
    END as status
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
    'machinery', 'implements', 'desiccation_details',
    'tillage_details', 'irrigation_details',
    'snow_retention_details', 'fallow_details'
)
ORDER BY table_name;

-- 2. Подсчет таблиц
SELECT
    '2. ПОДСЧЕТ НОВЫХ ТАБЛИЦ:' as step,
    COUNT(*) as found_count,
    7 as expected_count
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('machinery', 'implements', 'desiccation_details',
                   'tillage_details', 'irrigation_details',
                   'snow_retention_details', 'fallow_details');

-- 3. Проверка полей в operations
SELECT '3. НОВЫЕ ПОЛЯ В OPERATIONS:' as step;
SELECT
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'operations'
AND column_name IN ('end_date', 'implement_id', 'machine_year', 'implement_year', 'work_speed_kmh')
ORDER BY column_name;

-- 4. Подсчет полей в operations
SELECT
    '4. ПОДСЧЕТ ПОЛЕЙ В OPERATIONS:' as step,
    COUNT(*) as found_count,
    5 as expected_count
FROM information_schema.columns
WHERE table_name = 'operations'
AND column_name IN ('end_date', 'implement_id', 'machine_year', 'implement_year', 'work_speed_kmh');

-- 5. Проверка полей в sowing_details
SELECT '5. НОВЫЕ ПОЛЯ В SOWING_DETAILS:' as step;
SELECT
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'sowing_details'
AND column_name IN ('seed_reproduction', 'seed_origin_country', 'combined_with_fertilizer',
                     'combined_fertilizer_name', 'combined_fertilizer_rate_kg_ha')
ORDER BY column_name;

-- 6. Подсчет полей в sowing_details
SELECT
    '6. ПОДСЧЕТ ПОЛЕЙ В SOWING_DETAILS:' as step,
    COUNT(*) as found_count,
    5 as expected_count
FROM information_schema.columns
WHERE table_name = 'sowing_details'
AND column_name IN ('seed_reproduction', 'seed_origin_country', 'combined_with_fertilizer',
                     'combined_fertilizer_name', 'combined_fertilizer_rate_kg_ha');

-- 7. Проверка полей в economic_data
SELECT '7. НОВЫЕ ПОЛЯ В ECONOMIC_DATA:' as step;
SELECT
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'economic_data'
AND column_name IN ('field_rental_cost', 'field_rental_period', 'machinery_rental_cost',
                     'machinery_rental_type', 'rented_machinery_description')
ORDER BY column_name;

-- 8. Проверка представлений
SELECT '8. ПРЕДСТАВЛЕНИЯ:' as step;
SELECT
    table_name as view_name,
    '✅ OK' as status
FROM information_schema.views
WHERE table_schema = 'public'
AND table_name IN ('operations_with_equipment', 'active_equipment')
ORDER BY table_name;

-- 9. Подсчет представлений
SELECT
    '9. ПОДСЧЕТ ПРЕДСТАВЛЕНИЙ:' as step,
    COUNT(*) as found_count,
    2 as expected_count
FROM information_schema.views
WHERE table_schema = 'public'
AND table_name IN ('operations_with_equipment', 'active_equipment');

-- 10. Проверка constraint на operation_type
SELECT '10. CONSTRAINT НА OPERATION_TYPE:' as step;
SELECT
    conname,
    pg_get_constraintdef(oid) as definition
FROM pg_constraint
WHERE conname = 'operations_operation_type_check';

-- 11. Проверка типов операций через constraint
SELECT '11. ТИПЫ ОПЕРАЦИЙ (должно быть 10):' as step;
SELECT
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

-- 12. Подсчет типов операций
SELECT
    '12. ПОДСЧЕТ ТИПОВ ОПЕРАЦИЙ:' as step,
    array_length(
        string_to_array(
            replace(replace(replace(
                pg_get_constraintdef(oid),
                'CHECK ((operation_type)::text = ANY ((ARRAY[', ''
            ), '])))', ''), '''::character varying', ''),
            ', '
        ), 1
    ) as found_count,
    10 as expected_count
FROM pg_constraint
WHERE conname = 'operations_operation_type_check';
