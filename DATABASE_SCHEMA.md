# Схема базы данных - Farm Data System

## Обзор

Система содержит **18 таблиц**, разделенных на 4 категории:
1. **Аутентификация и авторизация** (2 таблицы)
2. **Основные таблицы** (10 таблиц)
3. **Новые расширенные таблицы** (3 таблицы)
4. **Справочные таблицы** (3 таблицы)

---

## 1. АУТЕНТИФИКАЦИЯ И АВТОРИЗАЦИЯ

### 1.1 users (Пользователи)
**Назначение:** Хранение данных пользователей системы

**Поля:**
- `id` - INTEGER, PRIMARY KEY, INDEX
- `username` - VARCHAR(50), **UNIQUE**, NOT NULL, INDEX
- `email` - VARCHAR(100), **UNIQUE**, NOT NULL, INDEX
- `hashed_password` - VARCHAR(255), NOT NULL
- `full_name` - VARCHAR(200)
- `role` - VARCHAR(20), NOT NULL, DEFAULT 'farmer' (admin/farmer/viewer)
- `is_active` - BOOLEAN, DEFAULT TRUE
- `farm_id` - INTEGER, **FOREIGN KEY** → farms.id, NULLABLE
- `created_at` - DATETIME, DEFAULT NOW()
- `updated_at` - DATETIME, DEFAULT NOW(), ON UPDATE NOW()
- `last_login` - DATETIME

**Уникальные ключи:**
- `username` (UNIQUE)
- `email` (UNIQUE)

**Внешние ключи:**
- `farm_id` → `farms.id` (связь многие-к-одному)

**Связи:**
- farm (ONE) ← User → Farm

---

### 1.2 audit_logs (Журнал аудита)
**Назначение:** Логирование всех действий пользователей

**Поля:**
- `id` - INTEGER, PRIMARY KEY, INDEX
- `user_id` - INTEGER, **FOREIGN KEY** → users.id, NOT NULL
- `action` - VARCHAR(100), NOT NULL (login/logout/create/update/delete)
- `entity_type` - VARCHAR(50) (farm/field/operation/etc.)
- `entity_id` - INTEGER
- `details` - TEXT (JSON)
- `ip_address` - VARCHAR(50)
- `created_at` - DATETIME, DEFAULT NOW()

**Внешние ключи:**
- `user_id` → `users.id`

---

## 2. ОСНОВНЫЕ ТАБЛИЦЫ

### 2.1 farms (Хозяйства)
**Назначение:** Центральная таблица - хозяйства (фермы)

**Поля:**
- `id` - INTEGER, PRIMARY KEY, INDEX
- `bin` - VARCHAR(12), **UNIQUE**, NOT NULL, INDEX (БИН/ИИН)
- `name` - VARCHAR(255), NOT NULL
- `director_name` - VARCHAR(255)
- `phone` - VARCHAR(20)
- `email` - VARCHAR(100)
- `address` - TEXT
- `region` - VARCHAR(100) (Область)
- `district` - VARCHAR(100) (Район)
- `village` - VARCHAR(100) (Населенный пункт)
- `farm_type` - VARCHAR(50)
- `founded_year` - INTEGER
- `total_area_ha` - FLOAT
- `arable_area_ha` - FLOAT
- `fallow_area_ha` - FLOAT
- `pasture_area_ha` - FLOAT
- `hayfield_area_ha` - FLOAT
- `center_lat` - FLOAT
- `center_lon` - FLOAT
- `created_at` - DATETIME, DEFAULT NOW()
- `updated_at` - DATETIME, DEFAULT NOW(), ON UPDATE NOW()

**Уникальные ключи:**
- `bin` (UNIQUE) - **КРИТИЧЕСКИ ВАЖНО!**

**Связи:**
- fields (MANY) ← Farm → Field
- users (MANY) ← Farm → User

---

### 2.2 fields (Поля)
**Назначение:** Поля хозяйства

