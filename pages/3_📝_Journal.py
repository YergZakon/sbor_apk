"""
Journal - Журнал полевых работ
Единая таблица всех операций с фильтрацией
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from modules.database import SessionLocal, Farm, Field, Operation
from modules.config import settings

# Настройка страницы
st.set_page_config(page_title="Журнал операций", page_icon="📝", layout="wide")

# Заголовок
st.title("📝 Журнал полевых работ")

# Получение сессии БД
db = SessionLocal()

try:
    # Проверка наличия хозяйства
    farm = db.query(Farm).first()

    if not farm:
        st.error("❌ Сначала необходимо зарегистрировать хозяйство!")
        st.stop()

    # Получение полей
    fields = db.query(Field).filter(Field.farm_id == farm.id).all()

    if not fields:
        st.warning("⚠️ Сначала добавьте поля в разделе 'Fields'")
        st.stop()

    # ============================================================================
    # ФИЛЬТРЫ
    # ============================================================================

    st.markdown("### 🔍 Фильтры")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Фильтр по типу операции
        operation_types = {
            "Все": None,
            "Посев": "sowing",
            "Внесение удобрений": "fertilizing",
            "Опрыскивание": "spraying",
            "Уборка": "harvesting"
        }

        selected_type = st.selectbox(
            "Тип операции",
            options=list(operation_types.keys())
        )

    with col2:
        # Фильтр по полю
        field_options = {"Все поля": None}
        field_options.update({f.name or f.field_code: f.id for f in fields})

        selected_field = st.selectbox(
            "Поле",
            options=list(field_options.keys())
        )

    with col3:
        # Фильтр по дате (начало)
        date_from = st.date_input(
            "Дата с",
            value=datetime.now() - timedelta(days=365),
            help="Начало периода"
        )

    with col4:
        # Фильтр по дате (конец)
        date_to = st.date_input(
            "Дата по",
            value=datetime.now(),
            help="Конец периода"
        )

    st.markdown("---")

    # ============================================================================
    # ПОЛУЧЕНИЕ ДАННЫХ С ФИЛЬТРАЦИЕЙ
    # ============================================================================

    # Базовый запрос
    query = db.query(
        Operation.id,
        Operation.operation_date,
        Operation.operation_type,
        Field.name.label('field_name'),
        Field.field_code,
        Operation.crop,
        Operation.variety,
        Operation.area_processed_ha,
        Operation.operator,
        Operation.notes
    ).join(Field)

    # Применение фильтров
    if operation_types[selected_type]:
        query = query.filter(Operation.operation_type == operation_types[selected_type])

    if field_options[selected_field]:
        query = query.filter(Operation.field_id == field_options[selected_field])

    if date_from:
        query = query.filter(Operation.operation_date >= date_from)

    if date_to:
        query = query.filter(Operation.operation_date <= date_to)

    # Сортировка по дате (новые сверху)
    query = query.order_by(Operation.operation_date.desc())

    # Выполнение запроса
    operations = query.all()

    # ============================================================================
    # ОТОБРАЖЕНИЕ ДАННЫХ
    # ============================================================================

    st.markdown(f"### 📋 Найдено операций: {len(operations)}")

    if operations:
        # Создание DataFrame
        df_operations = pd.DataFrame(operations, columns=[
            'ID',
            'Дата',
            'Тип операции',
            'Поле',
            'Код поля',
            'Культура',
            'Сорт',
            'Площадь (га)',
            'Оператор',
            'Примечания'
        ])

        # Русские названия типов операций
        operation_types_ru = {
            'sowing': '🌾 Посев',
            'fertilizing': '💊 Удобрения',
            'spraying': '🛡️ Опрыскивание',
            'harvesting': '🚜 Уборка'
        }

        df_operations['Тип операции'] = df_operations['Тип операции'].map(
            lambda x: operation_types_ru.get(x, x) if x else '-'
        )

        # Форматирование даты
        df_operations['Дата'] = pd.to_datetime(df_operations['Дата']).dt.strftime('%Y-%m-%d')

        # Замена None на '-'
        df_operations = df_operations.fillna('-')

        # Отображение таблицы с настройками
        st.dataframe(
            df_operations,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.NumberColumn("ID", width="small"),
                "Дата": st.column_config.TextColumn("Дата", width="medium"),
                "Тип операции": st.column_config.TextColumn("Тип операции", width="medium"),
                "Поле": st.column_config.TextColumn("Поле", width="medium"),
                "Площадь (га)": st.column_config.NumberColumn("Площадь (га)", format="%.1f", width="small"),
            }
        )

        # ============================================================================
        # СТАТИСТИКА
        # ============================================================================

        st.markdown("---")
        st.markdown("### 📊 Статистика по операциям")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Всего операций", len(operations))

        with col2:
            # Обработанная площадь
            total_area = sum([op.area_processed_ha for op in operations if op.area_processed_ha])
            st.metric("Обработано всего", f"{total_area:,.1f} га")

        with col3:
            # Уникальные поля
            unique_fields = len(set([op.field_name for op in operations]))
            st.metric("Полей задействовано", unique_fields)

        with col4:
            # Уникальные культуры
            unique_crops = len(set([op.crop for op in operations if op.crop]))
            st.metric("Культур", unique_crops)

        # ============================================================================
        # ГРАФИКИ
        # ============================================================================

        col1, col2 = st.columns(2)

        with col1:
            # График по типам операций
            operations_by_type = df_operations['Тип операции'].value_counts()

            import plotly.express as px

            fig_types = px.pie(
                values=operations_by_type.values,
                names=operations_by_type.index,
                title='Распределение по типам операций',
                height=300
            )
            st.plotly_chart(fig_types, use_container_width=True)

        with col2:
            # График по полям
            operations_by_field = df_operations['Поле'].value_counts().head(10)

            fig_fields = px.bar(
                x=operations_by_field.index,
                y=operations_by_field.values,
                title='Топ-10 полей по количеству операций',
                labels={'x': 'Поле', 'y': 'Количество операций'},
                height=300
            )
            st.plotly_chart(fig_fields, use_container_width=True)

        # ============================================================================
        # ЭКСПОРТ
        # ============================================================================

        st.markdown("---")
        st.markdown("### 📥 Экспорт данных")

        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            # Экспорт в CSV
            csv = df_operations.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📄 Скачать CSV",
                data=csv,
                file_name=f"journal_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col2:
            # Экспорт в Excel
            from io import BytesIO

            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_operations.to_excel(writer, index=False, sheet_name='Журнал')
            excel_data = output.getvalue()

            st.download_button(
                label="📊 Скачать Excel",
                data=excel_data,
                file_name=f"journal_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    else:
        st.info("📭 Операции не найдены. Измените фильтры или добавьте новые операции.")

        # Быстрые ссылки
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🌾 Добавить посев", use_container_width=True):
                st.switch_page("pages/4_🌾_Sowing.py")

        with col2:
            if st.button("💊 Внести удобрения", use_container_width=True):
                st.switch_page("pages/5_💊_Fertilizers.py")

        with col3:
            if st.button("🛡️ Опрыскивание", use_container_width=True):
                st.switch_page("pages/6_🛡️_Pesticides.py")

    st.markdown("---")

    # ============================================================================
    # ДЕТАЛЬНАЯ ИНФОРМАЦИЯ ПО ОПЕРАЦИИ
    # ============================================================================

    if operations:
        st.markdown("### 🔍 Детали операции")

        # Выбор операции для просмотра деталей
        operation_options = {
            f"{op.operation_date} - {operation_types_ru.get(op.operation_type, op.operation_type)} - {op.field_name or op.field_code}": op.id
            for op in operations[:50]  # Ограничение для производительности
        }

        if operation_options:
            selected_op_name = st.selectbox(
                "Выберите операцию для просмотра деталей:",
                options=list(operation_options.keys())
            )

            if selected_op_name:
                selected_op_id = operation_options[selected_op_name]
                selected_op = db.query(Operation).filter(Operation.id == selected_op_id).first()

                if selected_op:
                    with st.expander("📝 Детальная информация", expanded=False):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown(f"**ID операции:** {selected_op.id}")
                            st.markdown(f"**Дата:** {selected_op.operation_date}")
                            st.markdown(f"**Тип:** {operation_types_ru.get(selected_op.operation_type, selected_op.operation_type)}")
                            st.markdown(f"**Культура:** {selected_op.crop or '-'}")
                            st.markdown(f"**Сорт:** {selected_op.variety or '-'}")

                        with col2:
                            field = db.query(Field).filter(Field.id == selected_op.field_id).first()
                            st.markdown(f"**Поле:** {field.name or field.field_code if field else '-'}")
                            st.markdown(f"**Площадь обработанная:** {selected_op.area_processed_ha or '-'} га")
                            st.markdown(f"**Оператор:** {selected_op.operator or '-'}")
                            st.markdown(f"**Техника ID:** {selected_op.machine_id or '-'}")

                        if selected_op.notes:
                            st.markdown("**Примечания:**")
                            st.info(selected_op.notes)

                        if selected_op.weather_conditions:
                            st.markdown("**Погодные условия:**")
                            st.info(selected_op.weather_conditions)

finally:
    db.close()

# Sidebar
with st.sidebar:
    st.markdown("### ℹ️ Справка")
    st.info("""
    **Журнал полевых работ** - единая таблица всех операций с возможностью фильтрации.

    **Возможности:**
    - Фильтрация по типу, полю, дате
    - Просмотр статистики
    - Экспорт в CSV/Excel
    - Детальная информация

    **Типы операций:**
    - 🌾 Посев
    - 💊 Внесение удобрений
    - 🛡️ Опрыскивание СЗР
    - 🚜 Уборка урожая
    """)

    st.markdown("### 🎯 Быстрые действия")
    st.markdown("""
    Используйте навигацию слева для добавления новых операций.
    """)

    st.markdown("### 📊 Рекомендации")
    st.markdown("""
    - Вносите данные своевременно
    - Указывайте всю доступную информацию
    - Регулярно экспортируйте данные
    - Проверяйте полноту записей
    """)
