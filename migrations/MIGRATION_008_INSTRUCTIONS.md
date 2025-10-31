# Migration 008: Add crop_name to phytosanitary_monitoring

## Описание
Добавление колонки `crop_name` в таблицу `phytosanitary_monitoring` для хранения названия культуры при фитосанитарном обследовании.

## Причина
Модуль фитосанитарного мониторинга позволяет выбирать культуру из справочника в форме, но эта информация не сохранялась в базе данных. Теперь культура сохраняется и отображается в истории обследований.

## Изменения в коде
1. **database.py**: Добавлено поле `crop_name = Column(String(100))` в модель `PhytosanitaryMonitoring`
2. **Фитосанитария.py**:
   - Импортирован `load_crops()` из `reference_loader`
   - Заменен `st.text_input` на `st.selectbox` для выбора культуры из справочника
   - Добавлен параметр `crop_name=crop` при создании записи мониторинга
   - Добавлена колонка "Культура" в таблицу истории

## Применение миграции на Supabase

### Шаг 1: Войдите в Supabase Dashboard
1. Откройте https://supabase.com/dashboard
2. Выберите свой проект
3. Перейдите в SQL Editor

### Шаг 2: Выполните миграцию
Скопируйте и выполните содержимое файла `008_add_crop_name_to_phytosanitary.sql`:

```sql
BEGIN;

ALTER TABLE phytosanitary_monitoring
ADD COLUMN IF NOT EXISTS crop_name VARCHAR(100);

COMMENT ON COLUMN phytosanitary_monitoring.crop_name IS
    'Название культуры на момент обследования';

COMMIT;
```

### Шаг 3: Проверьте результат
Выполните проверочный запрос:

```sql
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'phytosanitary_monitoring'
  AND column_name = 'crop_name';
```

Ожидаемый результат:
```
column_name | data_type         | character_maximum_length
------------|-------------------|-------------------------
crop_name   | character varying | 100
```

### Шаг 4: Проверьте работу приложения
1. Перейдите на страницу "Фитосанитария"
2. Создайте новое обследование
3. Убедитесь, что культуру можно выбрать из выпадающего списка
4. Проверьте, что культура отображается в истории обследований

## Откат миграции (если необходимо)

⚠️ **ВНИМАНИЕ**: Откат удалит все данные о культурах из существующих записей!

Если необходимо откатить миграцию, выполните файл `008_add_crop_name_to_phytosanitary_rollback.sql`:

```sql
BEGIN;

ALTER TABLE phytosanitary_monitoring
DROP COLUMN IF EXISTS crop_name;

COMMIT;
```

## Влияние на существующие данные
- Существующие записи `phytosanitary_monitoring` получат значение `NULL` в колонке `crop_name`
- Это нормально и не нарушит работу приложения
- В истории для старых записей будет отображаться "-" вместо названия культуры

## Статус
- [x] Код обновлен
- [x] Миграция SQL создана
- [ ] Миграция применена на production (Supabase)
- [ ] Проверена работа на Streamlit Cloud

## Дата создания
2025-10-31