**Поля:**
- `id` - INTEGER, PRIMARY KEY, INDEX
- `farm_id` - INTEGER, **FOREIGN KEY** → farms.id, NOT NULL
- `field_code` - VARCHAR(20), **UNIQUE**, NOT NULL, INDEX
- `name` - VARCHAR(100)
- `cadastral_number` - VARCHAR(50)
- `area_ha` - FLOAT, NOT NULL
- `center_lat` - FLOAT
- `center_lon` - FLOAT
- `soil_type` - VARCHAR(100)
- `soil_texture` - VARCHAR(50)
- `ph_water` - FLOAT
- `humus_pct` - FLOAT
- `p2o5_mg_kg` - FLOAT
- `k2o_mg_kg` - FLOAT
- `relief` - VARCHAR(50)
- `slope_degree` - FLOAT
- `drainage` - VARCHAR(50)
- `last_analysis_year` - INTEGER
- `created_at` - DATETIME, DEFAULT NOW()

**Уникальные ключи:**
- `field_code` (UNIQUE)

**Внешние ключи:**
- `farm_id` → `farms.id` (CASCADE DELETE)

**Связи:**
- farm (ONE) ← Field → Farm
- operations (MANY) ← Field → Operation

---

### 2.3 operations (Операции)
**Назначение:** Сельскохозяйственные операции

**Поля:**
- `id` - INTEGER, PRIMARY KEY, INDEX
- `farm_id` - INTEGER, **FOREIGN KEY** → farms.id, NOT NULL
- `field_id` - INTEGER, **FOREIGN KEY** → fields.id, NOT NULL
- `operation_type` - VARCHAR(50), NOT NULL (sowing/fertilizing/spraying/harvest/soil_analysis)
- `operation_date` - DATE, NOT NULL
- `crop` - VARCHAR(100)
- `variety` - VARCHAR(100)
- `area_processed_ha` - FLOAT
- `machine_id` - INTEGER
- `operator` - VARCHAR(100)
- `weather_conditions` - TEXT
- `notes` - TEXT
- `created_at` - DATETIME, DEFAULT NOW()

**Внешние ключи:**
- `farm_id` → `farms.id`
- `field_id` → `fields.id` (CASCADE DELETE)

**Связи:**
- field (ONE) ← Operation → Field
- sowing_details (ONE) ← Operation → SowingDetail
- fertilizer_applications (MANY) ← Operation → FertilizerApplication
- pesticide_applications (MANY) ← Operation → PesticideApplication
- harvest_data (ONE) ← Operation → HarvestData
- agrochemical_analysis (ONE) ← Operation → AgrochemicalAnalysis

---

### 2.4 sowing_details (Детали посева)
**Назначение:** Подробные данные о посеве

**Поля:**
- `id` - INTEGER, PRIMARY KEY, INDEX
- `operation_id` - INTEGER, **FOREIGN KEY** → operations.id, NOT NULL
- `crop` - VARCHAR(100), NOT NULL
- `variety` - VARCHAR(100)
- `seeding_rate_kg_ha` - FLOAT
- `seeding_depth_cm` - FLOAT
- `row_spacing_cm` - FLOAT
- `seed_treatment` - VARCHAR(100)
- `soil_temp_c` - FLOAT
- `soil_moisture_percent` - FLOAT
- `total_seeds_kg` - FLOAT

**Внешние ключи:**
- `operation_id` → `operations.id` (CASCADE DELETE)

**Связь:** ONE-TO-ONE с operations

---

### 2.5 fertilizer_applications (Внесение удобрений)
**Назначение:** Данные о внесении удобрений

**Поля:**
- `id` - INTEGER, PRIMARY KEY, INDEX
- `operation_id` - INTEGER, **FOREIGN KEY** → operations.id, NOT NULL
- `fertilizer_name` - VARCHAR(100), NOT NULL
- `fertilizer_type` - VARCHAR(50)
- `rate_kg_ha` - FLOAT
- `total_fertilizer_kg` - FLOAT
- `n_content_percent` - FLOAT
- `p_content_percent` - FLOAT
- `k_content_percent` - FLOAT
- `n_applied_kg` - FLOAT
- `p_applied_kg` - FLOAT
- `k_applied_kg` - FLOAT
- `application_method` - VARCHAR(50)
- `application_purpose` - VARCHAR(50)

**Внешние ключи:**
- `operation_id` → `operations.id` (CASCADE DELETE)

**Связь:** MANY-TO-ONE с operations

---

### 2.6 pesticide_applications (Применение СЗР)
**Назначение:** Данные о применении средств защиты растений

