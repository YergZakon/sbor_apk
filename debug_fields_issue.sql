-- ============================================================================
-- ДИАГНОСТИКА ПРОБЛЕМЫ С ОТОБРАЖЕНИЕМ ПОЛЕЙ
-- ============================================================================

-- Этот скрипт поможет понять, почему пользователь не видит свои поля

-- 1. ПРОВЕРКА ПОЛЬЗОВАТЕЛЕЙ И ИХ ХОЗЯЙСТВ
SELECT '1. ПОЛЬЗОВАТЕЛИ И ИХ ХОЗЯЙСТВА' AS step;

SELECT
    u.id AS user_id,
    u.username,
    u.full_name,
    u.role,
    u.farm_id,
    f.name AS farm_name,
    f.bin AS farm_bin
FROM users u
LEFT JOIN farms f ON u.farm_id = f.id
ORDER BY u.id;

-- 2. ПРОВЕРКА ХОЗЯЙСТВ И КОЛИЧЕСТВА ПОЛЕЙ
SELECT '2. ХОЗЯЙСТВА И КОЛИЧЕСТВО ПОЛЕЙ' AS step;

SELECT
    f.id AS farm_id,
    f.bin,
    f.name AS farm_name,
    COUNT(fd.id) AS fields_count,
    string_agg(fd.field_code, ', ') AS field_codes
FROM farms f
LEFT JOIN fields fd ON f.id = fd.farm_id
GROUP BY f.id, f.bin, f.name
ORDER BY f.id;

-- 3. ПОЛНАЯ ИНФОРМАЦИЯ О ПОЛЯХ
SELECT '3. ВСЕ ПОЛЯ В СИСТЕМЕ' AS step;

SELECT
    fd.id AS field_id,
    fd.farm_id,
    fd.field_code,
    fd.name AS field_name,
    fd.area_ha,
    f.name AS farm_name,
    f.bin AS farm_bin
FROM fields fd
JOIN farms f ON fd.farm_id = f.id
ORDER BY fd.farm_id, fd.field_code;

-- 4. ПОИСК НЕСООТВЕТСТВИЙ: ПОЛЬЗОВАТЕЛЬ → ХОЗЯЙСТВО → ПОЛЯ
SELECT '4. ПРОБЛЕМНЫЕ СВЯЗИ' AS step;

-- Пользователи БЕЗ хозяйства
SELECT 'Пользователи без хозяйства:' AS issue;
SELECT u.id, u.username, u.full_name, u.farm_id
FROM users u
WHERE u.farm_id IS NULL AND u.role != 'admin';

-- Пользователи с НЕСУЩЕСТВУЮЩИМ хозяйством
SELECT 'Пользователи с несуществующим хозяйством:' AS issue;
SELECT u.id, u.username, u.farm_id
FROM users u
WHERE u.farm_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM farms f WHERE f.id = u.farm_id);

-- Поля с НЕСУЩЕСТВУЮЩИМ хозяйством
SELECT 'Поля с несуществующим хозяйством:' AS issue;
SELECT fd.id, fd.field_code, fd.farm_id
FROM fields fd
WHERE NOT EXISTS (SELECT 1 FROM farms f WHERE f.id = fd.farm_id);

-- 5. ДЕТАЛЬНАЯ ПРОВЕРКА КОНКРЕТНОГО ПОЛЬЗОВАТЕЛЯ
-- Замените 'USERNAME' на имя пользователя, у которого проблема

SELECT '5. ДЕТАЛЬНАЯ ПРОВЕРКА КОНКРЕТНОГО ПОЛЬЗОВАТЕЛЯ' AS step;

-- Введите username пользователя:
DO $$
DECLARE
    check_username TEXT := 'ВВЕДИТЕ_USERNAME_СЮДА'; -- ИЗМЕНИТЕ ЭТО!
    user_record RECORD;
    farm_record RECORD;
