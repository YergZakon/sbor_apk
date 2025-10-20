# Файлы базы данных - Навигация

## 🚀 Быстрый старт

**Новичок? Начните здесь:**
1. 📖 [SUPABASE_QUICKSTART.md](SUPABASE_QUICKSTART.md) - за 5 минут
2. ⚡ [quick_check.sql](quick_check.sql) - быстрая проверка

**Первый раз настраиваете?**
→ [SUPABASE_SETUP.md](SUPABASE_SETUP.md) - подробная инструкция

---

## 📁 Все файлы базы данных

### 🎯 Для быстрого старта (начинайте с этого)

| Файл | Назначение | Время | Сложность |
|------|-----------|-------|-----------|
| **SUPABASE_QUICKSTART.md** | Быстрый старт за 5 минут | 5 мин | ⭐ Легко |
| **quick_check.sql** | Быстрая проверка БД (8 запросов) | 10 сек | ⭐ Легко |

### 📚 Документация

| Файл | Назначение | Когда читать |
|------|-----------|-------------|
| **DATABASE_SUMMARY.md** | Краткая сводка структуры БД | Для общего понимания |
| **DATABASE_SCHEMA.md** | Полная документация (6500+ строк) | Для детального изучения |
| **DATABASE_FILES_README.md** | Навигация (этот файл) | Когда не знаете, с чего начать |

### 🛠️ SQL-скрипты

| Файл | Назначение | Когда выполнять |
|------|-----------|----------------|
| **supabase_migration.sql** | Создание всех таблиц с нуля | При первой настройке |
| **supabase_improvements.sql** | Улучшения (ключи, индексы, constraints) | После создания таблиц |
| **check_database_integrity.sql** | Комплексная проверка целостности | Периодически для диагностики |

### 📖 Инструкции

| Файл | Назначение | Для кого |
|------|-----------|----------|
| **SUPABASE_SETUP.md** | Подробная настройка Supabase | Администраторы |

---

## 🎯 Сценарии использования

### Сценарий 1: Первый раз настраиваю Supabase

1. Прочитайте [SUPABASE_QUICKSTART.md](SUPABASE_QUICKSTART.md)
2. Выполните [supabase_migration.sql](supabase_migration.sql) в SQL Editor
3. Выполните [quick_check.sql](quick_check.sql) для проверки
4. Выполните [supabase_improvements.sql](supabase_improvements.sql)
5. Снова выполните [quick_check.sql](quick_check.sql)

**Время:** 10-15 минут

---

### Сценарий 2: У меня уже есть таблицы, хочу улучшить

1. Выполните [quick_check.sql](quick_check.sql) - проверьте текущее состояние
2. Если есть дубликаты - очистите их (см. SUPABASE_QUICKSTART.md)
3. Выполните [supabase_improvements.sql](supabase_improvements.sql)
4. Снова выполните [quick_check.sql](quick_check.sql) - убедитесь, что всё ОК

**Время:** 5 минут

---

### Сценарий 3: Что-то работает неправильно, нужна диагностика

1. Выполните [check_database_integrity.sql](check_database_integrity.sql)
2. Изучите результаты:
   - Есть ли все таблицы?
   - Есть ли уникальные ключи?
   - Есть ли дубликаты?
   - Есть ли сиротские записи?
3. Исправьте найденные проблемы
4. Повторите проверку

**Время:** 10 минут

---

### Сценарий 4: Хочу понять структуру базы данных

1. Прочитайте [DATABASE_SUMMARY.md](DATABASE_SUMMARY.md) - краткий обзор
2. Для деталей смотрите [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)
3. Посмотрите диаграмму связей в DATABASE_SUMMARY.md

**Время:** 15-30 минут

---

## 📊 Структура базы данных (кратко)

```
18 таблиц:
├── 2 таблицы аутентификации (users, audit_logs)
├── 10 основных таблиц (farms, fields, operations, ...)
├── 3 расширенные таблицы (gps_tracks, satellite_data, ...)
└── 3 справочника (ref_crops, ref_fertilizers, ref_pesticides)

Главный ключ: farms.bin (UNIQUE)
    ↓
Связывает через farm_id:
    ├── users (пользователи хозяйства)
    ├── fields (поля хозяйства)
    ├── operations (операции на полях)
    ├── weather_data (погода)
    └── machinery (техника)
```

---

## 🔑 Критически важные элементы

### Уникальные ключи (UNIQUE)
- ✅ `farms.bin` - БИН хозяйства (12 цифр)
- ✅ `users.username` - имя пользователя
- ✅ `users.email` - email
- ✅ `fields.field_code` - код поля

