-- ============================================================================
-- БЫСТРАЯ ПРОВЕРКА БАЗЫ ДАННЫХ
-- Упрощённая версия для Supabase SQL Editor
-- ============================================================================

-- 1. ПРОВЕРКА ТАБЛИЦ
SELECT '1. ПРОВЕРКА НАЛИЧИЯ ТАБЛИЦ' AS step;

SELECT
    COUNT(*) AS total_tables,
    string_agg(table_name, ', ' ORDER BY table_name) AS tables
FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';

-- 2. ПРОВЕРКА УНИКАЛЬНЫХ КЛЮЧЕЙ
SELECT '2. ПРОВЕРКА УНИКАЛЬНЫХ КЛЮЧЕЙ' AS step;

SELECT
    tc.table_name,
    string_agg(kcu.column_name, ', ' ORDER BY kcu.ordinal_position) AS unique_columns
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
WHERE tc.constraint_type = 'UNIQUE' AND tc.table_schema = 'public'
GROUP BY tc.table_name
ORDER BY tc.table_name;

-- 3. ПРОВЕРКА ДУБЛИКАТОВ БИН
SELECT '3. ПРОВЕРКА ДУБЛИКАТОВ БИН' AS step;

SELECT
    bin,
    COUNT(*) AS duplicates,
    string_agg(id::text, ', ') AS farm_ids
FROM farms
GROUP BY bin
HAVING COUNT(*) > 1;

-- 4. ПРОВЕРКА ДУБЛИКАТОВ USERNAME
SELECT '4. ПРОВЕРКА ДУБЛИКАТОВ USERNAME' AS step;

SELECT
    username,
    COUNT(*) AS duplicates
FROM users
GROUP BY username
HAVING COUNT(*) > 1;

-- 5. ПРОВЕРКА ДУБЛИКАТОВ EMAIL
SELECT '5. ПРОВЕРКА ДУБЛИКАТОВ EMAIL' AS step;

SELECT
    email,
    COUNT(*) AS duplicates
FROM users
GROUP BY email
HAVING COUNT(*) > 1;

-- 6. СТАТИСТИКА ПО ДАННЫМ
SELECT '6. СТАТИСТИКА ПО ТАБЛИЦАМ' AS step;

SELECT 'users' AS table_name, COUNT(*) AS rows FROM users
UNION ALL SELECT 'farms', COUNT(*) FROM farms
UNION ALL SELECT 'fields', COUNT(*) FROM fields
UNION ALL SELECT 'operations', COUNT(*) FROM operations
UNION ALL SELECT 'sowing_details', COUNT(*) FROM sowing_details
UNION ALL SELECT 'fertilizer_applications', COUNT(*) FROM fertilizer_applications
UNION ALL SELECT 'pesticide_applications', COUNT(*) FROM pesticide_applications
UNION ALL SELECT 'harvest_data', COUNT(*) FROM harvest_data
UNION ALL SELECT 'economic_data', COUNT(*) FROM economic_data
UNION ALL SELECT 'weather_data', COUNT(*) FROM weather_data
UNION ALL SELECT 'machinery', COUNT(*) FROM machinery
UNION ALL SELECT 'gps_tracks', COUNT(*) FROM gps_tracks
UNION ALL SELECT 'satellite_data', COUNT(*) FROM satellite_data
ORDER BY rows DESC;

-- 7. ПРОВЕРКА СИРОТСКИХ ЗАПИСЕЙ
SELECT '7. ПРОВЕРКА СИРОТСКИХ ПОЛЬЗОВАТЕЛЕЙ' AS step;

SELECT u.id, u.username, u.farm_id
FROM users u
WHERE u.farm_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM farms f WHERE f.id = u.farm_id);

SELECT '8. ПРОВЕРКА СИРОТСКИХ ПОЛЕЙ' AS step;

SELECT f.id, f.field_code, f.farm_id
FROM fields f
WHERE NOT EXISTS (SELECT 1 FROM farms fm WHERE fm.id = f.farm_id);

-- ИТОГ
SELECT '✅ ПРОВЕРКА ЗАВЕРШЕНА' AS result;