**Поля:**
- `id` - INTEGER, PRIMARY KEY, INDEX
- `operation_id` - INTEGER, **FOREIGN KEY** → operations.id, NOT NULL
- `pesticide_name` - VARCHAR(100), NOT NULL
- `pesticide_class` - VARCHAR(50)
- `active_ingredient` - VARCHAR(200)
- `rate_per_ha` - FLOAT
- `total_product_used` - FLOAT
- `water_rate_l_ha` - FLOAT
- `application_method` - VARCHAR(50)
- `treatment_target` - VARCHAR(100)
- `growth_stage` - VARCHAR(100)
- `temperature_c` - FLOAT
- `wind_speed_ms` - FLOAT
- `humidity_percent` - FLOAT
- `waiting_period_days` - INTEGER

**Внешние ключи:**
- `operation_id` → `operations.id` (CASCADE DELETE)

**Связь:** MANY-TO-ONE с operations

---

### 2.7 harvest_data (Данные уборки)
**Назначение:** Данные об урожае

**Поля:**
- `id` - INTEGER, PRIMARY KEY, INDEX
- `operation_id` - INTEGER, **FOREIGN KEY** → operations.id, NOT NULL
- `crop` - VARCHAR(100)
- `variety` - VARCHAR(100)
- `yield_t_ha` - FLOAT
- `total_yield_t` - FLOAT
- `moisture_percent` - FLOAT
- `protein_percent` - FLOAT
- `gluten_percent` - FLOAT
- `test_weight_g_l` - FLOAT
- `falling_number` - INTEGER
- `weed_content_percent` - FLOAT
- `oil_content_percent` - FLOAT
- `quality_class` - INTEGER

**Внешние ключи:**
- `operation_id` → `operations.id` (CASCADE DELETE)

**Связь:** ONE-TO-ONE с operations

---

### 2.8 agrochemical_analyses (Агрохимические анализы)
**Назначение:** Результаты почвенных анализов

**Поля:**
- `id` - INTEGER, PRIMARY KEY, INDEX
- `operation_id` - INTEGER, **FOREIGN KEY** → operations.id, NOT NULL
- `sample_depth_cm` - INTEGER
- `sample_location` - VARCHAR(100)
- `ph_water` - FLOAT
- `ph_salt` - FLOAT
- `humus_percent` - FLOAT
- `nitrogen_total_percent` - FLOAT
- `p2o5_mg_kg` - FLOAT
- `k2o_mg_kg` - FLOAT
- `mobile_s_mg_kg` - FLOAT
- `no3_mg_kg` - FLOAT
- `nh4_mg_kg` - FLOAT
- `ec_ds_m` - FLOAT
- `cec_cmol_kg` - FLOAT
- `ca_mg_kg` - FLOAT
- `mg_mg_kg` - FLOAT
- `na_mg_kg` - FLOAT
- `zn_mg_kg` - FLOAT
- `cu_mg_kg` - FLOAT
- `fe_mg_kg` - FLOAT
- `mn_mg_kg` - FLOAT
- `b_mg_kg` - FLOAT
- `sand_pct` - FLOAT
- `silt_pct` - FLOAT
- `clay_pct` - FLOAT
- `lab_name` - VARCHAR(200)
- `analysis_method` - VARCHAR(100)
- `notes` - TEXT

**Внешние ключи:**
- `operation_id` → `operations.id` (CASCADE DELETE)

**Связь:** ONE-TO-ONE с operations

---

### 2.9 economic_data (Экономические данные)
**Назначение:** Экономика по полям

**Поля:**
- `id` - INTEGER, PRIMARY KEY, INDEX
- `field_id` - INTEGER, **FOREIGN KEY** → fields.id, NOT NULL
- `year` - INTEGER, NOT NULL
- `crop` - VARCHAR(100)
- `area_ha` - FLOAT
- `seeds_cost_kzt_ha` - FLOAT
- `fertilizers_cost_kzt_ha` - FLOAT
- `pesticides_cost_kzt_ha` - FLOAT
- `fuel_cost_kzt_ha` - FLOAT
- `labor_cost_kzt_ha` - FLOAT
- `other_costs_kzt_ha` - FLOAT
- `total_costs_kzt_ha` - FLOAT
- `yield_t_ha` - FLOAT
- `selling_price_kzt_t` - FLOAT
- `revenue_kzt_ha` - FLOAT
- `profit_kzt_ha` - FLOAT
- `profitability_pct` - FLOAT
- `notes` - TEXT