BEGIN
    -- Получаем пользователя
    SELECT * INTO user_record FROM users WHERE username = check_username;

    IF user_record IS NULL THEN
        RAISE NOTICE 'Пользователь % не найден!', check_username;
        RETURN;
    END IF;

    RAISE NOTICE '=== ПОЛЬЗОВАТЕЛЬ ===';
    RAISE NOTICE 'ID: %, Username: %, Role: %', user_record.id, user_record.username, user_record.role;
    RAISE NOTICE 'farm_id: %', user_record.farm_id;

    IF user_record.farm_id IS NULL THEN
        RAISE NOTICE 'ПРОБЛЕМА: Пользователь НЕ ПРИВЯЗАН к хозяйству!';
        RETURN;
    END IF;

    -- Получаем хозяйство
    SELECT * INTO farm_record FROM farms WHERE id = user_record.farm_id;

    IF farm_record IS NULL THEN
        RAISE NOTICE 'ПРОБЛЕМА: Хозяйство с ID=% НЕ СУЩЕСТВУЕТ!', user_record.farm_id;
        RETURN;
    END IF;

    RAISE NOTICE '=== ХОЗЯЙСТВО ===';
    RAISE NOTICE 'ID: %, БИН: %, Название: %', farm_record.id, farm_record.bin, farm_record.name;

    -- Проверяем поля
    DECLARE
        fields_count INT;
    BEGIN
        SELECT COUNT(*) INTO fields_count FROM fields WHERE farm_id = user_record.farm_id;
        RAISE NOTICE '=== ПОЛЯ ===';
        RAISE NOTICE 'Количество полей: %', fields_count;

        IF fields_count = 0 THEN
            RAISE NOTICE 'ПРОБЛЕМА: У хозяйства НЕТ ПОЛЕЙ!';
        ELSE
            RAISE NOTICE 'Список полей:';
            FOR farm_record IN SELECT field_code, name, area_ha FROM fields WHERE farm_id = user_record.farm_id LOOP
                RAISE NOTICE '  - %: % (% га)', farm_record.field_code, farm_record.name, farm_record.area_ha;
            END LOOP;
        END IF;
    END;
END $$;

-- 6. ПРОВЕРКА: КАКИЕ ХОЗЯЙСТВА БЕЗ ПОЛЬЗОВАТЕЛЕЙ
SELECT '6. ХОЗЯЙСТВА БЕЗ ПОЛЬЗОВАТЕЛЕЙ' AS step;

SELECT
    f.id,
    f.bin,
    f.name,
    COUNT(fd.id) AS fields_count
FROM farms f
LEFT JOIN fields fd ON f.id = fd.farm_id
WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.farm_id = f.id)
GROUP BY f.id, f.bin, f.name;

-- 7. ИТОГОВАЯ СТАТИСТИКА
SELECT '7. ИТОГОВАЯ СТАТИСТИКА' AS step;

SELECT
    'Пользователей всего' AS metric,
    COUNT(*)::TEXT AS value
FROM users
UNION ALL
SELECT
    'Пользователей с хозяйством',
    COUNT(*)::TEXT
FROM users WHERE farm_id IS NOT NULL
UNION ALL
SELECT
    'Пользователей БЕЗ хозяйства (не админы)',
    COUNT(*)::TEXT
FROM users WHERE farm_id IS NULL AND role != 'admin'
UNION ALL
SELECT
    'Хозяйств всего',
    COUNT(*)::TEXT
FROM farms
UNION ALL
SELECT
    'Полей всего',
    COUNT(*)::TEXT
FROM fields
UNION ALL
SELECT
    'Хозяйств БЕЗ полей',
    COUNT(*)::TEXT
FROM farms f
WHERE NOT EXISTS (SELECT 1 FROM fields fd WHERE fd.farm_id = f.id);

-- ============================================================================
-- РЕКОМЕНДАЦИИ ПО ИСПРАВЛЕНИЮ
-- ============================================================================

/*
ПРОБЛЕМА 1: Пользователь без хозяйства (farm_id = NULL)

РЕШЕНИЕ:
-- Привязать пользователя к хозяйству
UPDATE users
SET farm_id = (SELECT id FROM farms WHERE bin = 'БИН_ХОЗЯЙСТВА')
WHERE username = 'USERNAME';


ПРОБЛЕМА 2: Поля созданы с неправильным farm_id

РЕШЕНИЕ:
-- Изменить farm_id у полей
UPDATE fields
SET farm_id = (SELECT id FROM farms WHERE bin = 'ПРАВИЛЬНЫЙ_БИН')
WHERE farm_id = НЕПРАВИЛЬНЫЙ_ID;


ПРОБЛЕМА 3: У хозяйства нет полей

РЕШЕНИЕ:
-- Создать поле для хозяйства
INSERT INTO fields (farm_id, field_code, name, area_ha, created_at)
VALUES (
    (SELECT id FROM farms WHERE bin = 'БИН_ХОЗЯЙСТВА'),
    'FIELD_001',
    'Тестовое поле',
    100.0,
    NOW()
);


ПРОБЛЕМА 4: Пользователь привязан к несуществующему хозяйству

РЕШЕНИЕ:
-- Убрать неправильную привязку
UPDATE users SET farm_id = NULL WHERE username = 'USERNAME';
-- Затем привязать к правильному хозяйству (см. ПРОБЛЕМА 1)
*/

SELECT '✅ ДИАГНОСТИКА ЗАВЕРШЕНА' AS result;
