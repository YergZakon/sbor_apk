-- Диагностика операций для пользователя Latifundist
-- Выполните эти запросы в Supabase SQL Editor

-- 1. Информация о пользователе Latifundist
SELECT id, username, full_name, farm_id
FROM users
WHERE username = 'Latifundist' OR full_name LIKE '%Латифундия%';

-- 2. Все операции в системе с информацией о farm_id
SELECT
    o.id,
    o.operation_type,
    o.operation_date,
    f.field_code,
    f.name as field_name,
    f.farm_id,
    fa.name as farm_name
FROM operations o
LEFT JOIN fields f ON o.field_id = f.id
LEFT JOIN farms fa ON f.farm_id = fa.id
ORDER BY o.operation_date DESC;

-- 3. Операции для хозяйства Латифундия (farm_id=8)
SELECT
    o.id,
    o.operation_type,
    o.operation_date,
    f.field_code,
    f.name as field_name
FROM operations o
JOIN fields f ON o.field_id = f.id
WHERE f.farm_id = 8
ORDER BY o.operation_date DESC;

-- 4. Операции для хозяйства Журавлевка (farm_id=2)
SELECT
    o.id,
    o.operation_type,
    o.operation_date,
    f.field_code,
    f.name as field_name
FROM operations o
JOIN fields f ON o.field_id = f.id
WHERE f.farm_id = 2
ORDER BY o.operation_date DESC;

-- 5. Подсчет операций по хозяйствам
SELECT
    fa.id as farm_id,
    fa.name as farm_name,
    COUNT(o.id) as operations_count
FROM farms fa
LEFT JOIN fields f ON fa.id = f.farm_id
LEFT JOIN operations o ON f.id = o.field_id
GROUP BY fa.id, fa.name
ORDER BY fa.id;