**Внешние ключи:**
- `field_id` → `fields.id` (CASCADE DELETE)

**Рекомендация:** Добавить составной уникальный ключ `(field_id, year, crop)`

---

### 2.10 weather_data (Метеоданные)
**Назначение:** Погодные данные

**Поля:**
- `id` - INTEGER, PRIMARY KEY, INDEX
- `farm_id` - INTEGER, **FOREIGN KEY** → farms.id
- `datetime` - DATETIME, NOT NULL
- `temp_air_c` - FLOAT
- `temp_min_c` - FLOAT
- `temp_max_c` - FLOAT
- `precipitation_mm` - FLOAT
- `humidity_pct` - FLOAT
- `wind_speed_ms` - FLOAT
- `wind_direction` - VARCHAR(20)
- `solar_radiation_wm2` - FLOAT
- `pressure_hpa` - FLOAT
- `temp_soil_5cm_c` - FLOAT
- `temp_soil_10cm_c` - FLOAT
- `soil_moisture_pct` - FLOAT
- `evapotranspiration_mm` - FLOAT
- `notes` - TEXT

**Внешние ключи:**
- `farm_id` → `farms.id` (CASCADE DELETE)

**Рекомендация:** Добавить составной уникальный ключ `(farm_id, datetime)`

---

### 2.11 machinery (Техника)
**Назначение:** Техника хозяйства

**Поля:**
- `id` - INTEGER, PRIMARY KEY, INDEX
- `farm_id` - INTEGER, **FOREIGN KEY** → farms.id, NOT NULL
- `machine_type` - VARCHAR(100)
- `brand` - VARCHAR(100)
- `model` - VARCHAR(100)
- `year` - INTEGER
- `registration_number` - VARCHAR(50)
- `status` - VARCHAR(50)
- `notes` - TEXT

**Внешние ключи:**
- `farm_id` → `farms.id` (CASCADE DELETE)

**Связи:**
- equipment (ONE) ← Machinery → MachineryEquipment

**Рекомендация:** Добавить уникальный ключ `registration_number` (если применимо)

---

## 3. НОВЫЕ РАСШИРЕННЫЕ ТАБЛИЦЫ

### 3.1 phytosanitary_monitoring (Фитосанитарный мониторинг)
**Назначение:** Мониторинг болезней, вредителей, сорняков

**Поля:**
- `id` - INTEGER, PRIMARY KEY, INDEX
- `field_id` - INTEGER, **FOREIGN KEY** → fields.id, NOT NULL
- `inspection_date` - DATE, NOT NULL
- `pest_type` - VARCHAR(50), NOT NULL (disease/pest/weed)
- `pest_name` - VARCHAR(200), NOT NULL
- `latin_name` - VARCHAR(200)
- `severity_pct` - FLOAT (0-100)
- `prevalence_pct` - FLOAT (0-100)
- `intensity_score` - INTEGER (1-5)
- `threshold_exceeded` - BOOLEAN
- `crop_stage` - VARCHAR(100)
- `control_measures` - TEXT
- `control_effectiveness_pct` - FLOAT
- `photo_url` - VARCHAR(500)
- `gps_lat` - FLOAT
- `gps_lon` - FLOAT
- `forecast` - TEXT
- `notes` - TEXT
- `created_at` - DATETIME, DEFAULT NOW()

**Внешние ключи:**
- `field_id` → `fields.id` (CASCADE DELETE)

---

### 3.2 gps_tracks (GPS-треки)
**Назначение:** Треки движения техники

**Поля:**
- `id` - INTEGER, PRIMARY KEY, INDEX
- `datetime` - DATETIME, NOT NULL, INDEX
- `latitude` - FLOAT, NOT NULL
- `longitude` - FLOAT, NOT NULL
- `altitude_m` - FLOAT
- `machine_id` - INTEGER, **FOREIGN KEY** → machinery.id
- `operation_type` - VARCHAR(50)
- `speed_kmh` - FLOAT
- `heading_deg` - FLOAT
- `field_id` - INTEGER, **FOREIGN KEY** → fields.id
- `created_at` - DATETIME, DEFAULT NOW()

