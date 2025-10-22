-- ============================================================================
-- ДИАГНОСТИЧЕСКИЕ ЗАПРОСЫ ДЛЯ НОВОГО ПОЛЬЗОВАТЕЛЯ
-- ============================================================================

-- Выполните ВСЕ эти запросы в Supabase SQL Editor и скопируйте результаты

-- ============================================================================
-- 1. ИНФОРМАЦИЯ О ВАШЕМ ПОЛЬЗОВАТЕЛЕ
-- ============================================================================

-- ЗАМЕНИТЕ 'ВАШ_USERNAME' на ваш логин!
SELECT
    id AS user_id,
    username,
    full_name,
    role,
    farm_id,
    created_at,
    last_login
FROM users
WHERE username = 'ВАШ_USERNAME';  -- ИЗМЕНИТЕ ЭТО!

-- ============================================================================
-- 2. ИНФОРМАЦИЯ О ВАШЕМ ХОЗЯЙСТВЕ
-- ============================================================================

-- Используйте farm_id из предыдущего запроса
SELECT
    id AS farm_id,
    bin,
    name,
    director_name,
    region,
    created_at
FROM farms
WHERE id = (SELECT farm_id FROM users WHERE username = 'ВАШ_USERNAME');  -- ИЗМЕНИТЕ ЭТО!

-- ============================================================================
-- 3. ВСЕ ПОЛЯ ВАШЕГО ХОЗЯЙСТВА
-- ============================================================================

SELECT
    f.id AS field_id,
    f.farm_id,
    f.field_code,
    f.name AS field_name,
    f.area_ha,
    f.created_at,
    fm.name AS farm_name
FROM fields f
LEFT JOIN farms fm ON f.farm_id = fm.id
WHERE f.farm_id = (SELECT farm_id FROM users WHERE username = 'ВАШ_USERNAME');  -- ИЗМЕНИТЕ ЭТО!

-- ============================================================================
-- 4. ВСЕ ПОЛЯ В СИСТЕМЕ (для проверки)
-- ============================================================================

SELECT
    f.id AS field_id,
    f.farm_id,
    f.field_code,
    f.name AS field_name,
    f.area_ha,
    fm.name AS farm_name,
    fm.bin
FROM fields f
LEFT JOIN farms fm ON f.farm_id = fm.id
ORDER BY f.created_at DESC
LIMIT 10;

-- ============================================================================
-- 5. ПРОВЕРКА: ГДЕ СОЗДАНО ПОСЛЕДНЕЕ ПОЛЕ?
-- ============================================================================

SELECT
    f.id AS field_id,
    f.farm_id,
    f.field_code,
    f.name AS field_name,
    f.area_ha,
    f.created_at,
    fm.name AS farm_name,
    fm.bin,
    u.username AS farm_owner
FROM fields f
LEFT JOIN farms fm ON f.farm_id = fm.id
LEFT JOIN users u ON u.farm_id = fm.id
ORDER BY f.created_at DESC
LIMIT 1;

-- ============================================================================
-- 6. ВСЕ ХОЗЯЙСТВА В СИСТЕМЕ
-- ============================================================================

SELECT
    f.id AS farm_id,
    f.bin,
    f.name AS farm_name,
    COUNT(fd.id) AS fields_count,
    u.username AS owner_username
FROM farms f
LEFT JOIN fields fd ON f.id = fd.farm_id
LEFT JOIN users u ON u.farm_id = f.id
GROUP BY f.id, f.bin, f.name, u.username
ORDER BY f.created_at DESC;

-- ============================================================================
-- СКОПИРУЙТЕ РЕЗУЛЬТАТЫ ВСЕХ 6 ЗАПРОСОВ!
-- ============================================================================
