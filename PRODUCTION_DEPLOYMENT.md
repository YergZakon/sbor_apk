# 🚀 ИНСТРУКЦИЯ: Применение улучшений на Production

## ⚠️ КРИТИЧЕСКИ ВАЖНО!

Перед началом:
1. ✅ Создайте резервную копию базы данных
2. ✅ Убедитесь, что никто не работает в системе
3. ✅ Выполняйте шаги СТРОГО ПО ПОРЯДКУ

---

## 📋 ШАГ 1: Создание резервной копии

### В Supabase Dashboard:

1. Откройте ваш проект в Supabase
2. Перейдите: **Database** → **Backups**
3. Нажмите **Create Backup**
4. Название: `pre_enhancement_backup_2025_10_22`
5. Дождитесь завершения создания бэкапа
6. ✅ Убедитесь, что бэкап создан успешно

**Или через SQL:**

```sql
-- Суперсет создаст автоматический снэпшот
-- Просто убедитесь, что включены автоматические бэкапы
```

---

## 📋 ШАГ 2: Очистка данных (кроме пользователей и хозяйств)

### В Supabase SQL Editor:

1. Откройте **SQL Editor**
2. Создайте **New Query**
3. Скопируйте содержимое файла: [migrations/000_cleanup_production.sql](migrations/000_cleanup_production.sql)
4. Вставьте в редактор
5. Нажмите **Run** (или F5)

### Ожидаемый результат:

```
========================================
РЕЗУЛЬТАТЫ ОЧИСТКИ:
========================================
СОХРАНЕНО:
  - Пользователей: X
  - Хозяйств: Y
  - Записей аудита: Z
========================================
УДАЛЕНО (должно быть 0):
  - Полей: 0
  - Операций: 0
========================================
✅ Очистка выполнена успешно!
Можно применять миграцию 001_enhanced_operations.sql
```

### Что будет удалено:
- ❌ Все поля
- ❌ Все операции (посев, удобрения, СЗР, уборка)
- ❌ Все экономические данные
- ❌ Все метеоданные
- ❌ Все фитосанитарные обследования
- ❌ Все агрохимические анализы

### Что НЕ будет удалено:
- ✅ Пользователи (users)
- ✅ Хозяйства (farms)
- ✅ Журнал аудита (audit_logs)

---

## 📋 ШАГ 3: Применение миграции с улучшениями

### В Supabase SQL Editor:

1. Создайте **New Query**
2. Скопируйте содержимое файла: [migrations/001_enhanced_operations.sql](migrations/001_enhanced_operations.sql)
3. Вставьте в редактор
4. Нажмите **Run** (или F5)
5. ⏱️ Ожидайте 10-30 секунд

### Ожидаемый результат:

```
Миграция 001_enhanced_operations.sql успешно выполнена
Создано таблиц: machinery, implements, desiccation_details, tillage_details, irrigation_details, snow_retention_details, fallow_details
Обновлено таблиц: operations, sowing_details, economic_data
Создано представлений: operations_with_equipment, active_equipment
```

### Если возникли ошибки:

**Ошибка: "relation already exists"**
- Значит таблица уже создана
- Проверьте, не запускали ли вы миграцию раньше
- Если да, сначала выполните откат: [migrations/001_enhanced_operations_ROLLBACK.sql](migrations/001_enhanced_operations_ROLLBACK.sql)

**Ошибка: "foreign key constraint"**
- Убедитесь, что шаг 2 (очистка) выполнен успешно
- Проверьте, что в таблицах fields и operations нет данных

**Другие ошибки:**
- Скопируйте текст ошибки
- Отправьте мне для анализа

---

## 📋 ШАГ 4: Проверка успешности миграции

### Выполните тестовые запросы:

```sql
-- 1. Проверка новых таблиц
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
    'machinery', 'implements',
    'desiccation_details', 'tillage_details',
    'irrigation_details', 'snow_retention_details', 'fallow_details'
)
ORDER BY table_name;
```

**Ожидаемый результат:** 7 строк (все новые таблицы)

```sql
-- 2. Проверка новых полей в operations
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'operations'
AND column_name IN ('end_date', 'implement_id', 'work_speed_kmh', 'machine_year', 'implement_year')
ORDER BY column_name;
```