**Внешние ключи:**
- `machine_id` → `machinery.id` (CASCADE DELETE)
- `field_id` → `fields.id` (SET NULL)

**Рекомендация:** Добавить индекс на `(machine_id, datetime)` для быстрых запросов

---

### 3.3 machinery_equipment (Техническая оснащенность)
**Назначение:** GPS/RTK/Автопилот на технике

**Поля:**
- `id` - INTEGER, PRIMARY KEY, INDEX
- `machine_id` - INTEGER, **FOREIGN KEY** → machinery.id, NOT NULL
- `has_gps` - BOOLEAN, DEFAULT FALSE
- `gps_type` - VARCHAR(50) (RTK/DGPS/Standard)
- `accuracy_cm` - FLOAT
- `gps_manufacturer` - VARCHAR(100)
- `gps_model` - VARCHAR(100)
- `has_autopilot` - BOOLEAN, DEFAULT FALSE
- `rtk_station_type` - VARCHAR(50) (Local/Network/None)
- `rtk_operator` - VARCHAR(100)
- `notes` - TEXT

**Внешние ключи:**
- `machine_id` → `machinery.id` (CASCADE DELETE)

**Связь:** ONE-TO-ONE с machinery

**Рекомендация:** Добавить уникальный ключ `machine_id`

---

### 3.4 satellite_data (Спутниковые данные)
**Назначение:** NDVI, EVI индексы

**Поля:**
- `id` - INTEGER, PRIMARY KEY, INDEX
- `field_id` - INTEGER, **FOREIGN KEY** → fields.id, NOT NULL
- `acquisition_date` - DATE, NOT NULL, INDEX
- `satellite_source` - VARCHAR(50) (Sentinel-2/Landsat/PlanetScope)
- `ndvi_mean` - FLOAT (-1 to 1)
- `ndvi_min` - FLOAT
- `ndvi_max` - FLOAT
- `ndvi_std` - FLOAT
- `evi_mean` - FLOAT
- `cloud_cover_pct` - FLOAT
- `resolution_m` - FLOAT
- `image_quality` - VARCHAR(50)
- `crop_stage` - VARCHAR(100)
- `notes` - TEXT

**Внешние ключи:**
- `field_id` → `fields.id` (CASCADE DELETE)

**Рекомендация:** Добавить составной уникальный ключ `(field_id, acquisition_date, satellite_source)`

---

## 4. СПРАВОЧНЫЕ ТАБЛИЦЫ

### 4.1 ref_crops (Справочник культур)
**Поля:**
- `id` - INTEGER, PRIMARY KEY, INDEX
- `crop_name` - VARCHAR(100), NOT NULL, **UNIQUE**
- `crop_type` - VARCHAR(50)
- `typical_yield_min` - FLOAT
- `typical_yield_max` - FLOAT
- `seeding_rate_min` - FLOAT
- `seeding_rate_max` - FLOAT
- `seeding_depth_cm` - FLOAT
- `row_spacing_cm` - FLOAT

**Уникальные ключи:**
- `crop_name` (UNIQUE)

---

### 4.2 ref_fertilizers (Справочник удобрений)
**Поля:**
- `id` - INTEGER, PRIMARY KEY, INDEX
- `name` - VARCHAR(100), NOT NULL, **UNIQUE**
- `type` - VARCHAR(50)
- `n_content` - FLOAT
- `p2o5_content` - FLOAT
- `k2o_content` - FLOAT
- `s_content` - FLOAT

**Уникальные ключи:**
- `name` (UNIQUE)

---

### 4.3 ref_pesticides (Справочник СЗР)
**Поля:**
- `id` - INTEGER, PRIMARY KEY, INDEX
- `trade_name` - VARCHAR(100), NOT NULL
- `active_ingredient` - VARCHAR(200)
- `pesticide_class` - VARCHAR(50)
- `typical_dose_min` - FLOAT
- `typical_dose_max` - FLOAT
- `dose_unit` - VARCHAR(20)

**Рекомендация:** Добавить уникальный ключ `trade_name`

---

## ДИАГРАММА СВЯЗЕЙ (ER-диаграмма)

