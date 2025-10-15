# Changelog

Все важные изменения в проекте Farm Data Collection System.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/).

---

## [Unreleased] - 2025-10-15

### 🎯 Текущий статус
- ✅ Приложение развернуто на Streamlit Cloud
- ✅ Подключение к PostgreSQL (Supabase) настроено
- ✅ Все критические ошибки полей базы данных исправлены
- ⚠️ Требуется тестирование всех модулей на продакшене

### 🐛 Исправлено

#### Коммит `5a8039e` - Исправление PhytosanitaryMonitoring (2025-10-15)
**Проблема:** Несоответствие имен полей между моделью базы данных и кодом страницы
**Файлы:** `pages/7_🐛_Phytosanitary.py`

Исправления:
- `monitoring_date` → `inspection_date`
- `problem_type` → `pest_type`
- `problem_name` → `pest_name`
- `severity` → `severity_pct`
- `affected_area_percent` → `prevalence_pct`
- `intensity` → `intensity_score`
- `treatment_required` → `threshold_exceeded`
- `growth_stage` → `crop_stage`
- Удалены несуществующие поля: `crop`, `weather_conditions`

**Ошибки, которые были исправлены:**
```
'monitoring_date' is an invalid keyword argument for PhytosanitaryMonitoring
AttributeError: PhytosanitaryMonitoring object has no attribute 'monitoring_date'
```

---

#### Коммит `b3e5d4c` - Удаление вложенных кнопок (2025-10-15)
**Проблема:** `st.button()` нельзя использовать внутри `st.form()` или внутри других кнопок
**Файлы:** `pages/4_🌾_Sowing.py`, `pages/15_📥_Import.py`

Исправления:
- Удалена кнопка "Перейти к внесению удобрений" из формы посева
- Удалена кнопка "Перейти к полям" из обработчика импорта
- Заменены на информационные сообщения с указанием использовать боковое меню

**Ошибка, которая была исправлена:**
```
StreamlitAPIException: st.button() can't be used in an st.form()
```

---

#### Коммит `e082bec` - Добавление обязательных полей в SowingDetail (2025-10-15)
**Проблема:** Отсутствовали обязательные поля при создании записи посева
**Файлы:** `pages/4_🌾_Sowing.py`

Исправления:
- Добавлено обязательное поле `crop` (nullable=False в модели)
- Добавлено поле `variety` для консистентности данных
- Добавлено поле `total_seeds_kg` с расчетным значением

**Ошибка, которая была исправлена:**
```
psycopg2.errors.NotNullViolation: null value in column "crop" of relation "sowing_details" violates not-null constraint
```

---

#### Коммит `9e43bb9` - Исправление несоответствий имен полей (2025-10-15)
**Проблема:** Множественные несоответствия между именами полей в моделях и их использованием в коде
**Файлы:** `pages/4_🌾_Sowing.py`, `pages/15_📥_Import.py`

Исправления в `pages/4_🌾_Sowing.py`:
- `soil_moisture_pct` → `soil_moisture_percent` (строка 323)

Исправления в `pages/15_📥_Import.py`:
- `contact_person` → `director_name` (строка 200)

Комплексная проверка всех страниц подтвердила корректность:
- ✅ `area_processed_ha` (не `area_processed`)
- ✅ `farm_id` присутствует во всех Operation
- ✅ `humus_pct` в Field
- ✅ `*_percent` поля в HarvestData, AgrochemicalAnalysis
- ✅ `*_content_percent` в FertilizerApplication
- ✅ `humidity_percent` в PesticideApplication

**Ошибки, которые были исправлены:**
```
'soil_moisture_pct' is an invalid keyword argument for SowingDetail
'contact_person' is an invalid keyword argument for Farm
```

---

#### Коммит `1683ba6` - Исправление area_processed и farm_id (2025-10-15)
**Проблема:** Неправильное имя поля и отсутствие обязательного параметра
**Файлы:** `pages/4_🌾_Sowing.py`

Исправления:
- `area_processed` → `area_processed_ha` (строка 306)
- Добавлен отсутствующий параметр `farm_id=farm.id`

**Ошибка, которая была исправлена:**
```
'area_processed' is an invalid keyword argument for Operation
```

---

#### Коммит `7e75783` - Добавление поддержки PostgreSQL (2025-10-15)
**Проблема:** SQLite не сохраняет данные на Streamlit Cloud
**Файлы:** `requirements.txt`, `modules/database.py`, документация

Добавлено:
- Зависимость `psycopg2-binary>=2.9.0` в requirements.txt
- Документация по настройке Supabase: `SUPABASE_SETUP.md`
- Шаблон секретов: `STREAMLIT_SECRETS_TEMPLATE.md`
- Поддержка переменной окружения `DATABASE_URL`

**Важно:** Требуется настроить DATABASE_URL в Streamlit Secrets для персистентности данных

---

#### Коммит `b8c3784` - Исправление packages.txt (2025-10-15)
**Проблема:** Русские комментарии в packages.txt парсились как имена пакетов
**Файлы:** `packages.txt`

