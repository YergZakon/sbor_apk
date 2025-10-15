# 🔐 Authentication Integration Guide

Руководство по интеграции аутентификации в оставшиеся страницы системы.

## ✅ Уже интегрировано

- ✅ [pages/1_🏠_Dashboard.py](pages/1_🏠_Dashboard.py) - **ГОТОВО**
- ✅ [pages/0_🏢_Farm_Setup.py](pages/0_🏢_Farm_Setup.py) - **ГОТОВО**
- ✅ [pages/99_🔐_Login.py](pages/99_🔐_Login.py) - **НЕ ТРЕБУЕТСЯ** (это страница логина)
- ✅ [pages/98_⚙️_Admin.py](pages/98_⚙️_Admin.py) - **УЖЕ ЕСТЬ** (админка)

## ⏳ Требуют интеграции

- ⏳ [pages/2_🌱_Fields.py](pages/2_🌱_Fields.py)
- ⏳ [pages/3_📝_Journal.py](pages/3_📝_Journal.py)
- ⏳ [pages/4_🌾_Sowing.py](pages/4_🌾_Sowing.py)
- ⏳ [pages/5_💊_Fertilizers.py](pages/5_💊_Fertilizers.py)
- ⏳ [pages/6_🛡️_Pesticides.py](pages/6_🛡️_Pesticides.py)
- ⏳ [pages/7_🐛_Phytosanitary.py](pages/7_🐛_Phytosanitary.py)
- ⏳ [pages/8_🚜_Harvest.py](pages/8_🚜_Harvest.py)
- ⏳ [pages/9_🧪_Agrochemistry.py](pages/9_🧪_Agrochemistry.py)
- ⏳ [pages/11_🌤️_Weather.py](pages/11_🌤️_Weather.py)
- ⏳ [pages/15_📥_Import.py](pages/15_📥_Import.py)

---

## 📋 Шаблон интеграции

### Шаг 1: Добавить импорты

**Найти:**
```python
from modules.database import SessionLocal, Farm, Field, ...
from modules.config import settings
```

**Добавить после:**
```python
from modules.auth import (
    require_auth,
    require_farm_binding,
    filter_query_by_farm,
    get_user_display_name,
    can_edit_data,
    can_delete_data
)
```

### Шаг 2: Добавить проверку авторизации

**Найти:**
```python
st.set_page_config(page_title="...", page_icon="...", layout="wide")

st.title("...")
```

**Заменить на:**
```python
st.set_page_config(page_title="...", page_icon="...", layout="wide")

# Требуем авторизацию и привязку к хозяйству
require_auth()
require_farm_binding()

st.title("...")
st.caption(f"Пользователь: **{get_user_display_name()}**")
```

### Шаг 3: Фильтровать запросы к БД

**Найти все:**
```python
db.query(Farm).first()
db.query(Farm).all()
db.query(Field).all()
db.query(Field).filter(...)
db.query(Operation).all()
# и т.д.
```

**Заменить на:**
```python
filter_query_by_farm(db.query(Farm), Farm).first()
filter_query_by_farm(db.query(Farm), Farm).all()
filter_query_by_farm(db.query(Field), Field).all()
filter_query_by_farm(db.query(Field).filter(...), Field)
filter_query_by_farm(db.query(Operation), Operation).all()
```

**❗ ВАЖНО:**
- Применять к моделям с `farm_id`: Farm, Field, Operation, SowingDetail, FertilizerApplication, PesticideApplication, PhytosanitaryMonitoring, HarvestDetail, AgrochemicalAnalysis, WeatherData
- НЕ применять к справочным таблицам: Crop, Variety, Fertilizer, Pesticide, Disease, Pest, Weed

### Шаг 4: Защитить формы редактирования

**Найти секции добавления/редактирования:**
```python
st.markdown("### ➕ Добавить...")

with st.form("..."):
    # форма
```

**Обернуть в проверку прав:**
```python
if can_edit_data():
    st.markdown("### ➕ Добавить...")

    with st.form("..."):
        # форма
else:
    st.info("ℹ️ У вас нет прав на редактирование данных")
```

**Для кнопок удаления:**
```python
if can_delete_data():
    delete_btn = st.form_submit_button("🗑️ Удалить", ...)

    if delete_btn:
        # логика удаления
else:
    st.warning("⚠️ Только администратор может удалять данные")
```

### Шаг 5: Фильтровать JOIN запросы

**Найти:**
```python
db.query(Operation, Field).join(Field).all()
db.query(Field.name, Operation.date).join(Field).all()
```

**Заменить на:**
```python
filter_query_by_farm(
    db.query(Operation, Field).join(Field),
    Field  # Используем Field, так как у него есть farm_id
).all()

filter_query_by_farm(
    db.query(Field.name, Operation.date).join(Field),
    Field
).all()
```

---

## 🔧 Примеры из готовых страниц

### Dashboard (ГОТОВО)

```python
# Импорты
from modules.auth import require_auth, filter_query_by_farm, get_current_user, get_user_display_name

# Проверка авторизации
require_auth()

# Заголовок
user = get_current_user()
st.title(f"🏠 Dashboard - Панель управления")
st.caption(f"Добро пожаловать, **{get_user_display_name()}**!")

# Фильтрация запросов
farms_count = filter_query_by_farm(db.query(Farm), Farm).count()
fields_count = filter_query_by_farm(db.query(Field), Field).count()
operations_count = filter_query_by_farm(db.query(Operation), Operation).count()

# JOIN запросы
recent_operations = filter_query_by_farm(
    db.query(
        Operation.operation_date,
        Operation.operation_type,
        Field.name.label('field_name'),
        Operation.crop,
        Operation.area_processed_ha
    ).join(Field),
    Field
).order_by(Operation.operation_date.desc()).limit(10).all()
```