```
farms (БИН - UNIQUE)
├─→ users (farm_id) - MANY TO ONE
├─→ fields (farm_id) - ONE TO MANY
│   ├─→ operations (field_id) - ONE TO MANY
│   │   ├─→ sowing_details (operation_id) - ONE TO ONE
│   │   ├─→ fertilizer_applications (operation_id) - ONE TO MANY
│   │   ├─→ pesticide_applications (operation_id) - ONE TO MANY
│   │   ├─→ harvest_data (operation_id) - ONE TO ONE
│   │   └─→ agrochemical_analyses (operation_id) - ONE TO ONE
│   ├─→ economic_data (field_id) - ONE TO MANY
│   ├─→ phytosanitary_monitoring (field_id) - ONE TO MANY
│   ├─→ satellite_data (field_id) - ONE TO MANY
│   └─→ gps_tracks (field_id) - ONE TO MANY
├─→ weather_data (farm_id) - ONE TO MANY
└─→ machinery (farm_id) - ONE TO MANY
    ├─→ machinery_equipment (machine_id) - ONE TO ONE
    └─→ gps_tracks (machine_id) - ONE TO MANY

users
└─→ audit_logs (user_id) - ONE TO MANY

Справочники (независимые):
- ref_crops
- ref_fertilizers
- ref_pesticides
```

---

## КРИТИЧЕСКИ ВАЖНЫЕ УНИКАЛЬНЫЕ КЛЮЧИ

### Существующие:
1. **users.username** (UNIQUE) ✅
2. **users.email** (UNIQUE) ✅
3. **farms.bin** (UNIQUE) ✅ **← ГЛАВНЫЙ КЛЮЧ СВЯЗИ!**
4. **fields.field_code** (UNIQUE) ✅
5. **ref_crops.crop_name** (UNIQUE) ✅
6. **ref_fertilizers.name** (UNIQUE) ✅

### Рекомендуемые добавить:
1. **economic_data**: составной ключ `(field_id, year, crop)` - предотвратит дубликаты экономических данных
2. **weather_data**: составной ключ `(farm_id, datetime)` - предотвратит дубликаты погодных записей
3. **satellite_data**: составной ключ `(field_id, acquisition_date, satellite_source)` - предотвратит дубликаты спутниковых данных
4. **machinery_equipment.machine_id** (UNIQUE) - обеспечит ONE-TO-ONE связь
5. **ref_pesticides.trade_name** (UNIQUE) - предотвратит дубликаты в справочнике

---

## ПРОБЛЕМЫ И РЕКОМЕНДАЦИИ ДЛЯ SUPABASE

### ✅ Совместимость с Supabase
База данных полностью совместима с PostgreSQL (Supabase), но требуются изменения:

### 1. Миграция с SQLite на PostgreSQL

**Изменения в типах данных:**
- SQLite `INTEGER` → PostgreSQL `INTEGER` (ОК)
- SQLite `FLOAT` → PostgreSQL `DOUBLE PRECISION` или `NUMERIC`
- SQLite `TEXT` → PostgreSQL `TEXT` (ОК)
- SQLite `BOOLEAN` → PostgreSQL `BOOLEAN` (ОК)
- SQLite `DateTime` → PostgreSQL `TIMESTAMP` или `TIMESTAMPTZ`

**Рекомендуемые изменения:**

```sql
-- Пример миграции для Supabase (PostgreSQL)

-- 1. Изменить все FLOAT на NUMERIC для точности
ALTER TABLE fields ALTER COLUMN area_ha TYPE NUMERIC(10,2);

-- 2. Добавить составные уникальные ключи
ALTER TABLE economic_data
  ADD CONSTRAINT uk_economic_data UNIQUE (field_id, year, crop);

ALTER TABLE weather_data
  ADD CONSTRAINT uk_weather_data UNIQUE (farm_id, datetime);

ALTER TABLE satellite_data
  ADD CONSTRAINT uk_satellite_data UNIQUE (field_id, acquisition_date, satellite_source);

-- 3. Добавить ON DELETE CASCADE для внешних ключей (если не задано)
ALTER TABLE fields
  DROP CONSTRAINT IF EXISTS fields_farm_id_fkey,
  ADD CONSTRAINT fields_farm_id_fkey
    FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE;

-- 4. Добавить индексы для производительности
CREATE INDEX idx_operations_farm_date ON operations(farm_id, operation_date);
CREATE INDEX idx_gps_tracks_machine_datetime ON gps_tracks(machine_id, datetime);
CREATE INDEX idx_satellite_acquisition ON satellite_data(field_id, acquisition_date);
```

