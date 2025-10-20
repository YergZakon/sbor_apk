# Supabase Quick Start - Быстрый старт

## 🚀 За 5 минут

### Шаг 1: Подключитесь к Supabase (1 мин)

1. Откройте `.env` файл
2. Добавьте строку подключения:
```env
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

### Шаг 2: Проверьте текущее состояние (1 мин)

Откройте **Supabase SQL Editor** и выполните:

```sql
-- Скопируйте содержимое файла quick_check.sql
```

Это покажет:
- ✅ Какие таблицы есть (должно быть 18)
- ✅ Какие уникальные ключи установлены
- ⚠️ Есть ли дубликаты БИН/username/email
- ⚠️ Есть ли сиротские записи

### Шаг 3: Примените улучшения (2 мин)

**Если нашли дубликаты**, сначала очистите их:

```sql
-- Удалить дубликаты БИН (оставить первый)
DELETE FROM farms
WHERE id NOT IN (SELECT MIN(id) FROM farms GROUP BY bin);

-- Удалить дубликаты username
DELETE FROM users
WHERE id NOT IN (SELECT MIN(id) FROM users GROUP BY username);
```

**Затем выполните:**

```sql
-- Скопируйте содержимое файла supabase_improvements.sql
```

### Шаг 4: Проверьте результат (1 мин)

Снова выполните `quick_check.sql` и убедитесь:
- ✅ Уникальные ключи добавлены
- ✅ Дубликатов нет
- ✅ Сиротских записей нет

### Шаг 5: Запустите приложение

```bash
streamlit run Home.py
```

Готово! 🎉

---

## 📋 Что было улучшено

После выполнения `supabase_improvements.sql`:

### ✅ Уникальные ключи
- `farms.bin` - БИН хозяйства (UNIQUE)
- `users.username` - имя пользователя (UNIQUE)
- `users.email` - email (UNIQUE)
- `fields.field_code` - код поля (UNIQUE)

### ✅ Составные ключи (предотвращение дубликатов)
- `economic_data(field_id, year, crop)` - одна запись на поле/год/культуру
- `weather_data(farm_id, datetime)` - одна запись на время
- `satellite_data(field_id, acquisition_date, satellite_source)` - одна запись на дату/источник

### ✅ 40+ индексов для скорости
- На `farm_id` во всех таблицах
- На датах операций
- На типах операций
- Для быстрых JOIN'ов

### ✅ CHECK constraints (валидация)
- БИН = 12 символов
- Площади >= 0
- Роль в ('admin', 'farmer', 'viewer')
- NDVI между -1 и 1

### ✅ Триггеры
- Автоматическое обновление `updated_at`

### ✅ CASCADE DELETE
- При удалении хозяйства удаляются все связанные данные

### ✅ Views (представления)
- `v_fields_with_farms` - поля с хозяйствами
- `v_operations_summary` - сводка операций
- `v_users_with_farms` - пользователи с хозяйствами
- `v_farm_statistics` - статистика по хозяйствам

---

## 🔍 Проверка конкретных проблем

### Проблема 1: Дубликаты БИН

```sql
-- Найти дубликаты
SELECT bin, COUNT(*), string_agg(name, ', ') AS farms
FROM farms
GROUP BY bin
HAVING COUNT(*) > 1;

-- Удалить (оставить первый)
DELETE FROM farms
WHERE id NOT IN (SELECT MIN(id) FROM farms GROUP BY bin);
```

### Проблема 2: Пользователь с несуществующим хозяйством

```sql
-- Найти проблемных пользователей
SELECT u.id, u.username, u.farm_id
FROM users u
WHERE u.farm_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM farms f WHERE f.id = u.farm_id);

-- Исправить (установить farm_id в NULL)
UPDATE users SET farm_id = NULL
WHERE farm_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM farms WHERE id = farm_id);
```

### Проблема 3: Медленные запросы

```sql
-- Проверить наличие индексов
SELECT tablename, indexname
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- Если индексов мало, выполните supabase_improvements.sql
```

---

## 📁 Файлы в проекте

### Для быстрого старта:
- **SUPABASE_QUICKSTART.md** ← вы здесь
- **quick_check.sql** - быстрая проверка (5 запросов)
- **supabase_improvements.sql** - все улучшения (одним скриптом)

### Для детального изучения:
- **DATABASE_SCHEMA.md** - полная документация
- **DATABASE_SUMMARY.md** - краткая сводка
- **SUPABASE_SETUP.md** - подробная инструкция
- **check_database_integrity.sql** - комплексная проверка
- **supabase_migration.sql** - создание таблиц с нуля

---

## ⚠️ Важно!

### Перед применением улучшений:

1. ✅ Сделайте резервную копию данных
2. ✅ Проверьте, есть ли дубликаты
3. ✅ Очистите дубликаты (если есть)
4. ✅ Только потом применяйте `supabase_improvements.sql`

### После применения:

1. ✅ Проверьте, что уникальные ключи установлены
2. ✅ Протестируйте создание хозяйства
3. ✅ Протестируйте регистрацию пользователя
4. ✅ Проверьте, что дубликаты больше не создаются

---

## 🆘 Если что-то пошло не так

### Ошибка: "duplicate key value violates unique constraint"

**Причина:** В базе уже есть дубликаты

**Решение:**
1. Выполните `quick_check.sql`
2. Найдите дубликаты
3. Удалите дубликаты вручную
4. Повторно выполните `supabase_improvements.sql`

### Ошибка: "constraint already exists"

**Причина:** Улучшения уже применены

**Решение:** Это нормально, можете игнорировать или использовать:
```sql
ALTER TABLE ... DROP CONSTRAINT IF EXISTS ...
```

### База данных повреждена

**Решение:**
1. Откройте Supabase Dashboard → Database → Backups
2. Восстановите последнюю резервную копию
3. Повторите процесс

---

## ✅ Чек-лист готовности к production

- [ ] Выполнен `supabase_improvements.sql`
- [ ] Проверено `quick_check.sql` - нет дубликатов
- [ ] Уникальные ключи установлены (БИН, username, email)
- [ ] Индексы созданы (40+ индексов)
- [ ] CHECK constraints работают
- [ ] Триггеры для updated_at активны
- [ ] CASCADE DELETE настроен
- [ ] Представления (views) созданы
- [ ] Приложение запускается
- [ ] Регистрация нового пользователя работает
- [ ] Создание хозяйства работает
- [ ] Дубликаты не создаются

---

## 📞 Нужна помощь?

1. Проверьте **DATABASE_SUMMARY.md** - там есть быстрые решения
2. Проверьте **SUPABASE_SETUP.md** - полная инструкция
3. Выполните `check_database_integrity.sql` - полная диагностика
4. Обратитесь к разработчику