**Ожидаемый результат:** 5 строк с новыми полями

```sql
-- 3. Проверка новых полей в sowing_details
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'sowing_details'
AND (column_name LIKE '%seed%' OR column_name LIKE '%combined%')
AND column_name NOT IN ('seeding_rate_kg_ha', 'seeding_depth_cm')
ORDER BY column_name;
```

**Ожидаемый результат:** 5 строк (новые поля для посева)

```sql
-- 4. Проверка расширенных типов операций
SELECT UNNEST(
    string_to_array(
        replace(replace(
            pg_get_constraintdef(oid),
            'CHECK ((operation_type)::text = ANY (ARRAY[', ''
        ), '])))', ''),
        ', '
    )
) AS operation_type
FROM pg_constraint
WHERE conname = 'operations_operation_type_check';
```

**Ожидаемый результат:** 10 типов операций (включая новые: desiccation, tillage, irrigation, snow_retention, fallow)

```sql
-- 5. Проверка представлений
SELECT table_name
FROM information_schema.views
WHERE table_schema = 'public'
AND table_name IN ('operations_with_equipment', 'active_equipment')
ORDER BY table_name;
```

**Ожидаемый результат:** 2 представления

```sql
-- 6. Итоговый отчет
SELECT
    'users' as table_name,
    COUNT(*) as records
FROM users
UNION ALL
SELECT 'farms', COUNT(*) FROM farms
UNION ALL
SELECT 'fields', COUNT(*) FROM fields
UNION ALL
SELECT 'operations', COUNT(*) FROM operations
UNION ALL
SELECT 'machinery', COUNT(*) FROM machinery
UNION ALL
SELECT 'implements', COUNT(*) FROM implements
ORDER BY table_name;
```

**Ожидаемый результат:**
```
table_name  | records
------------|--------
farms       | X (ваши хозяйства)
fields      | 0 (очищено)
implements  | 0 (новая таблица, пустая)
machinery   | 0 (новая таблица, пустая)
operations  | 0 (очищено)
users       | Y (ваши пользователи)
```

---

## 📋 ШАГ 5: Уведомление об успешной миграции

После успешной проверки напишите мне:

```
✅ Миграция выполнена успешно!
Все проверки пройдены.
Готов к обновлению кода.
```

Я сразу начну обновление кода Python:
1. Обновлю `modules/database.py` с новыми моделями
2. Создам страницу Equipment Management
3. Обновлю формы операций
4. Создам новые страницы операций

---

## 🆘 ШАГ 6: Откат (если что-то пошло не так)

### Если миграция не удалась:

**Вариант A: Откатить только новые таблицы**

```sql
-- Выполните в SQL Editor
-- Содержимое файла: migrations/001_enhanced_operations_ROLLBACK.sql
```

**Вариант B: Полное восстановление из бэкапа**

1. Откройте Supabase Dashboard
2. **Database** → **Backups**
3. Найдите бэкап `pre_enhancement_backup_2025_10_22`
4. Нажмите **Restore**
5. Подтвердите восстановление
6. ⏱️ Дождитесь завершения (может занять 5-15 минут)

---

## ⏱️ Время выполнения

- Шаг 1 (Бэкап): 1-2 минуты
- Шаг 2 (Очистка): 10-30 секунд
- Шаг 3 (Миграция): 10-30 секунд
- Шаг 4 (Проверка): 1-2 минуты
- **ИТОГО: 3-5 минут**

---

## 📞 Готовы начать?

Когда будете готовы:

1. Убедитесь, что никто не работает в системе
2. Создайте бэкап
3. Выполните шаги 2-4
4. Сообщите о результате

**Я буду на связи и помогу с любыми вопросами!**

---

## 📋 Чек-лист перед началом

- [ ] Создан бэкап базы данных
- [ ] Пользователи уведомлены о техническом обслуживании
- [ ] Никто не работает в системе
- [ ] Открыт Supabase SQL Editor
- [ ] Готовы файлы миграций
- [ ] Готов откатить изменения в случае проблем

**Все пункты отмечены? Начинайте!** 🚀
