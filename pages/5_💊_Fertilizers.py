"""
Fertilizers - Учет внесения удобрений
"""
import streamlit as st
import pandas as pd
import json
from datetime import datetime, date
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

# Добавляем путь к модулям
import sys
sys.path.append(str(Path(__file__).parent.parent))

from modules.database import get_db, Farm, Field, Operation, FertilizerApplication
from modules.auth import (
    require_auth,
    require_farm_binding,
    filter_query_by_farm,
    get_user_display_name,
    can_edit_data,
    can_delete_data
)
from modules.validators import DataValidator
from utils.formatters import format_date, format_area, format_number, format_npk

# Настройка страницы
st.set_page_config(page_title="Удобрения", page_icon="💊", layout="wide")

# Требуем авторизацию и привязку к хозяйству
require_auth()
require_farm_binding()

st.title("💊 Учет внесения удобрений")
st.caption(f"Пользователь: **{get_user_display_name()}**")

# Инициализация валидатора
validator = DataValidator()

# Загрузка справочника удобрений
def load_fertilizers_reference():
    """Загрузка справочника удобрений из JSON"""
    reference_path = Path(__file__).parent.parent / "data" / "fertilizers.json"
    try:
        with open(reference_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Справочник удобрений не найден!")
        return {}

fertilizers_ref = load_fertilizers_reference()

# Подключение к БД
db = next(get_db())

# Проверка наличия хозяйства
farm = filter_query_by_farm(db.query(Farm), Farm).first()
if not farm:
    st.warning("⚠️ Сначала создайте хозяйство на странице импорта!")
    st.stop()

# Получение списка полей
fields = filter_query_by_farm(db.query(Field), Field).all()
if not fields:
    st.warning("⚠️ Сначала добавьте поля на странице 'Поля'!")
    st.stop()

# Табы
tab1, tab2, tab3 = st.tabs(["📝 Регистрация внесения", "📊 История внесений", "📚 Справочник удобрений"])

# ========================================
# TAB 1: Регистрация внесения удобрений
# ========================================
with tab1:
    st.subheader("Регистрация внесения удобрений")

    with st.form("fertilizer_application_form"):
        col1, col2 = st.columns(2)

        with col1:
            # Выбор поля
            field_options = {f"{f.field_code} - {f.name}": f for f in fields}
            selected_field_name = st.selectbox(
                "Поле *",
                options=list(field_options.keys()),
                help="Выберите поле для внесения удобрений"
            )
            selected_field = field_options[selected_field_name]

            # Дата внесения
            application_date = st.date_input(
                "Дата внесения *",
                value=date.today(),
                help="Дата внесения удобрений"
            )

            # Тип удобрений
            fertilizer_categories = list(fertilizers_ref.keys())
            selected_category = st.selectbox(
                "Категория удобрений *",
                options=fertilizer_categories,
                help="Выберите категорию удобрений"
            )

            # Конкретное удобрение
            fertilizer_names = list(fertilizers_ref[selected_category].keys()) if selected_category in fertilizers_ref else []
            selected_fertilizer = st.selectbox(
                "Удобрение *",
                options=fertilizer_names,
                help="Выберите конкретное удобрение"
            )

        with col2:
            # Норма внесения
            rate_kg_ha = st.number_input(
                "Норма внесения (кг/га) *",
                min_value=0.0,
                max_value=2000.0,
                value=100.0,
                step=10.0,
                help="Норма внесения в физическом весе"
            )

            # Обработанная площадь
            area_processed = st.number_input(
                "Обработанная площадь (га) *",
                min_value=0.1,
                max_value=selected_field.area_ha,
                value=selected_field.area_ha,
                step=0.1,
                help=f"Площадь поля: {format_area(selected_field.area_ha)}"
            )

            # Способ внесения
            application_method = st.selectbox(
                "Способ внесения *",
                options=[
                    "Разбрасывание",
                    "Локальное внесение",
                    "Фертигация",
                    "Листовая подкормка",
                    "Внесение с посевом"
                ],
                help="Способ внесения удобрений"
            )

            # Цель внесения
            application_purpose = st.selectbox(
                "Цель внесения",
                options=[
                    "Основное удобрение",
                    "Припосевное удобрение",
                    "Подкормка",
                    "Коррекция дефицита"
                ],
                help="Цель внесения удобрений"
            )

        # Расчет д.в. (действующего вещества)
        st.markdown("---")
        st.markdown("### 🧮 Расчет действующего вещества (NPK)")

        if selected_fertilizer and selected_category in fertilizers_ref:
            fertilizer_data = fertilizers_ref[selected_category][selected_fertilizer]

            col3, col4, col5, col6 = st.columns(4)

            # Содержание NPK в удобрении
            n_content = fertilizer_data.get("N", 0)
            p_content = fertilizer_data.get("P", 0)
            k_content = fertilizer_data.get("K", 0)

            with col3:
                st.metric("Содержание N", f"{n_content}%")
            with col4:
                st.metric("Содержание P", f"{p_content}%")
            with col5:
                st.metric("Содержание K", f"{k_content}%")
            with col6:
                st.metric("Формула NPK", format_npk(n_content, p_content, k_content))

            # Расчет внесенного д.в.
            total_fertilizer_kg = rate_kg_ha * area_processed
            n_applied = total_fertilizer_kg * n_content / 100
            p_applied = total_fertilizer_kg * p_content / 100
            k_applied = total_fertilizer_kg * k_content / 100

            st.markdown("#### Внесено действующего вещества:")
            col7, col8, col9, col10 = st.columns(4)

            with col7:
                st.metric("Всего удобрений", f"{format_number(total_fertilizer_kg, 0)} кг")
            with col8:
                st.metric("Азот (N)", f"{format_number(n_applied, 1)} кг д.в.")
            with col9:
                st.metric("Фосфор (P)", f"{format_number(p_applied, 1)} кг д.в.")
            with col10:
                st.metric("Калий (K)", f"{format_number(k_applied, 1)} кг д.в.")

            # Расчет на 1 га
            n_per_ha = n_applied / area_processed if area_processed > 0 else 0
            p_per_ha = p_applied / area_processed if area_processed > 0 else 0
            k_per_ha = k_applied / area_processed if area_processed > 0 else 0

            st.info(f"📊 На 1 га внесено: {format_npk(n_per_ha, p_per_ha, k_per_ha)}")

        # Примечание
        notes = st.text_area(
            "Примечание",
            height=80,
            help="Дополнительная информация о внесении удобрений"
        )

        # Кнопка отправки
        submitted = st.form_submit_button("✅ Зарегистрировать внесение", use_container_width=True)

        if submitted:
            # Валидация
            errors = []

            # Проверка даты
            is_valid, msg = validator.validate_date(application_date)
            if not is_valid:
                errors.append(f"Дата: {msg}")

            # Проверка площади
            is_valid, msg = validator.validate_area(area_processed)
            if not is_valid:
                errors.append(f"Площадь: {msg}")

            if area_processed > selected_field.area_ha:
                errors.append(f"Обработанная площадь ({area_processed} га) превышает площадь поля ({selected_field.area_ha} га)")

            # Проверка нормы внесения
            if rate_kg_ha <= 0:
                errors.append("Норма внесения должна быть больше 0")

            if errors:
                st.error("❌ Ошибки валидации:\n" + "\n".join(f"- {e}" for e in errors))
            else:
                try:
                    # Создаем операцию
                    operation = Operation(
                        farm_id=farm.id,
                        field_id=selected_field.id,
                        operation_type="fertilizing",
                        operation_date=application_date,
                        area_processed_ha=area_processed,
                        notes=notes
                    )
                    db.add(operation)
                    db.flush()  # Получаем ID операции

                    # Создаем детали внесения удобрений
                    fertilizer_application = FertilizerApplication(
                        operation_id=operation.id,
                        fertilizer_name=selected_fertilizer,
                        fertilizer_type=selected_category,
                        rate_kg_ha=rate_kg_ha,
                        total_fertilizer_kg=total_fertilizer_kg,
                        n_content_percent=n_content,
                        p_content_percent=p_content,
                        k_content_percent=k_content,
                        n_applied_kg=n_applied,
                        p_applied_kg=p_applied,
                        k_applied_kg=k_applied,
                        application_method=application_method,
                        application_purpose=application_purpose
                    )
                    db.add(fertilizer_application)

                    db.commit()

                    st.success(f"✅ Внесение удобрений зарегистрировано! Внесено {format_number(total_fertilizer_kg, 0)} кг удобрений")
                    st.balloons()

                except Exception as e:
                    db.rollback()
                    st.error(f"❌ Ошибка при сохранении: {str(e)}")

# ========================================
# TAB 2: История внесений
# ========================================
with tab2:
    st.subheader("История внесений удобрений")

    # Фильтры
    col1, col2, col3 = st.columns(3)

    with col1:
        filter_field = st.selectbox(
            "Фильтр по полю",
            options=["Все поля"] + [f"{f.field_code} - {f.name}" for f in fields],
            key="filter_field_history"
        )

    with col2:
        filter_category = st.selectbox(
            "Фильтр по категории",
            options=["Все категории"] + fertilizer_categories,
            key="filter_category_history"
        )

    with col3:
        filter_year = st.selectbox(
            "Фильтр по году",
            options=["Все годы"] + list(range(datetime.now().year, datetime.now().year - 10, -1)),
            key="filter_year_history"
        )

    # Получение данных
    query = db.query(Operation, FertilizerApplication, Field).join(
        FertilizerApplication, Operation.id == FertilizerApplication.operation_id
    ).join(
        Field, Operation.field_id == Field.id
    ).filter(
        Operation.operation_type == "fertilizing"
    )

    # Применение фильтров
    if filter_field != "Все поля":
        field_code = filter_field.split(" - ")[0]
        query = query.filter(Field.field_code == field_code)

    if filter_category != "Все категории":
        query = query.filter(FertilizerApplication.fertilizer_type == filter_category)

    if filter_year != "Все годы":
        from sqlalchemy import extract
        query = query.filter(extract('year', Operation.operation_date) == filter_year)

    applications = query.order_by(Operation.operation_date.desc()).all()

    if applications:
        st.metric("Всего внесений", len(applications))

        # Таблица
        data = []
        for op, fert_app, field in applications:
            data.append({
                "Дата": format_date(op.operation_date),
                "Поле": f"{field.field_code} - {field.name}",
                "Категория": fert_app.fertilizer_type,
                "Удобрение": fert_app.fertilizer_name,
                "Норма (кг/га)": format_number(fert_app.rate_kg_ha, 1),
                "Площадь (га)": format_area(op.area_processed_ha),
                "Всего (кг)": format_number(fert_app.total_fertilizer_kg, 0),
                "NPK д.в. (кг)": f"N:{format_number(fert_app.n_applied_kg, 1)} P:{format_number(fert_app.p_applied_kg, 1)} K:{format_number(fert_app.k_applied_kg, 1)}",
                "Способ": fert_app.application_method
            })

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Статистика
        st.markdown("---")
        st.markdown("### 📊 Статистика")

        col1, col2, col3, col4 = st.columns(4)

        total_fertilizer = sum(fert_app.total_fertilizer_kg for _, fert_app, _ in applications)
        total_n = sum(fert_app.n_applied_kg for _, fert_app, _ in applications)
        total_p = sum(fert_app.p_applied_kg for _, fert_app, _ in applications)
        total_k = sum(fert_app.k_applied_kg for _, fert_app, _ in applications)

        with col1:
            st.metric("Всего внесено удобрений", f"{format_number(total_fertilizer, 0)} кг")
        with col2:
            st.metric("Азот (N) д.в.", f"{format_number(total_n, 1)} кг")
        with col3:
            st.metric("Фосфор (P) д.в.", f"{format_number(total_p, 1)} кг")
        with col4:
            st.metric("Калий (K) д.в.", f"{format_number(total_k, 1)} кг")

        # Графики
        col1, col2 = st.columns(2)

        with col1:
            # График по категориям
            category_data = {}
            for _, fert_app, _ in applications:
                category = fert_app.fertilizer_type
                category_data[category] = category_data.get(category, 0) + fert_app.total_fertilizer_kg

            fig_category = px.pie(
                values=list(category_data.values()),
                names=list(category_data.keys()),
                title="Распределение по категориям удобрений (кг)"
            )
            st.plotly_chart(fig_category, use_container_width=True)

        with col2:
            # График NPK
            npk_data = {
                "Элемент": ["Азот (N)", "Фосфор (P)", "Калий (K)"],
                "Количество (кг д.в.)": [total_n, total_p, total_k]
            }
            fig_npk = px.bar(
                npk_data,
                x="Элемент",
                y="Количество (кг д.в.)",
                title="Внесено действующего вещества NPK",
                color="Элемент",
                color_discrete_map={
                    "Азот (N)": "#1f77b4",
                    "Фосфор (P)": "#ff7f0e",
                    "Калий (K)": "#2ca02c"
                }
            )
            st.plotly_chart(fig_npk, use_container_width=True)

        # График по полям
        field_data = {}
        for op, fert_app, field in applications:
            field_name = f"{field.field_code} - {field.name}"
            if field_name not in field_data:
                field_data[field_name] = {"N": 0, "P": 0, "K": 0}
            field_data[field_name]["N"] += fert_app.n_applied_kg
            field_data[field_name]["P"] += fert_app.p_applied_kg
            field_data[field_name]["K"] += fert_app.k_applied_kg

        if field_data:
            fields_list = list(field_data.keys())
            n_values = [field_data[f]["N"] for f in fields_list]
            p_values = [field_data[f]["P"] for f in fields_list]
            k_values = [field_data[f]["K"] for f in fields_list]

            fig_fields = go.Figure(data=[
                go.Bar(name='Азот (N)', x=fields_list, y=n_values),
                go.Bar(name='Фосфор (P)', x=fields_list, y=p_values),
                go.Bar(name='Калий (K)', x=fields_list, y=k_values)
            ])
            fig_fields.update_layout(
                barmode='group',
                title="Внесение NPK по полям (кг д.в.)",
                xaxis_title="Поля",
                yaxis_title="Количество (кг д.в.)"
            )
            st.plotly_chart(fig_fields, use_container_width=True)

    else:
        st.info("📭 Пока нет записей о внесении удобрений")

# ========================================
# TAB 3: Справочник удобрений
# ========================================
with tab3:
    st.subheader("Справочник удобрений")

    if fertilizers_ref:
        # Выбор категории
        selected_cat = st.selectbox(
            "Выберите категорию",
            options=fertilizer_categories,
            key="reference_category"
        )

        if selected_cat in fertilizers_ref:
            st.markdown(f"### {selected_cat}")

            # Таблица удобрений
            ref_data = []
            for fert_name, fert_info in fertilizers_ref[selected_cat].items():
                ref_data.append({
                    "Название": fert_name,
                    "N (%)": fert_info.get("N", 0),
                    "P (%)": fert_info.get("P", 0),
                    "K (%)": fert_info.get("K", 0),
                    "Формула": format_npk(fert_info.get("N", 0), fert_info.get("P", 0), fert_info.get("K", 0)),
                    "Форма": fert_info.get("форма", "-"),
                    "Растворимость": fert_info.get("растворимость", "-")
                })

            df_ref = pd.DataFrame(ref_data)
            st.dataframe(df_ref, use_container_width=True, hide_index=True)

            # Рекомендации
            st.markdown("---")
            st.markdown("### 💡 Рекомендации по применению")

            st.info("""
            **Общие рекомендации:**
            - Основное внесение: осенью под вспашку (фосфорно-калийные) или весной под культивацию (азотные)
            - Припосевное: локально в рядки при посеве (комплексные удобрения)
            - Подкормка: в период вегетации (азотные удобрения)
            - Листовая подкормка: микроэлементы в фазы активного роста

            **Нормы внесения для пшеницы в Акмолинской области:**
            - Азот (N): 60-90 кг д.в./га
            - Фосфор (P): 40-60 кг д.в./га
            - Калий (K): 20-40 кг д.в./га
            """)
    else:
        st.warning("Справочник удобрений не загружен")

# Футер
st.markdown("---")
st.markdown("💊 **Учет внесения удобрений** | Версия 1.0")
