# 🚀 Руководство по развертыванию системы АгроДанные КЗ

**Версия:** 2.0
**Дата обновления:** 25 октября 2025
**Статус:** Production Ready

---

## 📋 Содержание

1. [Быстрый старт](#быстрый-старт)
2. [Требования к системе](#требования-к-системе)
3. [Настройка базы данных](#настройка-базы-данных)
4. [Применение миграций](#применение-миграций)
5. [Развертывание на Streamlit Cloud](#развертывание-на-streamlit-cloud)
6. [Создание первого администратора](#создание-первого-администратора)
7. [Управление справочниками](#управление-справочниками)
8. [Мультихозяйственная система](#мультихозяйственная-система)
9. [Troubleshooting](#troubleshooting)

---

## 🚀 Быстрый старт

### Для локальной разработки:

```bash
# 1. Клонировать репозиторий
git clone https://github.com/YergZakon/sbor_apk.git
cd sbor_apk

# 2. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Настроить переменные окружения
# Создать файл .env с DATABASE_URL

# 5. Запустить приложение
streamlit run app.py
```

Приложение откроется на http://localhost:8501

---

## 💻 Требования к системе

### Минимальные требования:
- **Python:** 3.9+
- **RAM:** 512 MB
- **Disk:** 100 MB
- **PostgreSQL:** 12+ (Supabase рекомендуется)

### Зависимости:
```
streamlit>=1.28.0
pandas>=2.0.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
python-dotenv>=1.0.0
plotly>=5.14.0
folium>=0.14.0
streamlit-folium>=0.13.0
openpyxl>=3.1.0
```

---

## 🗄️ Настройка базы данных

### Вариант 1: Supabase (рекомендуется для production)

1. **Создать проект:**
   - Зайти на https://supabase.com
   - Создать новый проект
   - Выбрать регион (ближайший к Казахстану)
   - Задать надежный пароль

2. **Получить Database URL:**
   ```
   Project Settings → Database → Connection String → URI

   Формат:
   postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
   ```

3. **Настроить .env файл:**
   ```bash
   DATABASE_URL=postgresql://postgres:your_password@db.xxx.supabase.co:5432/postgres
   ```

### Вариант 2: Локальный PostgreSQL

```bash
# Создать базу данных
createdb farm_data

# Настроить .env
DATABASE_URL=postgresql://user:password@localhost:5432/farm_data
```

---

## 📦 Применение миграций

### ВАЖНО: Миграции применяются СТРОГО по порядку!

#### Миграция 002: Добавление типов агрегатов

**Файл:** `migrations/002_add_implement_types.sql`

**Что делает:**
- Добавляет типы агрегатов: header (жатки), mower (косилки), baler (пресс-подборщики)

**Применение:**
1. Откройте Supabase Dashboard → SQL Editor
2. Скопируйте содержимое `migrations/002_add_implement_types.sql`
3. Вставьте и нажмите RUN

```sql
BEGIN;

ALTER TABLE implements DROP CONSTRAINT IF EXISTS implements_implement_type_check;

ALTER TABLE implements ADD CONSTRAINT implements_implement_type_check
CHECK (implement_type IN (
    'seeder', 'planter', 'plow', 'cultivator', 'harrow', 'disc',
    'deep_loosener', 'roller', 'sprayer_trailer', 'fertilizer_spreader',
    'stubble_breaker', 'snow_plow',
    'header',  -- NEW
    'mower',   -- NEW
    'baler',   -- NEW
    'other'
));

COMMIT;
```

#### Миграция 003: Способ применения десикации

**Файл:** `migrations/003_add_desiccation_application_method.sql`

**Что делает:**
- Добавляет поле `application_method` в таблицу `desiccation_details`

```sql
BEGIN;

ALTER TABLE desiccation_details
ADD COLUMN IF NOT EXISTS application_method VARCHAR(100);

COMMENT ON COLUMN desiccation_details.application_method
IS 'Способ применения (Наземное/Авиационное опрыскивание)';

COMMIT;
```

#### Миграция 004: Дополнительные поля операций

**Файл:** `migrations/004_add_missing_operation_fields.sql`

**Что делает:**
- Добавляет `soil_moisture_before` в `irrigation_details`
- Добавляет `snow_depth_cm`, `number_of_passes` в `snow_retention_details`
- Добавляет `number_of_treatments` в `fallow_details`
- Добавляет `soil_moisture` в `tillage_details`

```sql
BEGIN;

-- irrigation_details
ALTER TABLE irrigation_details
ADD COLUMN IF NOT EXISTS soil_moisture_before FLOAT;

-- snow_retention_details
ALTER TABLE snow_retention_details
ADD COLUMN IF NOT EXISTS snow_depth_cm FLOAT;

ALTER TABLE snow_retention_details
ADD COLUMN IF NOT EXISTS number_of_passes INTEGER;

-- fallow_details
ALTER TABLE fallow_details
ADD COLUMN IF NOT EXISTS number_of_treatments INTEGER;

-- tillage_details
ALTER TABLE tillage_details
ADD COLUMN IF NOT EXISTS soil_moisture VARCHAR(50);

COMMIT;
```

#### Миграция 005: Мультихозяйственная система

**Файл:** `migrations/005_add_user_farms_table.sql`

**Что делает:**
- Создает таблицу `user_farms` для связи пользователей с несколькими хозяйствами
- Автоматически мигрирует существующие связи из `users.farm_id`
- Добавляет роли на уровне хозяйства (admin, manager, viewer)
- Поддержка первичного хозяйства (is_primary)

```sql
BEGIN;

-- Создание таблицы
CREATE TABLE IF NOT EXISTS user_farms (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    farm_id INTEGER NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'viewer',
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_user_farm UNIQUE (user_id, farm_id)
);

-- Индексы
CREATE INDEX IF NOT EXISTS idx_user_farms_user_id ON user_farms(user_id);
CREATE INDEX IF NOT EXISTS idx_user_farms_farm_id ON user_farms(farm_id);
CREATE INDEX IF NOT EXISTS idx_user_farms_is_primary ON user_farms(user_id, is_primary)
WHERE is_primary = TRUE;

-- Миграция существующих данных
INSERT INTO user_farms (user_id, farm_id, role, is_primary)
SELECT id, farm_id, role, TRUE
FROM users
WHERE farm_id IS NOT NULL
ON CONFLICT (user_id, farm_id) DO NOTHING;

COMMIT;
```

### Проверка успешности миграций:

```sql
-- Проверка таблицы user_farms
SELECT COUNT(*) as user_farm_links FROM user_farms;

-- Проверка новых полей в операциях
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'irrigation_details'
AND column_name = 'soil_moisture_before';

-- Проверка типов агрегатов
SELECT UNNEST(enum_range(NULL::implement_type)) AS implement_types;
```

---

## ☁️ Развертывание на Streamlit Cloud

### Шаг 1: Подготовка репозитория

```bash
# Убедитесь, что все изменения закоммичены
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Шаг 2: Создание приложения на Streamlit Cloud

1. Зайти на https://share.streamlit.io
2. Нажать **New app**
3. Выбрать репозиторий: `YergZakon/sbor_apk`
4. Branch: `main`
5. Main file: `app.py`
6. Нажать **Deploy**

### Шаг 3: Настройка Secrets

В Streamlit Cloud → App settings → Secrets:

```toml
DATABASE_URL = "postgresql://postgres:password@db.xxx.supabase.co:5432/postgres"
```

### Шаг 4: Перезапуск приложения

После добавления secrets нажать **Reboot app**

---

## 👤 Создание первого администратора

### Вариант 1: Через SQL (рекомендуется)

```sql
-- Вставить администратора напрямую в базу
INSERT INTO users (
    username,
    email,
    password_hash,
    full_name,
    role,
    is_active
) VALUES (
    'admin',
    'admin@example.com',
    'pbkdf2:sha256:600000$...',  -- Хэш пароля
    'Администратор Системы',
    'admin',
    TRUE
);
```

### Вариант 2: Через интерфейс (после деплоя)

1. Первый зарегистрированный пользователь автоматически становится админом
2. Или существующий админ создает нового через: Админка → Создать пользователя

---

## 📚 Управление справочниками

Система включает 16 справочных каталогов в формате JSON:

### Сельскохозяйственные справочники:
1. **crops.json** - Культуры и сорта
2. **diseases.json** - Болезни растений
3. **pests.json** - Вредители
4. **weeds.json** - Сорняки
5. **soil_types.json** - Типы почв

### Техника:
6. **tractors.json** - Тракторы
7. **combines.json** - Комбайны
8. **implements.json** - Агрегаты

### Агрохимия:
9. **pesticides.json** - Пестициды
10. **fertilizers.json** - Удобрения
11. **active_ingredients.json** - Действующие вещества
12. **pesticide_classes.json** - Классы препаратов
13. **fertilizer_categories.json** - Категории удобрений
14. **desiccation_products.json** - Десиканты

### Прочее:
15. **countries.json** - Страны происхождения
16. **seed_reproductions.json** - Репродукции семян

### Редактирование справочников:

**Через интерфейс (для админов):**
- Страница: **📚 Справочники** (pages/99_📚_References.py)
- 4 вкладки: Просмотр, Добавить, Редактировать, Импорт/Экспорт

**Через файлы:**
```bash
# Редактировать JSON файлы напрямую
nano data/crops.json

# Закоммитить изменения
git add data/
git commit -m "Update crop varieties"
git push
```

---

## 🏢 Мультихозяйственная система

### Архитектура:

**Таблица `user_farms`:**
- Связь многие-ко-многим между пользователями и хозяйствами
- Роли на уровне хозяйства: `admin`, `manager`, `viewer`
- Флаг `is_primary` для основного хозяйства

### Назначение пользователей на хозяйства:

1. **Админка** → **🏢 Назначение на хозяйства**
2. Выбрать пользователя
3. Добавить хозяйство с ролью
4. Отметить как первичное (опционально)

### Роли на уровне хозяйства:

| Роль | Права |
|------|-------|
| **👑 admin** | Полный доступ к хозяйству |
| **👔 manager** | Редактирование данных |
| **👁️ viewer** | Только просмотр |

### Переключение между хозяйствами:

Если у пользователя несколько хозяйств, в интерфейсе появится селектор для выбора текущего хозяйства.

---

## 🔧 Troubleshooting

### Проблема: Ошибка подключения к БД

**Симптомы:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Решение:**
1. Проверить DATABASE_URL в secrets/env
2. Проверить firewall в Supabase (разрешить все IP или 0.0.0.0/0)
3. Проверить пароль (специальные символы нужно экранировать)

### Проблема: IntegrityError при добавлении поля

**Симптомы:**
```
IntegrityError: duplicate key value violates unique constraint "fields_field_code_key"
```

**Решение:**
- Исправлено в последнем коммите (dbafba1)
- Перезапустить приложение на Streamlit Cloud

### Проблема: DetachedInstanceError

**Симптомы:**
```
sqlalchemy.exc.InvalidRequestError: Instance is not bound to a Session
```

**Решение:**
- Исправлено в коммите 7d3f99d
- Обновить код с GitHub

### Проблема: Миграция не применяется

**Симптомы:**
```
ERROR: relation "user_farms" already exists
```

**Решение:**
1. Проверить, не применена ли миграция уже:
   ```sql
   SELECT * FROM information_schema.tables WHERE table_name = 'user_farms';
   ```
2. Если таблица существует, миграция уже применена
3. Если нужен откат, использовать `*_ROLLBACK.sql` файл

### Проблема: Не могу удалить поле

**Симптомы:**
```
❌ Невозможно удалить поле: есть связанные данные (5 операций)
```

**Решение:**
- Это правильное поведение!
- Сначала удалите все операции, связанные с полем
- Или используйте CASCADE в SQL (не рекомендуется)

---

## 📞 Поддержка

**GitHub:** https://github.com/YergZakon/sbor_apk
**Issues:** https://github.com/YergZakon/sbor_apk/issues
**Production URL:** https://sbor-apk.streamlit.app

---

## 📝 Changelog

### Version 2.0 (25 октября 2025)
- ✅ Добавлена мультихозяйственная поддержка
- ✅ Создана страница управления справочниками
- ✅ Добавлено 7 новых справочников
- ✅ Исправлены ошибки удаления полей
- ✅ Исправлена генерация field_code
- ✅ Добавлены миграции 002-005

### Version 1.0 (22 октября 2025)
- ✅ Базовая система сбора данных
- ✅ 10 типов операций
- ✅ Справочники техники
- ✅ Импорт/экспорт данных
- ✅ Система авторизации

---

**Готовы к деплою!** 🚀
