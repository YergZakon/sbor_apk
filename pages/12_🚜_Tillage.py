"""
Tillage - Учет обработки почвы
Регистрация операций механической обработки почвы: вспашка, культивация, боронование и др.
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date
from pathlib import Path

# Добавляем путь к модулям
import sys
sys.path.append(str(Path(__file__).parent.parent))

from modules.database import get_db, Farm, Field, Operation, TillageDetails, Machinery, Implements
from modules.auth import (
    require_auth,
    require_farm_binding,
    filter_query_by_farm,
    get_user_display_name,
    get_current_user,
    is_admin,
    can_edit_data,
    can_delete_data
)

# Настройка страницы
st.set_page_config(page_title="Обработка почвы", page_icon="🚜", layout="wide")

# Требуем авторизацию и привязку к хозяйству
require_auth()
require_farm_binding()

st.title("🚜 Учет обработки почвы")
st.caption(f"Пользователь: **{get_user_display_name()}**")

# Подключение к БД
db = next(get_db())

# Проверка наличия хозяйства
user = get_current_user()

if is_admin():
    farm = db.query(Farm).first()
else:
    user_farm_id = user.get("farm_id") if user else None
    farm = db.query(Farm).filter(Farm.id == user_farm_id).first() if user_farm_id else None

if not farm:
    st.warning("⚠️ Сначала создайте хозяйство!")
    st.stop()

# Получение списка полей
fields = filter_query_by_farm(db.query(Field), Field).all()
if not fields:
    st.warning("⚠️ Сначала добавьте поля на странице 'Поля'!")
    st.stop()

# Табы
tab1, tab2 = st.tabs(["📝 Регистрация обработки", "📊 История обработок"])

# ========================================
# TAB 1: Регистрация обработки почвы
# ========================================
with tab1:
    st.subheader("Регистрация обработки почвы")

    with st.form("tillage_form"):
        col1, col2 = st.columns(2)

        with col1:
            # Выбор поля
            field_options = {f"{f.field_code} - {f.name}": f for f in fields}
            selected_field_name = st.selectbox(
                "Поле *",
                options=list(field_options.keys()),
                help="Выберите поле для обработки"
            )
            selected_field = field_options[selected_field_name]

            # Дата начала
            operation_date = st.date_input(
                "Дата начала обработки *",
                value=date.today(),
                help="Дата начала обработки почвы"
            )

            # Дата окончания
            end_date = st.date_input(
                "Дата окончания",
                value=None,
                help="Дата окончания (для многодневных работ)"
            )

            # Тип обработки
            tillage_type = st.selectbox(
                "Тип обработки *",
                options=[
                    'plowing',           # Вспашка
                    'cultivation',       # Культивация
                    'harrowing',        # Боронование
                    'discing',          # Дискование
                    'deep_loosening',   # Глубокое рыхление
                    'rolling',          # Прикатывание
                    'stubble_breaking', # Лущение стерни
                    'chiseling'         # Чизелевание
                ],
                format_func=lambda x: {
                    'plowing': 'Вспашка',
                    'cultivation': 'Культивация',
                    'harrowing': 'Боронование',
                    'discing': 'Дискование',
                    'deep_loosening': 'Глубокое рыхление',
                    'rolling': 'Прикатывание',
                    'stubble_breaking': 'Лущение стерни',
                    'chiseling': 'Чизелевание'
                }[x],
                help="Вид механической обработки почвы"
            )

        with col2:
            # Обработанная площадь
            area_processed = st.number_input(
                "Обработанная площадь (га) *",
                min_value=0.1,
                max_value=selected_field.area_ha,
                value=selected_field.area_ha,
                step=0.1,
                help=f"Площадь поля: {selected_field.area_ha} га"
            )

            # Глубина обработки
            depth_cm = st.number_input(
                "Глубина обработки (см)",
                min_value=0.0,
                max_value=50.0,
                value=20.0,
                step=1.0,
                help="Глубина обработки почвы"
            )

            # Цель обработки
            tillage_purpose = st.selectbox(
                "Цель обработки",
                options=[
                    'primary',      # Основная
                    'pre_sowing',   # Предпосевная
                    'post_harvest', # Послеуборочная
                    'weed_control', # Борьба с сорняками
                    'moisture_conservation', # Сохранение влаги
                    'other'
                ],
                format_func=lambda x: {
                    'primary': 'Основная обработка',
                    'pre_sowing': 'Предпосевная обработка',
                    'post_harvest': 'Послеуборочная обработка',
                    'weed_control': 'Борьба с сорняками',
                    'moisture_conservation': 'Сохранение влаги',
                    'other': 'Другое'
                }.get(x, x),
                help="Цель проведения обработки",
                index=None
            )

        # Техника и агрегаты
        st.markdown("---")
        st.markdown("### 🚜 Техника и агрегаты")

        # Получение списка техники и агрегатов
        machinery_list = filter_query_by_farm(db.query(Machinery).filter(Machinery.status == 'active'), Machinery).all()
        implements_list = filter_query_by_farm(db.query(Implements).filter(Implements.status == 'active'), Implements).all()

        col_tech1, col_tech2, col_tech3 = st.columns(3)

        with col_tech1:
            # Тракторы
            tractors = [m for m in machinery_list if m.machinery_type == 'tractor']

            selected_machinery = st.selectbox(
                "Трактор",
                options=[None] + tractors,
                format_func=lambda m: "Не выбрано" if m is None else f"{m.brand or ''} {m.model} ({m.year or '-'})",
                help="Выберите трактор",
                key="tillage_machinery"
            )

            machine_year = selected_machinery.year if selected_machinery else None

        with col_tech2:
            # Фильтруем агрегаты в зависимости от типа обработки
            implement_types_map = {
                'plowing': ['plow'],
                'cultivation': ['cultivator'],
                'harrowing': ['harrow'],
                'discing': ['disc'],
                'deep_loosening': ['deep_loosener'],
                'rolling': ['roller'],
                'stubble_breaking': ['stubble_breaker', 'disc'],
                'chiseling': ['cultivator', 'deep_loosener']
            }

            suitable_types = implement_types_map.get(tillage_type, [])
            suitable_implements = [impl for impl in implements_list if impl.implement_type in suitable_types]

            selected_implement = st.selectbox(
                "Агрегат",
                options=[None] + suitable_implements,
                format_func=lambda i: "Не выбрано" if i is None else f"{i.brand or ''} {i.model} ({i.working_width_m or '-'}м)",
                help="Выберите агрегат для обработки",
                key="tillage_implement"
            )

            implement_year = selected_implement.year if selected_implement else None

            if selected_implement:
                st.caption(f"Ширина захвата: {selected_implement.working_width_m or '-'}м")

        with col_tech3:
            work_speed_kmh = st.number_input(
                "Рабочая скорость (км/ч)",
                min_value=0.0,
                max_value=15.0,
                value=None,
                step=0.5,
                help="Скорость движения агрегата",
                key="tillage_speed"
            )

        # Условия и примечания
        st.markdown("---")
        st.markdown("### 📝 Дополнительная информация")

        col3, col4 = st.columns(2)

        with col3:
            soil_moisture = st.selectbox(
                "Влажность почвы",
                options=['dry', 'optimal', 'wet', 'very_wet'],
                format_func=lambda x: {
                    'dry': 'Сухая',
                    'optimal': 'Оптимальная',
                    'wet': 'Влажная',
                    'very_wet': 'Переувлажненная'
                }[x],
                help="Состояние почвы по влажности",
                index=None
            )

        with col4:
            weather_conditions = st.text_input(
                "Погодные условия",
                placeholder="Например: Ясно, +15°C",
                help="Описание погоды во время обработки"
            )

        notes = st.text_area(
            "Примечания",
            height=80,
            help="Дополнительная информация об обработке"
        )

        # Кнопка отправки
        submitted = st.form_submit_button("✅ Зарегистрировать обработку", use_container_width=True, type="primary")

        if submitted:
            # Валидация
            errors = []

            if area_processed > selected_field.area_ha:
                errors.append(f"Обработанная площадь ({area_processed} га) превышает площадь поля ({selected_field.area_ha} га)")

            if errors:
                st.error("❌ Ошибки валидации:\n" + "\n".join(f"- {e}" for e in errors))
            else:
                try:
                    # Создаем операцию
                    operation = Operation(
                        farm_id=farm.id,
                        field_id=selected_field.id,
                        operation_type="tillage",
                        operation_date=operation_date,
                        end_date=end_date if end_date else None,
                        area_processed_ha=area_processed,
                        machine_id=selected_machinery.id if selected_machinery else None,
                        implement_id=selected_implement.id if selected_implement else None,
                        machine_year=machine_year,
                        implement_year=implement_year,
                        work_speed_kmh=work_speed_kmh if work_speed_kmh else None,
                        weather_conditions=weather_conditions if weather_conditions else None,
                        notes=notes if notes else None
                    )
                    db.add(operation)
                    db.flush()

                    # Создаем детали обработки почвы
                    tillage_details = TillageDetails(
                        operation_id=operation.id,
                        tillage_type=tillage_type,
                        depth_cm=depth_cm if depth_cm else None,
                        tillage_purpose=tillage_purpose if tillage_purpose else None,
                        soil_moisture=soil_moisture if soil_moisture else None
                    )
                    db.add(tillage_details)

                    db.commit()

                    st.success(f"✅ Обработка почвы зарегистрирована! Обработано {area_processed} га")
                    st.balloons()

                except Exception as e:
                    db.rollback()
                    st.error(f"❌ Ошибка при сохранении: {str(e)}")

# ========================================
# TAB 2: История обработок
# ========================================
with tab2:
    st.subheader("История обработок почвы")

    # Получение обработок
    tillage_operations = db.query(
        Operation.id,
        Operation.operation_date,
        Field.name.label('field_name'),
        Field.field_code,
        Operation.area_processed_ha,
        TillageDetails.tillage_type,
        TillageDetails.depth_cm,
        TillageDetails.tillage_purpose
    ).join(Field).outerjoin(TillageDetails).filter(
        Operation.operation_type == "tillage",
        Field.farm_id == farm.id
    ).order_by(Operation.operation_date.desc()).all()

    if tillage_operations:
        # Создание DataFrame
        tillage_data = []
        for op in tillage_operations:
            tillage_data.append({
                'ID': op.id,
                'Дата': op.operation_date.strftime('%Y-%m-%d') if op.operation_date else '-',
                'Поле': op.field_name or op.field_code,
                'Тип обработки': {
                    'plowing': 'Вспашка',
                    'cultivation': 'Культивация',
                    'harrowing': 'Боронование',
                    'discing': 'Дискование',
                    'deep_loosening': 'Глубокое рыхление',
                    'rolling': 'Прикатывание',
                    'stubble_breaking': 'Лущение стерни',
                    'chiseling': 'Чизелевание'
                }.get(op.tillage_type, op.tillage_type or '-'),
                'Глубина (см)': op.depth_cm or '-',
                'Площадь (га)': op.area_processed_ha or '-',
                'Цель': {
                    'primary': 'Основная',
                    'pre_sowing': 'Предпосевная',
                    'post_harvest': 'Послеуборочная',
                    'weed_control': 'Борьба с сорняками',
                    'moisture_conservation': 'Сохранение влаги',
                    'other': 'Другое'
                }.get(op.tillage_purpose, op.tillage_purpose or '-')
            })

        df_tillage = pd.DataFrame(tillage_data)
        st.dataframe(df_tillage, use_container_width=True, hide_index=True)

        # Статистика
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Всего обработок", len(tillage_operations))

        with col2:
            total_area = sum([op.area_processed_ha for op in tillage_operations if op.area_processed_ha])
            st.metric("Обработано всего", f"{total_area:,.1f} га")

        with col3:
            unique_types = len(set([op.tillage_type for op in tillage_operations if op.tillage_type]))
            st.metric("Типов обработок", unique_types)

    else:
        st.info("📭 История обработок пуста. Добавьте первую обработку выше.")

# Sidebar
with st.sidebar:
    st.markdown("### ℹ️ Справка")
    st.info("""
    **Обработка почвы** - регистрация механических операций по обработке почвы.

    **Типы обработки:**
    - Вспашка - оборот пласта
    - Культивация - рыхление без оборота
    - Боронование - выравнивание, крошение
    - Дискование - измельчение растительных остатков
    - Глубокое рыхление - без оборота пласта
    - Прикатывание - уплотнение почвы
    - Лущение стерни - поверхностная обработка
    - Чизелевание - глубокое рыхление чизелем
    """)

    st.markdown("### 🎯 Рекомендации")
    st.markdown("""
    - Соблюдайте оптимальную влажность почвы
    - Выбирайте правильную глубину обработки
    - Учитывайте тип почвы и культуру
    - Избегайте обработки переувлажненной почвы
    """)
