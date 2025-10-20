# Краткая сводка структуры базы данных

## 📊 Общая статистика

- **Всего таблиц:** 18
- **Основных таблиц:** 10
- **Справочных таблиц:** 3
- **Расширенных таблиц:** 3
- **Служебных таблиц:** 2

## 🔑 Критически важные уникальные ключи

### Главный бизнес-ключ:
- **farms.bin** - БИН/ИИН хозяйства (12 цифр, UNIQUE)
  - Связывает все данные системы через farm_id
  - Должен быть уникальным для каждого хозяйства

### Другие уникальные ключи:
- **users.username** - имя пользователя (UNIQUE)
- **users.email** - email пользователя (UNIQUE)
- **fields.field_code** - код поля (UNIQUE)
- **ref_crops.crop_name** - название культуры (UNIQUE)
- **ref_fertilizers.name** - название удобрения (UNIQUE)

## 🔗 Ключевые связи

```
farms (центр системы)
│
├── users (farm_id → farms.id)
│   └── многие пользователи → одно хозяйство
│
├── fields (farm_id → farms.id)
│   ├── одно хозяйство → много полей
│   │
│   └── operations (field_id → fields.id)
│       ├── одно поле → много операций
│       │
│       ├── sowing_details (1:1)
│       ├── fertilizer_applications (1:M)
│       ├── pesticide_applications (1:M)
│       ├── harvest_data (1:1)
│       └── agrochemical_analyses (1:1)
│
├── weather_data (farm_id → farms.id)
│
└── machinery (farm_id → farms.id)
    ├── machinery_equipment (1:1)
    └── gps_tracks (1:M)
```

## 📁 Группы таблиц по функциональности

### 1. Аутентификация и безопасность
- `users` - пользователи системы
- `audit_logs` - журнал всех действий

### 2. Основная информация о хозяйстве
- `farms` - хозяйства (**центральная таблица**)
- `fields` - поля с почвенными данными
- `machinery` - техника
- `machinery_equipment` - GPS/RTK оснащение

### 3. Агрономические операции
- `operations` - все виды операций
- `sowing_details` - детали посева
- `fertilizer_applications` - внесение удобрений
- `pesticide_applications` - применение СЗР
- `harvest_data` - данные уборки
- `agrochemical_analyses` - почвенные анализы

### 4. Мониторинг и аналитика
- `phytosanitary_monitoring` - болезни/вредители/сорняки
- `satellite_data` - NDVI/EVI индексы
- `gps_tracks` - треки техники
- `weather_data` - погодные данные

### 5. Экономика
- `economic_data` - затраты и доходность

### 6. Справочники
- `ref_crops` - культуры
- `ref_fertilizers` - удобрения
- `ref_pesticides` - СЗР

## ⚙️ Важные настройки

### CASCADE DELETE
При удалении хозяйства автоматически удаляются:
- Все поля (fields)
- Все операции (operations)
- Все связанные данные операций
- Погодные данные (weather_data)
- Техника и GPS-треки

### SET NULL
При удалении хозяйства НЕ удаляются пользователи:
- `users.farm_id` устанавливается в NULL
- Пользователь может быть привязан к другому хозяйству

## 📝 Рекомендованные улучшения

### Обязательные (применить в production):

1. **Уникальные ключи** ✅
   ```sql
   ALTER TABLE farms ADD CONSTRAINT farms_bin_unique UNIQUE (bin);
   ALTER TABLE users ADD CONSTRAINT users_username_unique UNIQUE (username);
   ALTER TABLE users ADD CONSTRAINT users_email_unique UNIQUE (email);
   ALTER TABLE fields ADD CONSTRAINT fields_field_code_unique UNIQUE (field_code);
   ```

2. **Составные ключи** ✅
   ```sql
   ALTER TABLE economic_data ADD CONSTRAINT uk_economic_data UNIQUE (field_id, year, crop);
   ALTER TABLE weather_data ADD CONSTRAINT uk_weather_data UNIQUE (farm_id, datetime);
   ALTER TABLE satellite_data ADD CONSTRAINT uk_satellite_data UNIQUE (field_id, acquisition_date, satellite_source);
   ```

