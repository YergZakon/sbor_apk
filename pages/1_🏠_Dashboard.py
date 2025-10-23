"""
Dashboard - Панель управления
Метрики, прогресс, уведомления
"""
import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from modules.database import SessionLocal, Farm, Field, Operation, AgrochemicalAnalysis
from modules.config import settings
from modules.auth import require_auth, filter_query_by_farm, get_current_user, get_user_display_name, is_admin
import plotly.express as px
import plotly.graph_objects as go

# Настройка страницы
st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")

# Требуем авторизацию
require_auth()

# Заголовок
user = get_current_user()
st.title(f"🏠 Dashboard - Панель управления")
st.caption(f"Добро пожаловать, **{get_user_display_name()}**!")

# Получение сессии БД
db = SessionLocal()

try:
    # ============================================================================
    # ОСНОВНЫЕ МЕТРИКИ
    # ============================================================================

    st.markdown("### 📊 Основные показатели")

    # Получение данных с учетом прав доступа
    # Для обычного пользователя - только его хозяйство (всегда 1)
    # Для админа - все хозяйства в системе
    if is_admin():
        farms_count = db.query(Farm).count()
        farm = db.query(Farm).first()
    else:
        user_farm_id = user.get("farm_id") if user else None
        farm = db.query(Farm).filter(Farm.id == user_farm_id).first() if user_farm_id else None
        farms_count = 1 if farm else 0

    fields_count = filter_query_by_farm(db.query(Field), Field).count()
    operations_count = filter_query_by_farm(db.query(Operation), Operation).count()

    # Расчет общей площади
    total_area = filter_query_by_farm(db.query(Field), Field).with_entities(Field.area_ha).all()
    total_area_sum = sum([f[0] for f in total_area if f[0]]) if total_area else 0

    # Метрики в 4 колонки
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Хозяйств зарегистрировано" if is_admin() else "Хозяйство",
            value=farms_count if is_admin() else (farm.name if farm else "Не зарегистрировано"),
            delta=None
        )

    with col2:
        st.metric(
            label="Полей добавлено",
            value=fields_count,
            delta=f"📊 Всего полей" if fields_count > 0 else None
        )

    with col3:
        st.metric(
            label="Общая площадь",
            value=f"{total_area_sum:,.0f} га",
            delta=None
        )

    with col4:
        st.metric(
            label="Операций выполнено",
            value=operations_count,
            delta=f"📈 Операции" if operations_count > 0 else None
        )

    st.markdown("---")

    # ============================================================================
    # ПОЛНОТА ДАННЫХ
    # ============================================================================

    st.markdown("### 📈 Полнота данных")

    # Расчет полноты данных по категориям
    # Для полей: 100% если есть поля, иначе 0%
    # Для операций: показываем прогресс до 100 операций как ориентир
    data_completeness = {
        "Общая информация хозяйства": 100 if farms_count > 0 else 0,
        "Паспорта полей": 100 if fields_count > 0 else 0,
        "Агрохимические анализы": 0,  # Будет рассчитано позже
        "Полевые работы": min(100, (operations_count / 100) * 100) if operations_count > 0 else 0,
        "Урожайность": 0,
        "Экономические данные": 0,
        "Метеоданные": 0,
        "Фитосанитария": 0,
    }

    # Агрохимические анализы
    analyses_count = filter_query_by_farm(db.query(AgrochemicalAnalysis), AgrochemicalAnalysis).count()
    if fields_count > 0:
        data_completeness["Агрохимические анализы"] = min(100, (analyses_count / fields_count) * 100)

    # Средняя полнота
    avg_completeness = sum(data_completeness.values()) / len(data_completeness)

    # Отображение общей полноты
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Текущая полнота данных",
            value=f"{avg_completeness:.1f}%",
            delta=f"Цель: 70%"
        )

    with col2:
        st.metric(
            label="ML-готовность",
            value=f"{min(avg_completeness * 1.3, 100):.1f}%",
            delta="Цель: 90%"
        )

    with col3:
        status = "✅ Отлично" if avg_completeness >= 70 else "⚠️ Требует внимания" if avg_completeness >= 40 else "❌ Критично"
        st.metric(
            label="Статус",
            value=status,
            delta=None
        )

    # Прогресс-бары по категориям
    st.markdown("#### Прогресс по категориям данных:")

    for category, completeness in data_completeness.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.progress(completeness / 100)
        with col2:
            st.write(f"{category}: **{completeness:.0f}%**")

    st.markdown("---")

    # ============================================================================
    # ВИЗУАЛИЗАЦИЯ
    # ============================================================================

    if fields_count > 0:
        st.markdown("### 📊 Визуализация данных")

        col1, col2 = st.columns(2)

        with col1:
            # График полноты данных
            fig_completeness = go.Figure(data=[
                go.Bar(
                    x=list(data_completeness.keys()),
                    y=list(data_completeness.values()),
                    marker_color=['green' if v >= 70 else 'orange' if v >= 40 else 'red' for v in data_completeness.values()],
                    text=[f"{v:.0f}%" for v in data_completeness.values()],
                    textposition='auto',
                )
            ])
            fig_completeness.update_layout(
                title="Полнота данных по категориям",
                xaxis_title="Категория",
                yaxis_title="Полнота (%)",
                yaxis_range=[0, 100],
                height=400
            )
            fig_completeness.add_hline(y=70, line_dash="dash", line_color="green", annotation_text="Цель: 70%")
            st.plotly_chart(fig_completeness, use_container_width=True)

        with col2:
            # Распределение площадей полей
            fields_data = filter_query_by_farm(db.query(Field.name, Field.area_ha).filter(Field.area_ha.isnot(None)), Field).all()
            if fields_data:
                df_fields = pd.DataFrame(fields_data, columns=['Поле', 'Площадь (га)'])

                fig_fields = px.pie(
                    df_fields,
                    values='Площадь (га)',
                    names='Поле',
                    title='Распределение площадей по полям',
                    height=400
                )
                st.plotly_chart(fig_fields, use_container_width=True)
            else:
                st.info("Добавьте поля для отображения графика")

    st.markdown("---")

    # ============================================================================
    # УВЕДОМЛЕНИЯ И ЗАДАЧИ
    # ============================================================================

    st.markdown("### 📋 Требует внимания")

    notifications = []

    # Проверка наличия хозяйства
    if farms_count == 0:
        notifications.append({
            "type": "error",
            "message": "❗ Не зарегистрировано ни одного хозяйства. Перейдите на главную страницу для регистрации."
        })

    # Проверка наличия полей
    if fields_count == 0:
        notifications.append({
            "type": "warning",
            "message": "⚠️ Не добавлено ни одного поля. Перейдите в раздел 'Управление полями' для добавления."
        })
    elif farm and farm.arable_area_ha and fields_count < 10:
        # Показываем уведомление только если полей мало относительно площади хозяйства
        notifications.append({
            "type": "info",
            "message": f"ℹ️ Добавлено {fields_count} полей. Убедитесь, что внесены все поля хозяйства."
        })

    # Проверка агрохимических анализов
    if fields_count > 0 and analyses_count == 0:
        notifications.append({
            "type": "warning",
            "message": "⚠️ Не добавлено ни одного агрохимического анализа. Рекомендуется провести анализ почвы."
        })

    # Проверка полей без координат
    fields_no_coords = filter_query_by_farm(
        db.query(Field).filter(
            (Field.center_lat.is_(None)) | (Field.center_lon.is_(None))
        ),
        Field
    ).count()

    if fields_no_coords > 0:
        notifications.append({
            "type": "info",
            "message": f"ℹ️ У {fields_no_coords} полей не указаны GPS-координаты. Добавьте координаты для отображения на карте."
        })

    # Проверка операций
    if operations_count == 0:
        notifications.append({
            "type": "info",
            "message": "ℹ️ Не зарегистрировано ни одной полевой операции. Начните вносить данные о посеве, обработках и уборке."
        })

    # Отображение уведомлений
    if notifications:
        for notif in notifications:
            if notif["type"] == "error":
                st.error(notif["message"])
            elif notif["type"] == "warning":
                st.warning(notif["message"])
            else:
                st.info(notif["message"])
    else:
        st.success("✅ Все основные данные заполнены. Продолжайте вносить информацию!")

    st.markdown("---")

    # ============================================================================
    # БЫСТРЫЕ ДЕЙСТВИЯ
    # ============================================================================

    st.markdown("### 🚀 Быстрые действия")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("➕ Добавить поле", use_container_width=True):
            st.switch_page("pages/2_🌱_Fields.py")

    with col2:
        if st.button("📥 Импорт из Excel", use_container_width=True):
            st.switch_page("pages/15_📥_Import.py")

    with col3:
        if st.button("📝 Журнал операций", use_container_width=True):
            st.switch_page("pages/3_📝_Journal.py")

    with col4:
        if st.button("🌾 Добавить посев", use_container_width=True):
            st.switch_page("pages/4_🌾_Sowing.py")

    st.markdown("---")

    # ============================================================================
    # ПОСЛЕДНИЕ ОПЕРАЦИИ
    # ============================================================================

    if operations_count > 0 and farm:
        st.markdown("### 📜 Последние операции")

        # Получение последних 10 операций с фильтрацией по хозяйству
        recent_operations = db.query(
            Operation.operation_date,
            Operation.operation_type,
            Field.name.label('field_name'),
            Operation.crop,
            Operation.area_processed_ha
        ).join(Field).filter(
            Field.farm_id == farm.id  # КРИТИЧЕСКИЙ ФИЛЬТР: только операции текущего хозяйства
        ).order_by(Operation.operation_date.desc()).limit(10).all()

        if recent_operations:
            df_operations = pd.DataFrame(recent_operations, columns=[
                'Дата', 'Тип операции', 'Поле', 'Культура', 'Площадь (га)'
            ])

            # Русские названия типов операций
            operation_types_ru = {
                'sowing': 'Посев',
                'fertilizing': 'Внесение удобрений',
                'spraying': 'Опрыскивание',
                'harvesting': 'Уборка урожая'
            }
            df_operations['Тип операции'] = df_operations['Тип операции'].map(
                lambda x: operation_types_ru.get(x, x)
            )

            st.dataframe(df_operations, use_container_width=True, hide_index=True)
        else:
            st.info("Операции еще не добавлены")

    # ============================================================================
    # СТАТИСТИКА ПО ХОЗЯЙСТВУ
    # ============================================================================

    if farms_count > 0:
        st.markdown("---")
        st.markdown("### 🏢 Информация о хозяйстве")

        if farm:
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"**Название:** {farm.name}")
                st.markdown(f"**БИН:** {farm.bin}")
                st.markdown(f"**Тип:** {farm.farm_type or 'Не указан'}")

            with col2:
                st.markdown(f"**Общая площадь:** {farm.total_area_ha or 0:,.0f} га")
                st.markdown(f"**Пашня:** {farm.arable_area_ha or 0:,.0f} га")
                st.markdown(f"**Количество полей:** {fields_count}")

            with col3:
                st.markdown(f"**Руководитель:** {farm.director_name or 'Не указано'}")
                st.markdown(f"**Телефон:** {farm.phone or 'Не указан'}")
                st.markdown(f"**Email:** {farm.email or 'Не указан'}")

finally:
    db.close()

# Sidebar
with st.sidebar:
    st.markdown("### ℹ️ Справка")
    st.info("""
    **Dashboard** показывает общее состояние данных в системе.

    **Основные разделы:**
    - Метрики и показатели
    - Полнота данных
    - Уведомления
    - Быстрые действия

    **Рекомендуемый порядок работы:**
    1. Зарегистрируйте хозяйство
    2. Добавьте поля
    3. Импортируйте данные из Excel (если есть)
    4. Начните вносить операции
    """)

    st.markdown("### 🎯 Цели")
    st.markdown(f"""
    - Полнота данных: **>70%**
    - ML-готовность: **>90%**
    - Все поля внесены: **✓**
    - Операции: **100+**
    """)