### 2. Рекомендации по безопасности (Row Level Security)

Для Supabase критически важно настроить RLS:

```sql
-- Включить RLS на всех таблицах
ALTER TABLE farms ENABLE ROW LEVEL SECURITY;
ALTER TABLE fields ENABLE ROW LEVEL SECURITY;
ALTER TABLE operations ENABLE ROW LEVEL SECURITY;
-- ... и т.д. для всех таблиц

-- Политика: админы видят все
CREATE POLICY admin_all ON farms
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE users.id = auth.uid()
      AND users.role = 'admin'
    )
  );

-- Политика: фермеры видят только свое хозяйство
CREATE POLICY farmer_own_farm ON farms
  FOR SELECT USING (
    id = (
      SELECT farm_id FROM users WHERE users.id = auth.uid()
    )
  );
```

### 3. Индексы для оптимизации

```sql
-- Для быстрого поиска по датам
CREATE INDEX idx_operations_date ON operations(operation_date);
CREATE INDEX idx_weather_datetime ON weather_data(datetime);
CREATE INDEX idx_phyto_inspection ON phytosanitary_monitoring(field_id, inspection_date);

-- Для JOIN операций
CREATE INDEX idx_users_farm ON users(farm_id) WHERE farm_id IS NOT NULL;
CREATE INDEX idx_fields_farm ON fields(farm_id);
CREATE INDEX idx_operations_field ON operations(field_id);
```

### 4. Триггеры для updated_at

```sql
-- Функция для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггер для farms
CREATE TRIGGER update_farms_updated_at
  BEFORE UPDATE ON farms
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Аналогично для users
CREATE TRIGGER update_users_updated_at
  BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## СВОДНАЯ ТАБЛИЦА СВЯЗЕЙ

| Родительская таблица | Дочерняя таблица | Связь | Ключ | ON DELETE |
|----------------------|------------------|-------|------|-----------|
| farms | users | 1:M | farm_id | SET NULL |
| farms | fields | 1:M | farm_id | CASCADE |
| farms | weather_data | 1:M | farm_id | CASCADE |
| farms | machinery | 1:M | farm_id | CASCADE |
| fields | operations | 1:M | field_id | CASCADE |
| fields | economic_data | 1:M | field_id | CASCADE |
| fields | phytosanitary_monitoring | 1:M | field_id | CASCADE |
| fields | satellite_data | 1:M | field_id | CASCADE |
| fields | gps_tracks | 1:M | field_id | SET NULL |
| operations | sowing_details | 1:1 | operation_id | CASCADE |
| operations | fertilizer_applications | 1:M | operation_id | CASCADE |
| operations | pesticide_applications | 1:M | operation_id | CASCADE |
| operations | harvest_data | 1:1 | operation_id | CASCADE |
| operations | agrochemical_analyses | 1:1 | operation_id | CASCADE |
| machinery | machinery_equipment | 1:1 | machine_id | CASCADE |
| machinery | gps_tracks | 1:M | machine_id | CASCADE |
| users | audit_logs | 1:M | user_id | CASCADE |

---

## ИТОГОВЫЕ РЕКОМЕНДАЦИИ

### Для успешной работы с Supabase:

1. ✅ **Добавить составные уникальные ключи** (см. выше)
2. ✅ **Настроить Row Level Security (RLS)** для безопасности
3. ✅ **Добавить индексы** для производительности
4. ✅ **Настроить триггеры** для updated_at
5. ✅ **Изменить DATABASE_URL** в `.env` на Supabase PostgreSQL
6. ✅ **Протестировать миграцию** на тестовых данных
7. ✅ **Настроить CASCADE DELETE** для всех FK
8. ✅ **Добавить проверки (CHECK constraints)** для валидации данных

### Критические поля для целостности:
- `farms.bin` - UNIQUE (главный бизнес-ключ)
- `users.username`, `users.email` - UNIQUE
- `fields.field_code` - UNIQUE
- Все `farm_id` - корректно связаны с farms.id