3. **Индексы** ✅
   - На farm_id во всех таблицах
   - На датах операций
   - На типах операций

4. **CHECK Constraints** ✅
   - БИН должен быть 12 символов
   - Площади >= 0
   - Роль в ('admin', 'farmer', 'viewer')
   - NDVI между -1 и 1

### Опциональные (для масштабирования):

1. **Партиционирование** больших таблиц:
   - `gps_tracks` по датам
   - `weather_data` по месяцам
   - `operations` по годам

2. **Архивация** старых данных:
   - Перенос данных старше 3 лет в архив
   - Сжатие GPS-треков

## 🚀 Производительность

### Быстрые запросы (с индексами):
```sql
-- Получить хозяйство по БИН
SELECT * FROM farms WHERE bin = '123456789012';

-- Получить все поля хозяйства
SELECT * FROM fields WHERE farm_id = 1;

-- Операции за период
SELECT * FROM operations
WHERE farm_id = 1 AND operation_date BETWEEN '2024-01-01' AND '2024-12-31';
```

### Оптимизированные JOIN'ы:
```sql
-- Все операции с полями и хозяйствами (через view)
SELECT * FROM v_operations_summary WHERE farm_bin = '123456789012';

-- Статистика по хозяйству
SELECT * FROM v_farm_statistics WHERE bin = '123456789012';
```

## 🔒 Безопасность

### Row Level Security (RLS)
- Фермеры видят только свое хозяйство
- Администраторы видят все
- Неавторизованные пользователи не видят ничего

### Аудит
Все действия логируются в `audit_logs`:
- Кто (user_id)
- Что (action: create/update/delete)
- Когда (created_at)
- С каким IP (ip_address)

## 📦 Файлы в проекте

1. **DATABASE_SCHEMA.md** - полная документация (подробная)
2. **DATABASE_SUMMARY.md** - краткая сводка (этот файл)
3. **supabase_migration.sql** - создание всех таблиц
4. **supabase_improvements.sql** - добавление ограничений и индексов
5. **check_database_integrity.sql** - проверка целостности БД
6. **SUPABASE_SETUP.md** - пошаговая инструкция

## ✅ Чек-лист для production

- [ ] Выполнить `supabase_migration.sql`
- [ ] Выполнить `check_database_integrity.sql`
- [ ] Очистить дубликаты (если есть)
- [ ] Выполнить `supabase_improvements.sql`
- [ ] Настроить Row Level Security
- [ ] Настроить резервное копирование
- [ ] Добавить мониторинг производительности
- [ ] Протестировать все операции CRUD
- [ ] Проверить каскадное удаление
- [ ] Настроить аудит действий

## 🆘 Быстрая помощь

### Проблема: Дубликаты БИН
```sql
-- Найти дубликаты
SELECT bin, COUNT(*) FROM farms GROUP BY bin HAVING COUNT(*) > 1;

-- Удалить дубликаты (оставить первый)
DELETE FROM farms WHERE id NOT IN (
    SELECT MIN(id) FROM farms GROUP BY bin
);
```

### Проблема: Сиротские записи
```sql
-- Найти пользователей с несуществующими хозяйствами
SELECT u.* FROM users u
WHERE u.farm_id IS NOT NULL
    AND NOT EXISTS (SELECT 1 FROM farms f WHERE f.id = u.farm_id);

-- Исправить (установить farm_id в NULL)
UPDATE users SET farm_id = NULL
WHERE farm_id IS NOT NULL
    AND NOT EXISTS (SELECT 1 FROM farms f WHERE f.id = farm_id);
```

### Проблема: Медленные запросы
```sql
-- Анализ медленных запросов в Supabase
-- Dashboard → Reports → Database → Slow Queries

-- Добавить недостающий индекс
CREATE INDEX idx_custom ON table_name(column_name);
```

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи в Supabase Dashboard
2. Выполните `check_database_integrity.sql`
3. Проверьте DATABASE_SCHEMA.md для понимания связей
4. Обратитесь к разработчику системы
