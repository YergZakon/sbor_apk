-- ============================================================================
-- СКРИПТ ПРОВЕРКИ ЦЕЛОСТНОСТИ БАЗЫ ДАННЫХ
-- ============================================================================

-- Этот скрипт проверяет:
-- 1. Наличие всех таблиц
-- 2. Уникальные ключи
-- 3. Внешние ключи
-- 4. Индексы
-- 5. Дубликаты данных
-- 6. Сиротские записи (orphaned records)

-- ============================================================================
-- 1. ПРОВЕРКА НАЛИЧИЯ ВСЕХ ТАБЛИЦ
-- ============================================================================

SELECT 'ПРОВЕРКА ТАБЛИЦ' AS check_type, '=' AS separator;

SELECT
    table_name,
    CASE
        WHEN table_name IN (
            'users', 'farms', 'fields', 'operations',
            'sowing_details', 'fertilizer_applications',
            'pesticide_applications', 'harvest_data',
            'agrochemical_analyses', 'economic_data',
            'weather_data', 'machinery', 'machinery_equipment',
            'gps_tracks', 'phytosanitary_monitoring',
            'satellite_data', 'ref_crops', 'ref_fertilizers',
            'ref_pesticides', 'audit_logs'
        ) THEN '✅ OK'
        ELSE '❌ Unexpected table'
    END AS status
FROM information_schema.tables
WHERE table_schema = 'public'
    AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- Проверка на недостающие таблицы
SELECT 'НЕДОСТАЮЩИЕ ТАБЛИЦЫ' AS check_type;
SELECT
    unnest(ARRAY[
        'users', 'farms', 'fields', 'operations',
        'sowing_details', 'fertilizer_applications',
        'pesticide_applications', 'harvest_data',
        'agrochemical_analyses', 'economic_data',
        'weather_data', 'machinery', 'machinery_equipment',
        'gps_tracks', 'phytosanitary_monitoring',
        'satellite_data', 'ref_crops', 'ref_fertilizers',
        'ref_pesticides', 'audit_logs'
    ]) AS required_table
WHERE NOT EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_schema = 'public'
        AND table_name = required_table
);

-- ============================================================================
-- 2. ПРОВЕРКА УНИКАЛЬНЫХ КЛЮЧЕЙ
-- ============================================================================

SELECT 'ПРОВЕРКА УНИКАЛЬНЫХ КЛЮЧЕЙ' AS check_type;

SELECT
    tc.table_name,
    tc.constraint_name,
    string_agg(kcu.column_name, ', ' ORDER BY kcu.ordinal_position) AS columns,
    '✅ Exists' AS status
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
WHERE tc.constraint_type = 'UNIQUE'
    AND tc.table_schema = 'public'
GROUP BY tc.table_name, tc.constraint_name
ORDER BY tc.table_name, tc.constraint_name;

-- Проверка обязательных уникальных ключей
SELECT 'ПРОВЕРКА ОБЯЗАТЕЛЬНЫХ UNIQUE CONSTRAINTS' AS check_type;

WITH required_uniques AS (
    SELECT 'farms' AS table_name, 'bin' AS column_name
    UNION ALL SELECT 'users', 'username'
    UNION ALL SELECT 'users', 'email'
    UNION ALL SELECT 'fields', 'field_code'
    UNION ALL SELECT 'ref_crops', 'crop_name'
    UNION ALL SELECT 'ref_fertilizers', 'name'
)
SELECT
    ru.table_name,
    ru.column_name,
    CASE
        WHEN EXISTS (
            SELECT 1
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.constraint_type = 'UNIQUE'
                AND tc.table_name = ru.table_name
                AND kcu.column_name = ru.column_name
        ) THEN '✅ OK'
        ELSE '❌ MISSING'
    END AS status
FROM required_uniques ru;

-- ============================================================================
-- 3. ПРОВЕРКА ВНЕШНИХ КЛЮЧЕЙ
-- ============================================================================

SELECT 'ПРОВЕРКА ВНЕШНИХ КЛЮЧЕЙ' AS check_type;

SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    rc.delete_rule,
    '✅ Exists' AS status
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
JOIN information_schema.referential_constraints AS rc
    ON rc.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = 'public'
ORDER BY tc.table_name, kcu.column_name;

-- ============================================================================
-- 4. ПРОВЕРКА ИНДЕКСОВ
-- ============================================================================

SELECT 'ПРОВЕРКА ИНДЕКСОВ' AS check_type;

SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- ============================================================================
-- 5. ПРОВЕРКА ДУБЛИКАТОВ
-- ============================================================================

SELECT 'ПРОВЕРКА ДУБЛИКАТОВ БИН' AS check_type;
SELECT
    bin,
    COUNT(*) AS count,
    string_agg(name, ', ') AS farm_names
FROM farms
GROUP BY bin
HAVING COUNT(*) > 1;

SELECT 'ПРОВЕРКА ДУБЛИКАТОВ USERNAME' AS check_type;
SELECT
    username,
    COUNT(*) AS count
FROM users
GROUP BY username
HAVING COUNT(*) > 1;

SELECT 'ПРОВЕРКА ДУБЛИКАТОВ EMAIL' AS check_type;
SELECT
    email,
    COUNT(*) AS count
FROM users
GROUP BY email
HAVING COUNT(*) > 1;

SELECT 'ПРОВЕРКА ДУБЛИКАТОВ FIELD_CODE' AS check_type;
SELECT
    field_code,
    COUNT(*) AS count
