# 🚀 Инструкции по деплою улучшений

## 📦 Что было сделано

- ✅ 5 коммитов в ветке `feature/modern-stack`
- ✅ 9 страниц обновлено
- ✅ 2 новых справочника
- ✅ 1 новая страница (Укос)
- ✅ 1 новая таблица БД (mowing_details)
- ✅ Все изменения запушены на GitHub

---

## 🔄 Шаги для деплоя на Streamlit Cloud

### Шаг 1: Проверка ветки на GitHub

1. Открыть репозиторий: `https://github.com/YergZakon/sbor_apk`
2. Переключиться на ветку `feature/modern-stack`
3. Убедиться, что там 5 новых коммитов:
   - `feat: improve UX with optional sections and streamlined forms (Stage 1)`
   - `feat: add reference catalogs and smart selectors (Stage 2)`
   - `feat: add harvest implements and methods (Stage 4)`
   - `feat: add mowing page for forage crops (Stage 5)`
   - `feat: add database migration for mowing_details table`

---

### Шаг 2: Streamlit Cloud автоматически задеплоит

Streamlit Cloud следит за веткой `feature/modern-stack` и автоматически:
- Обнаружит новые коммиты
- Запустит повторный деплой
- Обновит приложение

**URL приложения:**
```
https://yergzakon-sbor-apk-feature-modern-stack-streamlit-app-app.streamlit.app/
```

**Проверка деплоя:**
1. Зайти в Streamlit Cloud Dashboard
2. Открыть приложение `sbor_apk`
3. Проверить статус деплоя (должно быть "Running")
4. Дождаться завершения (обычно 2-5 минут)

---

### Шаг 3: ⚠️ КРИТИЧНО - Применить миграцию БД

**Перед использованием новой страницы "Укос" необходимо создать таблицу в БД!**

#### Вариант 1: Через Supabase Dashboard (если используется Supabase)

1. Открыть Supabase Dashboard
2. Перейти в SQL Editor
3. Создать новый запрос
4. Скопировать содержимое файла `migrations/006_add_mowing_details_table.sql`
5. Выполнить запрос
6. Проверить, что таблица создана: `SELECT * FROM mowing_details LIMIT 1;`

#### Вариант 2: Через psql (если есть доступ)

```bash
# Установить переменную с URL базы данных
export DATABASE_URL="postgresql://user:password@host:port/database"

# Применить миграцию
psql $DATABASE_URL -f migrations/006_add_mowing_details_table.sql

# Проверить
psql $DATABASE_URL -c "SELECT * FROM mowing_details LIMIT 1;"
```

#### Вариант 3: Через pgAdmin или другой клиент

1. Подключиться к production БД
2. Открыть Query Tool
3. Скопировать содержимое `migrations/006_add_mowing_details_table.sql`
4. Выполнить
5. Проверить таблицу

#### Содержимое миграции:

```sql
BEGIN;

CREATE TABLE IF NOT EXISTS mowing_details (
    id SERIAL PRIMARY KEY,
    operation_id INTEGER NOT NULL REFERENCES operations(id) ON DELETE CASCADE UNIQUE,
    crop VARCHAR(100),
    mowing_number INTEGER,
    yield_green_mass_t_ha FLOAT,
    yield_hay_t_ha FLOAT,
    moisture_pct FLOAT,
    quality_class VARCHAR(20),
    harvest_phase VARCHAR(20),
    linked_operation_id INTEGER REFERENCES operations(id),
    plant_height_cm FLOAT,
    stubble_height_cm FLOAT
);

CREATE INDEX IF NOT EXISTS idx_mowing_details_operation_id ON mowing_details(operation_id);
CREATE INDEX IF NOT EXISTS idx_mowing_details_linked_operation_id ON mowing_details(linked_operation_id);
CREATE INDEX IF NOT EXISTS idx_mowing_details_harvest_phase ON mowing_details(harvest_phase);

COMMIT;
```

---

### Шаг 4: Проверка после деплоя

#### 4.1. Проверить загрузку справочников

1. Открыть приложение
2. Зайти на страницу "Посев"
3. Найти поле "Протравитель" - должен быть селектор с ~14 вариантами
4. Если видно текстовое поле или ошибка "Справочник не найден":
   - Проверить, что файлы есть в `streamlit_app/data/`
   - Проверить логи Streamlit Cloud

#### 4.2. Проверить новую страницу Укоса