Исправление:
- Полностью очищен файл packages.txt
- Удалены системные зависимости (GDAL больше не требуется)

**Ошибка, которая была исправлена:**
```
E: Unable to locate package Системные
E: Unable to locate package зависимости
```

---

#### Коммит `fd801ba` - Упрощение зависимостей (2025-10-15)
**Проблема:** Конфликты системных пакетов GDAL на Streamlit Cloud
**Файлы:** `requirements.txt`

Изменения:
- Уменьшено количество зависимостей с 20+ до 11 основных
- Удалены пакеты, требующие GDAL: geopandas, rasterio, sentinelhub, gpxpy, shapely
- Удалены dev-зависимости: pytest, black, flake8
- Удалены опциональные: reportlab, tqdm

**Ошибка, которая была исправлена:**
```
Errors were encountered while processing:
 /tmp/apt-dpkg-install-YIBhac/041-libodbc2_2.3.11-2+deb12u1_amd64.deb
E: Sub-process /usr/bin/dpkg returned an error code (1)
```

---

## [1.0.0] - Initial Deployment

### ✨ Добавлено

#### Основные модули
- 🏢 **Farm Setup** - Регистрация и управление хозяйством
- 🏠 **Dashboard** - Сводная панель с ключевыми метриками
- 🌱 **Fields** - Управление полями и земельными участками
- 📝 **Journal** - Журнал всех операций
- 🌾 **Sowing** - Регистрация посевных работ
- 💊 **Fertilizers** - Учет внесения удобрений
- 🛡️ **Pesticides** - Учет применения СЗР
- 🐛 **Phytosanitary** - Фитосанитарный мониторинг
- 🚜 **Harvest** - Учет уборки урожая
- 🧪 **Agrochemistry** - Агрохимические анализы почвы
- 📊 **Analytics** - Аналитика и отчеты
- 📥 **Import** - Импорт данных из Excel
- 📖 **Инструкция** - Подробное руководство пользователя на русском языке (831 строка)

#### База данных
18 таблиц с нормализованной схемой:
- Farm, Field, Operation
- SowingDetail, FertilizerApplication, PesticideApplication
- HarvestData, AgrochemicalAnalysis, PhytosanitaryMonitoring
- WeatherData, EconomicData, Machinery, MachineryEquipment
- GPSTrack, SatelliteData
- RefCrop, RefFertilizer, RefPesticide

#### Технологический стек
- **Frontend:** Streamlit 1.32+
- **Backend:** Python 3.10+
- **ORM:** SQLAlchemy 2.0+
- **Database (Dev):** SQLite
- **Database (Prod):** PostgreSQL via Supabase
- **Charts:** Plotly, Folium для карт
- **Deployment:** Streamlit Cloud

#### Справочники
- 22 культуры с рекомендациями по агротехнике
- 30+ видов удобрений с составом NPK
- 25+ пестицидов с характеристиками

---

## 📋 Известные ограничения

1. **SQLite на Streamlit Cloud** - Данные не персистируются без PostgreSQL
2. **Геолокация** - Пакеты для работы с геоданными (GDAL) удалены из-за конфликтов
3. **Satellite Data** - Модуль спутниковых данных не реализован (таблица есть, функционал нет)
4. **GPS Tracking** - Модуль GPS-треков не реализован
5. **Weather Data** - Модуль погодных данных не реализован

---

## 🔜 Планируемые улучшения

### Высокий приоритет
- [ ] Комплексное тестирование всех модулей на продакшене
- [ ] Проверка импорта данных из Excel
- [ ] Валидация всех форм и полей
- [ ] Тестирование аналитических отчетов

### Средний приоритет
- [ ] Добавить экспорт отчетов в PDF
- [ ] Реализовать модуль погодных данных
- [ ] Добавить интеграцию с внешними API погоды
- [ ] Улучшить визуализацию карт

### Низкий приоритет
- [ ] Реализовать GPS-трекинг техники
- [ ] Добавить интеграцию со спутниковыми данными
- [ ] Многопользовательский режим с аутентификацией
- [ ] Мобильное приложение

---

## 🐛 Как сообщить об ошибке

Если вы обнаружили ошибку:
1. Проверьте, не исправлена ли она в последних коммитах выше
2. Запишите точное сообщение об ошибке
3. Укажите, какую операцию вы пытались выполнить
4. Укажите версию/коммит приложения

---

## 📚 Дополнительная документация

- [README.md](README.md) - Общее описание проекта
- [SUPABASE_SETUP.md](SUPABASE_SETUP.md) - Настройка базы данных PostgreSQL
- [STREAMLIT_SECRETS_TEMPLATE.md](STREAMLIT_SECRETS_TEMPLATE.md) - Настройка секретов
- [DEPLOYMENT.md](DEPLOYMENT.md) - Инструкции по деплою

---

**Версия документа:** 1.0
**Последнее обновление:** 15 октября 2025
**GitHub:** https://github.com/YergZakon/sbor_apk