FROM fields
GROUP BY field_code
HAVING COUNT(*) > 1;

-- ============================================================================
-- 6. ПРОВЕРКА СИРОТСКИХ ЗАПИСЕЙ (orphaned records)
-- ============================================================================

SELECT 'ПРОВЕРКА СИРОТСКИХ ЗАПИСЕЙ' AS check_type;

-- Пользователи с несуществующими хозяйствами
SELECT 'Users with invalid farm_id' AS check_type;
SELECT u.id, u.username, u.farm_id
FROM users u
WHERE u.farm_id IS NOT NULL
    AND NOT EXISTS (SELECT 1 FROM farms f WHERE f.id = u.farm_id);

-- Поля с несуществующими хозяйствами
SELECT 'Fields with invalid farm_id' AS check_type;
SELECT f.id, f.field_code, f.farm_id
FROM fields f
WHERE NOT EXISTS (SELECT 1 FROM farms fm WHERE fm.id = f.farm_id);

-- Операции с несуществующими полями
SELECT 'Operations with invalid field_id' AS check_type;
SELECT o.id, o.operation_type, o.field_id
FROM operations o
WHERE NOT EXISTS (SELECT 1 FROM fields f WHERE f.id = o.field_id);

-- Операции с несуществующими хозяйствами
SELECT 'Operations with invalid farm_id' AS check_type;
SELECT o.id, o.operation_type, o.farm_id
FROM operations o
WHERE NOT EXISTS (SELECT 1 FROM farms f WHERE f.id = o.farm_id);

-- ============================================================================
-- 7. СТАТИСТИКА ПО ТАБЛИЦАМ
-- ============================================================================

SELECT 'СТАТИСТИКА ПО ТАБЛИЦАМ' AS check_type;

SELECT
    'users' AS table_name,
    COUNT(*) AS row_count,
    COUNT(CASE WHEN farm_id IS NOT NULL THEN 1 END) AS with_farm,
    COUNT(CASE WHEN farm_id IS NULL THEN 1 END) AS without_farm
FROM users
UNION ALL
SELECT
    'farms',
    COUNT(*),
    NULL,
    NULL
FROM farms
UNION ALL
SELECT
    'fields',
    COUNT(*),
    NULL,
    NULL
FROM fields
UNION ALL
SELECT
    'operations',
    COUNT(*),
    NULL,
    NULL
FROM operations
UNION ALL
SELECT
    'sowing_details',
    COUNT(*),
    NULL,
    NULL
FROM sowing_details
UNION ALL
SELECT
    'fertilizer_applications',
    COUNT(*),
    NULL,
    NULL
FROM fertilizer_applications
UNION ALL
SELECT
    'pesticide_applications',
    COUNT(*),
    NULL,
    NULL
FROM pesticide_applications
UNION ALL
SELECT
    'harvest_data',
    COUNT(*),
    NULL,
    NULL
FROM harvest_data
UNION ALL
SELECT
    'agrochemical_analyses',
    COUNT(*),
    NULL,
    NULL
FROM agrochemical_analyses
UNION ALL
SELECT
    'economic_data',
    COUNT(*),
    NULL,
    NULL
FROM economic_data
UNION ALL
SELECT
    'weather_data',
    COUNT(*),
    NULL,
    NULL
FROM weather_data
UNION ALL
SELECT
    'machinery',
    COUNT(*),
    NULL,
    NULL
FROM machinery
UNION ALL
SELECT
    'gps_tracks',
    COUNT(*),
    NULL,
    NULL
FROM gps_tracks
UNION ALL
SELECT
    'phytosanitary_monitoring',
    COUNT(*),
    NULL,
    NULL
FROM phytosanitary_monitoring
UNION ALL
SELECT
    'satellite_data',
    COUNT(*),
    NULL,
    NULL
FROM satellite_data;

-- ============================================================================
-- 8. ПРОВЕРКА ССЫЛОЧНОЙ ЦЕЛОСТНОСТИ
-- ============================================================================

SELECT 'ИТОГОВАЯ ПРОВЕРКА ЦЕЛОСТНОСТИ' AS check_type;

SELECT
    'Total farms' AS metric,
    COUNT(*)::text AS value
FROM farms
UNION ALL
SELECT
    'Total users',
    COUNT(*)::text
FROM users
UNION ALL
SELECT
    'Users with farms',
    COUNT(*)::text
FROM users WHERE farm_id IS NOT NULL
UNION ALL
SELECT
    'Total fields',
    COUNT(*)::text
FROM fields
UNION ALL
SELECT
    'Total operations',
    COUNT(*)::text
FROM operations
UNION ALL
SELECT
    'Orphaned users (invalid farm_id)',
    COUNT(*)::text
FROM users u
WHERE u.farm_id IS NOT NULL
    AND NOT EXISTS (SELECT 1 FROM farms f WHERE f.id = u.farm_id)
UNION ALL
SELECT
    'Orphaned fields (invalid farm_id)',
    COUNT(*)::text
FROM fields f
WHERE NOT EXISTS (SELECT 1 FROM farms fm WHERE fm.id = f.farm_id)
UNION ALL
SELECT
    'Orphaned operations (invalid field_id)',
    COUNT(*)::text
FROM operations o
WHERE NOT EXISTS (SELECT 1 FROM fields f WHERE f.id = o.field_id);

-- ============================================================================
-- КОНЕЦ ПРОВЕРКИ
-- ============================================================================

SELECT '=== ПРОВЕРКА ЗАВЕРШЕНА ===' AS status;
