"""
Pesticides - Учет применения средств защиты растений
"""
import streamlit as st
import pandas as pd
import json
from datetime import datetime, date, timedelta
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

# Добавляем путь к модулям
import sys
sys.path.append(str(Path(__file__).parent.parent))

from modules.database import get_db, Farm, Field, Operation, PesticideApplication
from modules.auth import (
    require_auth,
    require_farm_binding,
    filter_query_by_farm,
    get_user_display_name,
    can_edit_data,
    can_delete_data
)
from modules.validators import DataValidator
from utils.formatters import format_date, format_area, format_number

# Настройка страницы
st.set_page_config(page_title="СЗР", page_icon="🛡️", layout="wide")

# Требуем авторизацию и привязку к хозяйству
require_auth()
require_farm_binding()

st.title("🛡️ Учет применения средств защиты растений")
st.caption(f"Пользователь: **{get_user_display_name()}**")

# Инициализация валидатора
validator = DataValidator()

# Загрузка справочника СЗР
def load_pesticides_reference():
    """Загрузка справочника СЗР из JSON"""
    reference_path = Path(__file__).parent.parent / "data" / "pesticides.json"
    try:
        with open(reference_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Справочник СЗР не найден!")
        return {}

pesticides_ref = load_pesticides_reference()

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
tab1, tab2, tab3, tab4 = st.tabs(["📝 Регистрация обработки", "📊 История обработок", "📚 Справочник СЗР", "⚠️ Контроль сроков"])

# ========================================
# TAB 1: Регистрация обработки СЗР
# ========================================
with tab1:
    st.subheader("Регистрация обработки средствами защиты растений")

    with st.form("pesticide_application_form"):
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

            # Дата обработки
            application_date = st.date_input(
                "Дата обработки *",
                value=date.today(),
                help="Дата проведения обработки"
            )

            # Класс СЗР
            pesticide_classes = list(pesticides_ref.keys())
            selected_class = st.selectbox(
                "Класс препаратов *",
                options=pesticide_classes,
                help="Выберите класс средств защиты растений"
            )

            # Конкретный препарат
            pesticide_names = list(pesticides_ref[selected_class].keys()) if selected_class in pesticides_ref else []
            selected_pesticide = st.selectbox(
                "Препарат *",
                options=pesticide_names,
                help="Выберите конкретный препарат"
            )

            # Цель обработки
            treatment_target = st.selectbox(
                "Цель обработки *",
                options=[
                    "Болезни",
                    "Вредители",
                    "Сорняки",
                    "Комплексная защита",
                    "Десикация",
                    "Регулятор роста"
                ],
                help="Против чего проводится обработка"
            )

        with col2:
            # Норма расхода препарата
            rate_product = st.number_input(
                "Норма расхода препарата (л/га или кг/га) *",
                min_value=0.0,
                max_value=10.0,
                value=1.0,
                step=0.1,
                help="Норма расхода препарата"
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

            # Расход рабочего раствора
            water_rate = st.number_input(
                "Расход рабочего раствора (л/га)",
                min_value=50.0,
                max_value=600.0,
                value=200.0,
                step=10.0,
                help="Объем воды для приготовления рабочего раствора"
            )

            # Способ применения
            application_method = st.selectbox(
                "Способ применения *",
                options=[
                    "Опрыскивание наземное",
                    "Опрыскивание авиационное",
                    "Протравливание семян",
                    "Внесение в почву",
                    "Фумигация"
                ],
                help="Способ применения препарата"
            )

            # Фаза развития культуры
            growth_stage = st.text_input(
                "Фаза развития культуры",
                placeholder="Например: кущение, выход в трубку",
                help="Фаза развития культуры в момент обработки"
            )

        # Расчет потребности в препарате и воде
        st.markdown("---")
        st.markdown("### 🧮 Расчет потребности")

        if selected_pesticide and selected_class in pesticides_ref:
            pesticide_data = pesticides_ref[selected_class][selected_pesticide]

            col3, col4, col5, col6 = st.columns(4)

            total_product_needed = rate_product * area_processed
            total_water_needed = water_rate * area_processed

            with col3:
                st.metric(
                    "Препарат",
                    f"{format_number(total_product_needed, 2)} л/кг",
                    help="Общая потребность в препарате"
                )
            with col4:
                st.metric(
                    "Рабочий раствор",
                    f"{format_number(total_water_needed, 0)} л",
                    help="Общий объем рабочего раствора"
                )
            with col5:
                form = pesticide_data.get("форма_препарата", "-")
                st.metric("Форма препарата", form)
            with col6:
                active_substance = pesticide_data.get("действующее_вещество", "-")
                st.metric("Действующее вещество", active_substance[:20] + "..." if len(active_substance) > 20 else active_substance)

            # Рекомендуемая норма из справочника
            recommended_rate = pesticide_data.get("норма_расхода", {})
            if recommended_rate:
                rec_min = recommended_rate.get("мин", 0)
                rec_max = recommended_rate.get("макс", 0)
                if rec_min and rec_max:
                    if rate_product < rec_min or rate_product > rec_max:
                        st.warning(f"⚠️ Рекомендуемая норма: {rec_min}-{rec_max} л/га или кг/га")
                    else:
                        st.success(f"✅ Норма в пределах рекомендуемой: {rec_min}-{rec_max} л/га или кг/га")

            # Срок ожидания
            waiting_period = pesticide_data.get("срок_ожидания_дней", 0)
            if waiting_period:
                harvest_allowed_date = application_date + timedelta(days=waiting_period)
                st.info(f"⏱️ Срок ожидания до уборки: {waiting_period} дней (можно убирать после {format_date(harvest_allowed_date)})")

        # Погодные условия
        st.markdown("---")
        st.markdown("### 🌤️ Погодные условия")

        col7, col8, col9 = st.columns(3)

        with col7:
            temperature = st.number_input(
                "Температура воздуха (°C)",
                min_value=-10.0,
                max_value=50.0,
                value=20.0,
                step=0.5
            )

        with col8:
            wind_speed = st.number_input(
                "Скорость ветра (м/с)",
                min_value=0.0,
                max_value=20.0,
                value=2.0,
                step=0.5
            )

        with col9:
            humidity = st.number_input(
                "Влажность воздуха (%)",
                min_value=0.0,
                max_value=100.0,
                value=60.0,
                step=5.0
            )

        # Проверка погодных условий
        weather_warnings = []
        if wind_speed > 5:
            weather_warnings.append("⚠️ Высокая скорость ветра (>5 м/с) - риск сноса препарата")
        if temperature > 25:
            weather_warnings.append("⚠️ Высокая температура (>25°C) - риск испарения и фитотоксичности")
        if temperature < 10:
            weather_warnings.append("⚠️ Низкая температура (<10°C) - снижение эффективности препаратов")
        if humidity < 30:
            weather_warnings.append("⚠️ Низкая влажность (<30%) - быстрое испарение")

        if weather_warnings:
            for warning in weather_warnings:
                st.warning(warning)

        # Примечание
        notes = st.text_area(
            "Примечание",
            height=80,
            help="Дополнительная информация о обработке"
        )

        # Кнопка отправки
        submitted = st.form_submit_button("✅ Зарегистрировать обработку", use_container_width=True)

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

            # Проверка нормы
            if rate_product <= 0:
                errors.append("Норма расхода должна быть больше 0")

            if errors:
                st.error("❌ Ошибки валидации:\n" + "\n".join(f"- {e}" for e in errors))
            else:
                try:
                    # Создаем операцию
                    operation = Operation(
                        farm_id=farm.id,
                        field_id=selected_field.id,
                        operation_type="spraying",
                        operation_date=application_date,
                        area_processed_ha=area_processed,
                        notes=notes
                    )
                    db.add(operation)
                    db.flush()

                    # Создаем детали обработки СЗР
                    pesticide_application = PesticideApplication(
                        operation_id=operation.id,
                        pesticide_name=selected_pesticide,
                        pesticide_class=selected_class,
                        active_ingredient=pesticide_data.get("действующее_вещество", ""),
                        rate_per_ha=rate_product,
                        total_product_used=total_product_needed,
                        water_rate_l_ha=water_rate,
                        application_method=application_method,
                        treatment_target=treatment_target,
                        growth_stage=growth_stage if growth_stage else None,
                        temperature_c=temperature,
                        wind_speed_ms=wind_speed,
                        humidity_percent=humidity,
                        waiting_period_days=waiting_period if waiting_period else None
                    )
                    db.add(pesticide_application)

                    db.commit()

                    st.success(f"✅ Обработка зарегистрирована! Использовано {format_number(total_product_needed, 2)} л/кг препарата")
                    st.balloons()

                except Exception as e:
                    db.rollback()
                    st.error(f"❌ Ошибка при сохранении: {str(e)}")

# ========================================
# TAB 2: История обработок
# ========================================
with tab2:
    st.subheader("История обработок СЗР")

    # Фильтры
    col1, col2, col3 = st.columns(3)

    with col1:
        filter_field = st.selectbox(
            "Фильтр по полю",
            options=["Все поля"] + [f"{f.field_code} - {f.name}" for f in fields],
            key="filter_field_history"
        )

    with col2:
        filter_class = st.selectbox(
            "Фильтр по классу",
            options=["Все классы"] + pesticide_classes,
            key="filter_class_history"
        )

    with col3:
        filter_year = st.selectbox(
            "Фильтр по году",
            options=["Все годы"] + list(range(datetime.now().year, datetime.now().year - 10, -1)),
            key="filter_year_history"
        )

    # Получение данных
    query = db.query(Operation, PesticideApplication, Field).join(
        PesticideApplication, Operation.id == PesticideApplication.operation_id
    ).join(
        Field, Operation.field_id == Field.id
    ).filter(
        Operation.operation_type == "spraying"
    )

    # Применение фильтров
    if filter_field != "Все поля":
        field_code = filter_field.split(" - ")[0]
        query = query.filter(Field.field_code == field_code)

    if filter_class != "Все классы":
        query = query.filter(PesticideApplication.pesticide_class == filter_class)

    if filter_year != "Все годы":
        from sqlalchemy import extract
        query = query.filter(extract('year', Operation.operation_date) == filter_year)

    applications = query.order_by(Operation.operation_date.desc()).all()

    if applications:
        st.metric("Всего обработок", len(applications))

        # Таблица
        data = []
        for op, pest_app, field in applications:
            data.append({
                "Дата": format_date(op.operation_date),
                "Поле": f"{field.field_code} - {field.name}",
                "Класс": pest_app.pesticide_class,
                "Препарат": pest_app.pesticide_name,
                "Норма": f"{format_number(pest_app.rate_per_ha, 2)} л/га",
                "Площадь (га)": format_area(op.area_processed_ha),
                "Всего": f"{format_number(pest_app.total_product_used, 2)} л/кг",
                "Цель": pest_app.treatment_target,
                "Способ": pest_app.application_method
            })

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Статистика
        st.markdown("---")
        st.markdown("### 📊 Статистика")

        col1, col2, col3, col4 = st.columns(4)

        total_product = sum(pest_app.total_product_used for _, pest_app, _ in applications)
        total_area = sum(op.area_processed_ha for op, _, _ in applications)
        avg_rate = total_product / total_area if total_area > 0 else 0

        with col1:
            st.metric("Всего обработок", len(applications))
        with col2:
            st.metric("Обработано площади", format_area(total_area))
        with col3:
            st.metric("Израсходовано препаратов", f"{format_number(total_product, 1)} л/кг")
        with col4:
            st.metric("Средняя норма", f"{format_number(avg_rate, 2)} л/га")

        # Графики
        col1, col2 = st.columns(2)

        with col1:
            # График по классам
            class_data = {}
            for _, pest_app, _ in applications:
                pest_class = pest_app.pesticide_class
                class_data[pest_class] = class_data.get(pest_class, 0) + 1

            fig_class = px.pie(
                values=list(class_data.values()),
                names=list(class_data.keys()),
                title="Распределение по классам СЗР"
            )
            st.plotly_chart(fig_class, use_container_width=True)

        with col2:
            # График по целям
            target_data = {}
            for _, pest_app, _ in applications:
                target = pest_app.treatment_target
                target_data[target] = target_data.get(target, 0) + 1

            fig_target = px.pie(
                values=list(target_data.values()),
                names=list(target_data.keys()),
                title="Распределение по целям обработки"
            )
            st.plotly_chart(fig_target, use_container_width=True)

        # График расхода по полям
        field_data = {}
        for op, pest_app, field in applications:
            field_name = f"{field.field_code}"
            field_data[field_name] = field_data.get(field_name, 0) + pest_app.total_product_used

        if field_data:
            fig_fields = px.bar(
                x=list(field_data.keys()),
                y=list(field_data.values()),
                title="Расход препаратов по полям (л/кг)",
                labels={"x": "Поля", "y": "Расход (л/кг)"}
            )
            st.plotly_chart(fig_fields, use_container_width=True)

    else:
        st.info("📭 Пока нет записей об обработках СЗР")

# ========================================
# TAB 3: Справочник СЗР
# ========================================
with tab3:
    st.subheader("Справочник средств защиты растений")

    if pesticides_ref:
        # Выбор класса
        selected_cat = st.selectbox(
            "Выберите класс препаратов",
            options=pesticide_classes,
            key="reference_class"
        )

        if selected_cat in pesticides_ref:
            st.markdown(f"### {selected_cat}")

            # Таблица препаратов
            ref_data = []
            for pest_name, pest_info in pesticides_ref[selected_cat].items():
                rate_info = pest_info.get("норма_расхода", {})
                rate_str = f"{rate_info.get('мин', '-')}-{rate_info.get('макс', '-')} {rate_info.get('единица', '')}" if rate_info else "-"

                ref_data.append({
                    "Название": pest_name,
                    "Действующее вещество": pest_info.get("действующее_вещество", "-"),
                    "Форма": pest_info.get("форма_препарата", "-"),
                    "Норма расхода": rate_str,
                    "Срок ожидания (дней)": pest_info.get("срок_ожидания_дней", "-"),
                    "Класс опасности": pest_info.get("класс_опасности", "-")
                })

            df_ref = pd.DataFrame(ref_data)
            st.dataframe(df_ref, use_container_width=True, hide_index=True)

            # Детальная информация о выбранном препарате
            selected_pest = st.selectbox(
                "Выберите препарат для детальной информации",
                options=list(pesticides_ref[selected_cat].keys()),
                key="detail_pesticide"
            )

            if selected_pest:
                pest_detail = pesticides_ref[selected_cat][selected_pest]

                st.markdown(f"#### {selected_pest}")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Основная информация:**")
                    st.write(f"- **Действующее вещество:** {pest_detail.get('действующее_вещество', '-')}")
                    st.write(f"- **Форма препарата:** {pest_detail.get('форма_препарата', '-')}")
                    st.write(f"- **Класс опасности:** {pest_detail.get('класс_опасности', '-')}")
                    st.write(f"- **Срок ожидания:** {pest_detail.get('срок_ожидания_дней', '-')} дней")

                with col2:
                    st.markdown("**Применение:**")
                    rate_info = pest_detail.get("норма_расхода", {})
                    if rate_info:
                        st.write(f"- **Норма расхода:** {rate_info.get('мин', '-')}-{rate_info.get('макс', '-')} {rate_info.get('единица', '')}")
                    st.write(f"- **Цель:** {pest_detail.get('цель_применения', '-')}")
                    st.write(f"- **Культура:** {pest_detail.get('культура', '-')}")

    else:
        st.warning("Справочник СЗР не загружен")

# ========================================
# TAB 4: Контроль сроков
# ========================================
with tab4:
    st.subheader("Контроль сроков ожидания")

    # Получение обработок с непрошедшим сроком ожидания
    query = db.query(Operation, PesticideApplication, Field).join(
        PesticideApplication, Operation.id == PesticideApplication.operation_id
    ).join(
        Field, Operation.field_id == Field.id
    ).filter(
        Operation.operation_type == "spraying",
        PesticideApplication.waiting_period_days.isnot(None)
    )

    applications_with_waiting = query.order_by(Operation.operation_date.desc()).all()

    if applications_with_waiting:
        # Таблица со сроками
        data = []
        today = date.today()

        for op, pest_app, field in applications_with_waiting:
            waiting_days = pest_app.waiting_period_days
            harvest_allowed_date = op.operation_date + timedelta(days=waiting_days)
            days_remaining = (harvest_allowed_date - today).days

            status = "✅ Можно убирать" if days_remaining <= 0 else f"⏳ Осталось {days_remaining} дней"
            status_color = "🟢" if days_remaining <= 0 else ("🟡" if days_remaining <= 7 else "🔴")

            data.append({
                "Статус": status_color,
                "Поле": f"{field.field_code} - {field.name}",
                "Дата обработки": format_date(op.operation_date),
                "Препарат": pest_app.pesticide_name,
                "Срок ожидания": f"{waiting_days} дней",
                "Можно убирать": format_date(harvest_allowed_date),
                "Осталось дней": days_remaining if days_remaining > 0 else 0,
                "Статус текст": status
            })

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Уведомления
        urgent = [d for d in data if 0 < d["Осталось дней"] <= 7]
        if urgent:
            st.warning(f"⚠️ Внимание! У {len(urgent)} полей срок ожидания истекает в течение 7 дней")

        ready = [d for d in data if d["Осталось дней"] <= 0]
        if ready:
            st.success(f"✅ Готово к уборке: {len(ready)} полей")

    else:
        st.info("📭 Нет обработок с заданным сроком ожидания")

# Футер
st.markdown("---")
st.markdown("🛡️ **Учет применения СЗР** | Версия 1.0")