### Farm Setup (ГОТОВО)

```python
# Импорты
from modules.auth import (
    require_auth,
    filter_query_by_farm,
    get_current_user,
    get_user_display_name,
    can_edit_data,
    can_delete_data,
    is_admin
)

# Проверка авторизации
require_auth()

# Заголовок
st.title("🏢 Регистрация хозяйства")
st.caption(f"Пользователь: **{get_user_display_name()}**")

# Получение хозяйства с учетом роли
user = get_current_user()
if is_admin():
    # Админ может выбирать хозяйства
    all_farms = db.query(Farm).all()
    # ... логика выбора
else:
    # Фермер видит только свое хозяйство
    existing_farm = filter_query_by_farm(db.query(Farm), Farm).first()

# Защита кнопок
if can_edit_data():
    if st.button("✏️ Редактировать данные хозяйства"):
        st.session_state.edit_mode = True
else:
    st.info("ℹ️ У вас нет прав на редактирование данных хозяйства")

if can_delete_data():
    with st.expander("⚠️ Удалить хозяйство (опасно!)"):
        # ... логика удаления
```

---

## 🎯 Специфика для каждой страницы

### Fields (Поля)

- ✅ Фильтровать: `db.query(Field).filter(Field.farm_id == farm.id)`
- ✅ Защитить форму добавления поля
- ✅ Защитить форму редактирования поля
- ✅ Удаление только для админов

### Journal (Журнал операций)

- ✅ Фильтровать операции по полям хозяйства
- ✅ JOIN с Field для фильтрации
- ✅ Экспорт только своих данных

### Sowing, Fertilizers, Pesticides, Harvest (Агрооперации)

- ✅ Фильтровать поля для выбора
- ✅ Фильтровать историю операций
- ✅ Защитить формы ввода данных
- ✅ Справочники (культуры, удобрения, пестициды) - НЕ фильтровать

### Phytosanitary (Фитосанитария)

- ✅ Фильтровать мониторинги по полям хозяйства
- ✅ Справочники (болезни, вредители, сорняки) - НЕ фильтровать

### Agrochemistry (Агрохимия)

- ✅ Фильтровать анализы по полям хозяйства

### Weather (Погода)

- ✅ Фильтровать метеоданные по хозяйству
- ✅ Только редактирование своих данных

### Import (Импорт данных)

- ✅ Импорт только в свое хозяйство
- ✅ Валидация принадлежности полей
- ❗ ВАЖНО: Админ может импортировать в любое хозяйство

---

## 🧪 Тестирование

После интеграции необходимо проверить:

1. **Создать тестовых пользователей:**
   ```bash
   python create_admin.py  # Создать админа
   # Затем через админку создать 2 фермеров с разными хозяйствами
   ```

2. **Тест изоляции данных:**
   - Войти как Фермер 1, добавить поле/операцию
   - Войти как Фермер 2, проверить что данные Фермера 1 не видны
   - Войти как Админ, проверить что видны ВСЕ данные

3. **Тест прав доступа:**
   - Войти как Viewer, проверить что нет кнопок редактирования
   - Войти как Фермер, проверить что есть кнопки редактирования
   - Войти как Админ, проверить что есть все кнопки включая удаление

4. **Тест JOIN запросов:**
   - Проверить Dashboard с метриками
   - Проверить Journal с фильтрацией
   - Проверить графики и отчеты

---

## 📝 Чеклист интеграции

Для каждой страницы:

- [ ] Добавлены импорты из modules.auth
- [ ] Добавлен `require_auth()` после `st.set_page_config()`
- [ ] Добавлен `require_farm_binding()` (если нужна привязка к хозяйству)
- [ ] Добавлен caption с именем пользователя
- [ ] Все запросы к таблицам с farm_id обернуты в `filter_query_by_farm()`
- [ ] Формы добавления/редактирования обернуты в `if can_edit_data():`
- [ ] Кнопки удаления обернуты в `if can_delete_data():`
- [ ] JOIN запросы правильно фильтруются
- [ ] Страница протестирована с разными ролями
- [ ] Нет утечки данных между хозяйствами

---

## 🚀 Следующие шаги

1. Применить изменения к оставшимся 10 страницам
2. Протестировать каждую страницу
3. Закоммитить изменения
4. Задеплоить на Streamlit Cloud
5. Создать админа на продакшене
6. Провести финальное тестирование

---

## 📚 Справка по функциям

### require_auth()
Требует авторизации. Останавливает выполнение если пользователь не авторизован.

### require_farm_binding()
Требует привязки к хозяйству (кроме админов). Останавливает выполнение если пользователь не привязан.

### filter_query_by_farm(query, model)
Фильтрует SQLAlchemy query по хозяйству в зависимости от роли:
- **Админ** - возвращает query без изменений (видит всё)
- **Фермер/Viewer** - добавляет `.filter(model.farm_id == user.farm_id)`
- **Не авторизован** - возвращает `.filter(False)` (пустой результат)

### can_edit_data()
Проверяет право на редактирование. Возвращает `True` для админов и фермеров.

### can_delete_data()
Проверяет право на удаление. Возвращает `True` только для админов.

### get_user_display_name()
Возвращает отображаемое имя пользователя (full_name или username).

### is_admin()
Проверяет является ли пользователь администратором.

---

**Дата создания:** 2025-10-15
**Версия:** 2.0.0
**Статус:** В процессе интеграции
