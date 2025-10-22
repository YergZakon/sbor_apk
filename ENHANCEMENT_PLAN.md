# План улучшений системы Farm Data System

## Обзор улучшений

### 1. Расширение данных об операциях (общие поля)

Для ВСЕХ типов операций добавить:
- `end_date` (Дата окончания) - Date
- `machine_id` → расширить до работы с новой таблицей machinery
- `implement_id` (ID агрегата) - Integer, FK к implements
- `machine_year` (Год выпуска техники) - Integer
- `implement_year` (Год выпуска агрегата) - Integer
- `work_speed_kmh` (Скорость работы, км/ч) - Float

### 2. Расширение SowingDetail (Посев)

Новые поля:
- `seed_reproduction` (Репродукция семян: элита, первая, вторая и т.д.) - String
- `seed_origin_country` (Страна производства семян) - String
- `combined_with_fertilizer` (Комбинированный посев с удобрениями) - Boolean
- `fertilizer_name` (Название удобрения при комбинированном посеве) - String
- `fertilizer_rate_kg_ha` (Норма удобрения, кг/га) - Float

### 3. Разделение техники на 2 таблицы

#### Таблица `machinery` (Техника - трактора, комбайны, самоходные опрыскиватели)
- id
- farm_id
- machinery_type (tractor, combine, self_propelled_sprayer, drone, irrigation_system)
- brand (Марка)
- model (Модель)
- year (Год выпуска)
- registration_number (Гос. номер)
- engine_power_hp (Мощность двигателя, л.с.)
- fuel_type (Тип топлива)
- purchase_date (Дата приобретения)
- purchase_price (Цена покупки)
- current_value (Текущая стоимость)
- status (active, repair, sold, rented)
- notes
- created_at
- updated_at

#### Таблица `implements` (Агрегаты - сеялки, бороны, культиваторы, прицепные опрыскиватели)
- id
- farm_id
- implement_type (seeder, planter, plow, cultivator, harrow, disc, roller, sprayer_trailer, fertilizer_spreader)
- brand
- model
- year
- working_width_m (Рабочая ширина, м)
- purchase_date
- purchase_price
- current_value
- status (active, repair, sold, rented)
- notes
- created_at
- updated_at

### 4. Новые типы операций

#### 4.1 Desiccation (Десикация)
Новая таблица `desiccation_details`:
- operation_id
- product_name (Препарат)
- active_ingredient (Действующее вещество)
- rate_per_ha (Норма расхода)
- water_rate_l_ha (Расход воды)
- growth_stage (Фаза развития культуры)
- target_moisture_percent (Целевая влажность)
- temperature_c
- wind_speed_ms
- humidity_percent

#### 4.2 Tillage (Обработка почвы)
Новая таблица `tillage_details`:
- operation_id
- tillage_type (plowing, cultivation, harrowing, stubble_breaking, discing, deep_loosening, rolling)
- depth_cm (Глубина обработки)
- tillage_purpose (pre_sowing, post_harvest, weed_control, moisture_retention)

#### 4.3 Irrigation (Орошение)
Новая таблица `irrigation_details`:
- operation_id
- irrigation_type (sprinkler, drip, furrow, flood)
- water_volume_m3 (Объем воды, м3)
- water_rate_m3_ha (Норма полива, м3/га)
- water_source (Источник воды)
- soil_moisture_before_percent
- soil_moisture_after_percent

#### 4.4 Snow Retention (Снегозадержание)
Новая таблица `snow_retention_details`:
- operation_id
- method (snow_plowing, barriers, vegetation)
- snow_depth_before_cm
- snow_depth_after_cm

#### 4.5 Fallow Management (Пары)
Новая таблица `fallow_details`:
- operation_id
- fallow_type (black, early, green)
- processing_depth_cm
- weed_control_performed (Boolean)

### 5. Экономика - Аренда

Расширение таблицы `economic_data`:
- `field_rental_cost` (Стоимость аренды поля) - Float
- `field_rental_period` (Период аренды поля) - String
- `machinery_rental_cost` (Стоимость аренды техники) - Float
- `machinery_rental_type` (Тип аренды: почасовая, посменная, посезонная) - String
- `rented_machinery_description` (Описание арендованной техники) - Text

### 6. Урожайность - дата окончания

Добавить в `harvest_data`:
- Уже есть через `operation.end_date`

## Приоритеты внедрения

### Фаза 1 (Критичные улучшения):
1. ✅ Создать таблицы machinery и implements
2. ✅ Добавить общие поля в Operation (end_date, implement_id, work_speed_kmh)
3. ✅ Расширить SowingDetail
4. ✅ Добавить поля аренды в economic_data

### Фаза 2 (Новые операции):
5. ✅ Tillage (обработка почвы) - ПРИОРИТЕТ
6. ✅ Desiccation (десикация)
7. ✅ Irrigation (орошение)
8. ✅ Snow retention (снегозадержание)
9. ✅ Fallow management (пары)

### Фаза 3 (UI обновления):
10. Обновить все страницы операций с новыми полями
11. Создать страницу управления техникой и агрегатами
12. Обновить формы создания операций

## Техническая реализация

1. Создать SQL миграцию для всех изменений
2. Обновить models в database.py
3. Создать страницу Equipment Management (2 вкладки: Техника, Агрегаты)
4. Обновить формы операций
5. Обновить отчеты и аналитику