1. В боковом меню должна появиться страница "17_🌿_Mowing"
2. Открыть её
3. Если ошибка про таблицу `mowing_details`:
   - ⚠️ Миграция БД не применена! Вернуться к Шагу 3

#### 4.3. Проверить все обновленные страницы

- [ ] Поля: expanders видны и работают
- [ ] Посев: протравитель = селектор
- [ ] СЗР: фаза развития = динамический селектор
- [ ] Десикация: препарат = селектор
- [ ] Уборка: жатка и способ уборки
- [ ] Снегозадержание: упрощенная форма
- [ ] Пар: упрощенная форма
- [ ] Укос: новая страница работает

---

## 🐛 Troubleshooting

### Проблема: "Справочник не найден"

**Причина:** Файлы `seed_treatments.json` или `growth_stages.json` не найдены

**Решение:**
1. Проверить наличие файлов:
   - `streamlit_app/data/seed_treatments.json`
   - `streamlit_app/data/growth_stages.json`
   - `shared/data/seed_treatments.json`
   - `shared/data/growth_stages.json`

2. Если файлов нет - возможно, коммит не задеплоился. Проверить:
   ```bash
   git log --oneline feature/modern-stack -5
   ```

3. Убедиться, что коммит `feat: add reference catalogs...` присутствует

---

### Проблема: Ошибка "relation mowing_details does not exist"

**Причина:** Миграция БД не применена

**Решение:**
1. Применить миграцию (см. Шаг 3)
2. Перезапустить приложение на Streamlit Cloud
3. Проверить снова

---

### Проблема: Старая версия кода после деплоя

**Причина:** Streamlit Cloud кэширует зависимости

**Решение:**
1. В Streamlit Cloud Dashboard нажать "Reboot app"
2. Или изменить `requirements.txt` (добавить пустую строку)
3. Или нажать "Clear cache" в меню приложения (⋮ → Clear cache)

---

### Проблема: Селектор не показывает информацию

**Причина:** Структура JSON не соответствует ожидаемой

**Решение:**
1. Проверить формат в файлах:
   - `seed_treatments.json` - должны быть ключи "действующее_вещество", "норма_применения"
   - `growth_stages.json` - должны быть ключи "фазы", "описание", "период"

2. Проверить кодировку файлов (должна быть UTF-8)

---

## 📊 Мониторинг

После деплоя отслеживать:

1. **Логи Streamlit Cloud:**
   - Нет ошибок импорта
   - Нет ошибок загрузки справочников
   - Нет ошибок БД

2. **Метрики использования:**
   - Сколько операций создается
   - Какие страницы используются чаще
   - Есть ли ошибки сохранения

3. **База данных:**
   - Размер таблицы `mowing_details` растет
   - Связи `linked_operation_id` корректны
   - Нет NULL в обязательных полях

---

## 🔙 Откат изменений (если нужно)

### Откатить миграцию БД:

```sql
-- Или через файл
psql $DATABASE_URL -f migrations/006_add_mowing_details_table_ROLLBACK.sql

-- Или напрямую
DROP TABLE IF EXISTS mowing_details CASCADE;
```

### Откатить код на предыдущую версию:

```bash
# На GitHub создать новый коммит, откатывающий изменения
git revert 44a8aad  # Откат миграции
git revert 8d3d2c8  # Откат страницы Mowing
# И т.д. для остальных коммитов

# Или переключиться на commit до изменений
git checkout b8625db
git push origin feature/modern-stack --force
```

**⚠️ ВАЖНО:** Откат миграции приведет к потере всех данных в `mowing_details`!

---

## ✅ Чеклист успешного деплоя

- [ ] GitHub: 5 новых коммитов в feature/modern-stack
- [ ] Streamlit Cloud: деплой завершен успешно
- [ ] БД: миграция 006 применена
- [ ] БД: таблица mowing_details создана
- [ ] Приложение: открывается без ошибок
- [ ] Справочники: seed_treatments.json загружен
- [ ] Справочники: growth_stages.json загружен
- [ ] Страница "Укос": доступна и работает
- [ ] Все обновленные страницы: работают корректно
- [ ] Тестовые данные: создаются и сохраняются

---

## 📞 Контакты при проблемах

Если что-то не работает:
1. Проверить логи Streamlit Cloud
2. Проверить структуру БД: `\d mowing_details`
3. Проверить наличие файлов справочников
4. Посмотреть файл `TESTING_CHECKLIST.md` для детального тестирования