### Составные ключи (предотвращение дубликатов)
- ✅ `economic_data(field_id, year, crop)`
- ✅ `weather_data(farm_id, datetime)`
- ✅ `satellite_data(field_id, acquisition_date, satellite_source)`

### Индексы (производительность)
- ✅ 40+ индексов на часто запрашиваемые поля

---

## 🚨 Частые проблемы и решения

### Проблема: "duplicate key value violates unique constraint"

**Причина:** Пытаетесь создать запись с существующим уникальным значением

**Решение:**
```sql
-- Найти дубликаты БИН
SELECT bin, COUNT(*) FROM farms GROUP BY bin HAVING COUNT(*) > 1;

-- Удалить дубликаты
DELETE FROM farms WHERE id NOT IN (SELECT MIN(id) FROM farms GROUP BY bin);
```

---

### Проблема: "column required_table does not exist"

**Причина:** Старая версия check_database_integrity.sql

**Решение:** Обновите файл из репозитория (уже исправлено)

---

### Проблема: Медленные запросы

**Причина:** Отсутствуют индексы

**Решение:** Выполните [supabase_improvements.sql](supabase_improvements.sql)

---

### Проблема: Сиротские записи (orphaned records)

**Причина:** Удалили хозяйство, но остались связанные записи

**Решение:**
```sql
-- Найти пользователей с несуществующими хозяйствами
SELECT u.* FROM users u
WHERE u.farm_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM farms f WHERE f.id = u.farm_id);

-- Исправить
UPDATE users SET farm_id = NULL
WHERE farm_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM farms WHERE id = farm_id);
```

---

## ✅ Чек-лист настройки

### Базовая настройка
- [ ] Создан проект в Supabase
- [ ] Получена строка подключения (DATABASE_URL)
- [ ] Обновлён .env файл
- [ ] Выполнен supabase_migration.sql
- [ ] Проверено: все 18 таблиц созданы

### Улучшения
- [ ] Выполнен quick_check.sql - нет дубликатов
- [ ] Очищены дубликаты (если были)
- [ ] Выполнен supabase_improvements.sql
- [ ] Проверено: уникальные ключи установлены
- [ ] Проверено: индексы созданы

### Тестирование
- [ ] Приложение запускается
- [ ] Регистрация нового пользователя работает
- [ ] Создание хозяйства работает
- [ ] Создание поля работает
- [ ] Создание операции работает
- [ ] Дубликаты БИН не создаются

### Production
- [ ] Настроено резервное копирование
- [ ] Настроен мониторинг
- [ ] Настроена Row Level Security (RLS)
- [ ] Проверены права доступа
- [ ] Задокументированы процедуры восстановления

---

## 📈 Размеры файлов

| Файл | Строк | Размер | Время чтения |
|------|-------|--------|-------------|
| quick_check.sql | 80 | 2 KB | 2 мин |
| SUPABASE_QUICKSTART.md | 300 | 10 KB | 5 мин |
| DATABASE_SUMMARY.md | 500 | 20 KB | 15 мин |
| supabase_improvements.sql | 380 | 15 KB | 5 мин (выполнение) |
| check_database_integrity.sql | 240 | 10 KB | 30 сек (выполнение) |
| supabase_migration.sql | 600 | 25 KB | 10 сек (выполнение) |
| DATABASE_SCHEMA.md | 1000 | 80 KB | 60 мин |

---

## 🔄 Обновление базы данных

### Если добавляются новые таблицы

1. Обновите DATABASE_SCHEMA.md
2. Добавьте CREATE TABLE в supabase_migration.sql
3. Добавьте индексы в supabase_improvements.sql
4. Обновите quick_check.sql
5. Обновите этот файл (README)

### Если изменяется структура существующих таблиц

1. Создайте миграционный скрипт (например: migration_v2_0_0.sql)
2. Обновите документацию
3. Протестируйте на копии базы
4. Примените в production

---

## 📞 Поддержка

**При возникновении проблем:**

1. 🔍 Выполните `quick_check.sql` или `check_database_integrity.sql`
2. 📖 Проверьте `DATABASE_SUMMARY.md` → раздел "Быстрая помощь"
3. 📖 Проверьте `SUPABASE_QUICKSTART.md` → раздел "Если что-то пошло не так"
4. 📧 Обратитесь к разработчику с результатами проверки

---

## 🎓 Дополнительные материалы

- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

---

**Последнее обновление:** 2025-01-20
**Версия базы данных:** 2.0.0
**Количество таблиц:** 18
