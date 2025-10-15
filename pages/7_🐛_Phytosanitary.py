"""
Phytosanitary - Фитосанитарный мониторинг (болезни, вредители, сорняки)
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

from modules.database import get_db, Farm, Field, PhytosanitaryMonitoring
from modules.validators import DataValidator
from utils.formatters import format_date, format_area

# Настройка страницы
st.set_page_config(page_title="Фитосанитария", page_icon="🐛", layout="wide")

st.title("🐛 Фитосанитарный мониторинг")

# Инициализация валидатора
validator = DataValidator()

# Загрузка справочников
def load_reference(filename):
    """Загрузка справочника из JSON"""
    reference_path = Path(__file__).parent.parent / "data" / filename
    try:
        with open(reference_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Справочник {filename} не найден!")
        return {}

diseases_ref = load_reference("diseases.json")
pests_ref = load_reference("pests.json")
weeds_ref = load_reference("weeds.json")

# Подключение к БД
db = next(get_db())

# Проверка наличия хозяйства
farm = db.query(Farm).first()
if not farm:
    st.warning("⚠️ Сначала создайте хозяйство на странице Farm Setup!")
    st.stop()

# Получение списка полей
fields = db.query(Field).filter(Field.farm_id == farm.id).all()
if not fields:
    st.warning("⚠️ Сначала добавьте поля на странице 'Поля'!")
    st.stop()

# Табы
tab1, tab2, tab3, tab4 = st.tabs(["📝 Регистрация мониторинга", "📊 История мониторинга", "📚 Справочники", "⚠️ Пороги вредоносности"])

# ========================================
# TAB 1: Регистрация мониторинга
# ========================================
with tab1:
    st.subheader("Регистрация фитосанитарного мониторинга")

    with st.form("phytosanitary_form"):
        col1, col2 = st.columns(2)

        with col1:
            # Выбор поля
            field_options = {f"{f.field_code} - {f.name}": f for f in fields}
            selected_field_name = st.selectbox(
                "Поле *",
                options=list(field_options.keys()),
                help="Выберите поле для мониторинга"
            )
            selected_field = field_options[selected_field_name]

            # Дата мониторинга
            monitoring_date = st.date_input(
                "Дата обследования *",
                value=date.today(),
                help="Дата проведения фитосанитарного обследования"
            )

            # Тип проблемы
            problem_type = st.selectbox(
                "Тип проблемы *",
                options=["Болезнь", "Вредитель", "Сорняк"],
                help="Выберите тип фитосанитарной проблемы"
            )

        with col2:
            # Культура
            crop = st.text_input(
                "Культура *",
                help="Какая культура растет на поле"
            )

            # Фаза развития
            growth_stage = st.selectbox(
                "Фаза развития культуры *",
                options=[
                    "Всходы",
                    "Кущение",
                    "Выход в трубку",
                    "Колошение",
                    "Цветение",
                    "Налив зерна",
                    "Молочная спелость",
                    "Восковая спелость",
                    "Полная спелость"
                ],
                help="Фаза развития культуры"
            )

            # Погодные условия
            weather_conditions = st.text_input(
                "Погодные условия",
                placeholder="Ясно, +22°C, влажность 60%",
                help="Погодные условия в момент обследования"
            )

        # В зависимости от типа проблемы показываем разные поля
        st.markdown("---")
        st.markdown(f"### 🔍 Детали проблемы: {problem_type}")

        col3, col4 = st.columns(2)

        with col3:
            if problem_type == "Болезнь":
                # Выбор болезни из справочника
                all_diseases = []
                for crop_diseases in diseases_ref.values():
                    all_diseases.extend(list(crop_diseases.keys()))

                disease_name = st.selectbox(
                    "Название болезни *",
                    options=sorted(set(all_diseases)),
                    help="Выберите болезнь из справочника"
                )
                problem_name = disease_name

            elif problem_type == "Вредитель":
                # Выбор вредителя из справочника
                all_pests = list(pests_ref.keys())

                pest_name = st.selectbox(
                    "Название вредителя *",
                    options=sorted(all_pests),
                    help="Выберите вредителя из справочника"
                )
                problem_name = pest_name

            else:  # Сорняк
                # Выбор сорняка из справочника
                all_weeds = []
                for weed_category in weeds_ref.values():
                    all_weeds.extend(list(weed_category.keys()))

                weed_name = st.selectbox(
                    "Название сорняка *",
                    options=sorted(set(all_weeds)),
                    help="Выберите сорняк из справочника"
                )
                problem_name = weed_name

            # Степень поражения
            severity = st.selectbox(
                "Степень поражения/засоренности *",
                options=["Слабая", "Средняя", "Сильная", "Очень сильная"],
                help="Оцените степень поражения"
            )

        with col4:
            # Распространение
            affected_area_percent = st.slider(
                "Распространение (% площади) *",
                min_value=0,
                max_value=100,
                value=10,
                step=5,
                help="Процент площади поля с проблемой"
            )

            # Интенсивность
            intensity = st.number_input(
                "Интенсивность (балл 1-5)",
                min_value=1,
                max_value=5,
                value=2,
                help="1 - единичные экземпляры, 5 - массовое поражение"
            )

            # Требуется обработка
            treatment_required = st.checkbox(
                "Требуется обработка",
                value=False,
                help="Превышен порог вредоносности"
            )

        # Координаты точки обнаружения
        st.markdown("---")
        st.markdown("### 📍 Точка обнаружения")

        col5, col6 = st.columns(2)

        with col5:
            gps_lat = st.number_input(
                "Широта (GPS)",
                min_value=-90.0,
                max_value=90.0,
                value=51.1694 if selected_field.center_lat is None else selected_field.center_lat,
                step=0.000001,
                format="%.6f",
                help="GPS координаты точки обнаружения"
            )

        with col6:
            gps_lon = st.number_input(
                "Долгота (GPS)",
                min_value=-180.0,
                max_value=180.0,
                value=71.4491 if selected_field.center_lon is None else selected_field.center_lon,
                step=0.000001,
                format="%.6f",
                help="GPS координаты точки обнаружения"
            )

        # Фото
        st.markdown("---")
        st.markdown("### 📷 Фотодокументация")

        photo_url = st.text_input(
            "URL фотографии",
            placeholder="https://example.com/photo.jpg или путь к файлу",
            help="Ссылка на фото или путь к файлу"
        )

        # Примечание и прогноз
        col7, col8 = st.columns(2)

        with col7:
            notes = st.text_area(
                "Примечание",
                height=100,
                help="Дополнительная информация"
            )

        with col8:
            forecast = st.text_area(
                "Прогноз развития",
                height=100,
                placeholder="При сохранении погодных условий ожидается...",
                help="Прогноз развития ситуации"
            )

        # Кнопка отправки
        submitted = st.form_submit_button("✅ Зарегистрировать обследование", use_container_width=True)

        if submitted:
            # Валидация
            errors = []

            # Проверка даты
            is_valid, msg = validator.validate_date(monitoring_date)
            if not is_valid:
                errors.append(f"Дата: {msg}")

            # Проверка культуры
            if not crop or len(crop) < 2:
                errors.append("Культура обязательна")

            # Проверка координат
            if gps_lat and gps_lon:
                is_valid, msg = validator.validate_coordinates(gps_lat, gps_lon)
                if not is_valid:
                    errors.append(f"Координаты: {msg}")

            if errors:
                st.error("❌ Ошибки валидации:\n" + "\n".join(f"- {e}" for e in errors))
            else:
                try:
                    # Создаем запись мониторинга
                    monitoring = PhytosanitaryMonitoring(
                        field_id=selected_field.id,
                        inspection_date=monitoring_date,
                        pest_type=problem_type,
                        pest_name=problem_name,
                        severity_pct=affected_area_percent,
                        prevalence_pct=affected_area_percent,
                        intensity_score=intensity,
                        threshold_exceeded=treatment_required,
                        crop_stage=growth_stage,
                        photo_url=photo_url if photo_url else None,
                        gps_lat=gps_lat if gps_lat else None,
                        gps_lon=gps_lon if gps_lon else None,
                        forecast=forecast if forecast else None,
                        notes=notes if notes else None
                    )
                    db.add(monitoring)
                    db.commit()

                    st.success(f"✅ Обследование зарегистрировано! {problem_type}: {problem_name}")
                    if treatment_required:
                        st.warning("⚠️ Требуется обработка! Перейдите на страницу 'Pesticides' для регистрации.")
                    st.balloons()

                except Exception as e:
                    db.rollback()
                    st.error(f"❌ Ошибка при сохранении: {str(e)}")

# ========================================
# TAB 2: История мониторинга
# ========================================
with tab2:
    st.subheader("История фитосанитарного мониторинга")

    # Фильтры
    col1, col2, col3 = st.columns(3)

    with col1:
        filter_field = st.selectbox(
            "Фильтр по полю",
            options=["Все поля"] + [f"{f.field_code} - {f.name}" for f in fields],
            key="filter_field_history"
        )

    with col2:
        filter_type = st.selectbox(
            "Тип проблемы",
            options=["Все типы", "Болезнь", "Вредитель", "Сорняк"],
            key="filter_type_history"
        )

    with col3:
        filter_year = st.selectbox(
            "Фильтр по году",
            options=["Все годы"] + list(range(datetime.now().year, datetime.now().year - 5, -1)),
            key="filter_year_history"
        )

    # Получение данных
    query = db.query(PhytosanitaryMonitoring, Field).join(
        Field, PhytosanitaryMonitoring.field_id == Field.id
    )

    # Применение фильтров
    if filter_field != "Все поля":
        field_code = filter_field.split(" - ")[0]
        query = query.filter(Field.field_code == field_code)

    if filter_type != "Все типы":
        query = query.filter(PhytosanitaryMonitoring.pest_type == filter_type)

    if filter_year != "Все годы":
        from sqlalchemy import extract
        query = query.filter(extract('year', PhytosanitaryMonitoring.inspection_date) == filter_year)

    monitorings = query.order_by(PhytosanitaryMonitoring.inspection_date.desc()).all()

    if monitorings:
        st.metric("Всего обследований", len(monitorings))

        # Таблица
        data = []
        for mon, field in monitorings:
            data.append({
                "Дата": format_date(mon.inspection_date),
                "Поле": f"{field.field_code} - {field.name}",
                "Фаза": mon.crop_stage or "-",
                "Тип": mon.pest_type,
                "Проблема": mon.pest_name,
                "Степень пораж. (%)": f"{mon.severity_pct or 0:.1f}",
                "Распространение (%)": f"{mon.prevalence_pct or 0:.1f}",
                "Превышен порог": "⚠️ Да" if mon.threshold_exceeded else "✅ Нет"
            })

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Экспорт
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            "📥 Скачать CSV",
            csv,
            "phytosanitary_history.csv",
            "text/csv"
        )

        # Статистика
        st.markdown("---")
        st.markdown("### 📊 Статистика")

        col1, col2, col3, col4 = st.columns(4)

        diseases_count = sum(1 for m, _ in monitorings if m.pest_type == "Болезнь")
        pests_count = sum(1 for m, _ in monitorings if m.pest_type == "Вредитель")
        weeds_count = sum(1 for m, _ in monitorings if m.pest_type == "Сорняк")
        treatment_needed = sum(1 for m, _ in monitorings if m.threshold_exceeded)

        with col1:
            st.metric("Болезни", diseases_count)
        with col2:
            st.metric("Вредители", pests_count)
        with col3:
            st.metric("Сорняки", weeds_count)
        with col4:
            st.metric("Требует обработки", treatment_needed, delta="⚠️" if treatment_needed > 0 else None)

        # Графики
        col1, col2 = st.columns(2)

        with col1:
            # Распределение по типам
            type_data = {
                "Болезни": diseases_count,
                "Вредители": pests_count,
                "Сорняки": weeds_count
            }
            fig_types = px.pie(
                values=list(type_data.values()),
                names=list(type_data.keys()),
                title="Распределение по типам проблем"
            )
            st.plotly_chart(fig_types, use_container_width=True)

        with col2:
            # Топ проблем
            problem_counts = {}
            for mon, _ in monitorings:
                problem_counts[mon.pest_name] = problem_counts.get(mon.pest_name, 0) + 1

            top_problems = sorted(problem_counts.items(), key=lambda x: x[1], reverse=True)[:10]

            if top_problems:
                fig_top = px.bar(
                    x=[p[1] for p in top_problems],
                    y=[p[0] for p in top_problems],
                    orientation='h',
                    title="Топ-10 проблем",
                    labels={"x": "Количество случаев", "y": "Проблема"}
                )
                st.plotly_chart(fig_top, use_container_width=True)

        # Карта проблем
        if any(m.gps_lat and m.gps_lon for m, _ in monitorings):
            st.markdown("---")
            st.markdown("### 🗺️ Карта обнаружений")

            map_data = []
            for mon, field in monitorings:
                if mon.gps_lat and mon.gps_lon:
                    map_data.append({
                        "lat": mon.gps_lat,
                        "lon": mon.gps_lon,
                        "Проблема": f"{mon.pest_type}: {mon.pest_name}",
                        "Поле": field.name
                    })

            if map_data:
                df_map = pd.DataFrame(map_data)
                st.map(df_map[['lat', 'lon']])

    else:
        st.info("📭 Пока нет записей фитосанитарного мониторинга")

# ========================================
# TAB 3: Справочники
# ========================================
with tab3:
    st.subheader("Справочники по фитосанитарии")

    ref_tab1, ref_tab2, ref_tab3 = st.tabs(["🦠 Болезни", "🐛 Вредители", "🌿 Сорняки"])

    with ref_tab1:
        st.markdown("### 🦠 Болезни сельскохозяйственных культур")

        if diseases_ref:
            for crop, crop_diseases in diseases_ref.items():
                with st.expander(f"**{crop}** ({len(crop_diseases)} болезней)"):
                    for disease_name, disease_info in crop_diseases.items():
                        st.markdown(f"**{disease_name}**")
                        if isinstance(disease_info, dict):
                            st.write(f"- Возбудитель: {disease_info.get('возбудитель', '-')}")
                            st.write(f"- Признаки: {disease_info.get('признаки', '-')}")
                            st.write(f"- Вредоносность: {disease_info.get('вредоносность', '-')}")

    with ref_tab2:
        st.markdown("### 🐛 Вредители")

        if pests_ref:
            for pest_name, pest_info in pests_ref.items():
                with st.expander(f"**{pest_name}**"):
                    if isinstance(pest_info, dict):
                        st.write(f"- Культура: {pest_info.get('культура', '-')}")
                        st.write(f"- Фазы вредоносности: {pest_info.get('фазы_вредоносности', '-')}")
                        st.write(f"- Порог вредоносности: {pest_info.get('порог_вредоносности', '-')}")
                        st.write(f"- Меры борьбы: {pest_info.get('меры_борьбы', '-')}")

    with ref_tab3:
        st.markdown("### 🌿 Сорняки")

        if weeds_ref:
            for category, category_weeds in weeds_ref.items():
                with st.expander(f"**{category}** ({len(category_weeds)} видов)"):
                    for weed_name, weed_info in category_weeds.items():
                        st.markdown(f"**{weed_name}**")
                        if isinstance(weed_info, dict):
                            st.write(f"- Биогруппа: {weed_info.get('биогруппа', '-')}")
                            st.write(f"- Вредоносность: {weed_info.get('вредоносность', '-')}")
                            st.write(f"- Меры борьбы: {weed_info.get('меры_борьбы', '-')}")

# ========================================
# TAB 4: Пороги вредоносности
# ========================================
with tab4:
    st.subheader("Пороги вредоносности")

    st.info("""
    **Порог вредоносности** - это плотность популяции вредного организма или степень поражения,
    при которой необходимо проведение защитных мероприятий для предотвращения экономических потерь.
    """)

    st.markdown("### 🦠 Болезни (пороги для химобработки)")

    disease_thresholds = pd.DataFrame({
        "Культура": ["Пшеница", "Пшеница", "Пшеница", "Ячмень", "Рапс"],
        "Болезнь": ["Бурая ржавчина", "Септориоз листьев", "Мучнистая роса", "Пятнистость листьев", "Альтернариоз"],
        "Фаза культуры": ["Кущение-колошение", "Флаг-листа", "Выход в трубку", "Кущение", "Цветение"],
        "Порог (% поражения)": ["5-10%", "25-30%", "10-15%", "15-20%", "10-15%"]
    })
    st.dataframe(disease_thresholds, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### 🐛 Вредители (пороги плотности)")

    pest_thresholds = pd.DataFrame({
        "Культура": ["Пшеница", "Пшеница", "Пшеница", "Рапс", "Подсолнечник"],
        "Вредитель": ["Хлебная жужелица", "Пьявица", "Клоп вредная черепашка", "Крестоцветные блошки", "Луговой мотылек"],
        "Фаза культуры": ["Всходы", "Кущение-колошение", "Налив зерна", "Всходы", "Бутонизация"],
        "Порог (шт/м²)": ["3-5 жук/м²", "0.5-1 лич/стебель", "5-10 клоп/м²", "10-15 жук/м²", "10-15 гус/м²"]
    })
    st.dataframe(pest_thresholds, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### 🌿 Сорняки (пороги засоренности)")

    weed_thresholds = pd.DataFrame({
        "Тип сорняка": ["Малолетние яровые", "Многолетние корнеотпрысковые", "Многолетние корневищные", "Паразитные"],
        "Порог (шт/м²)": ["15-20 шт/м²", "1-3 шт/м²", "5-10 побегов/м²", "1-2 шт/м²"],
        "Примеры": ["Овсюг, щирица, марь", "Осот, вьюнок полевой", "Пырей ползучий", "Заразиха"],
        "Критический период": ["Фаза кущения", "До выхода в трубку", "От всходов до кущения", "Всходы-цветение"]
    })
    st.dataframe(weed_thresholds, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.warning("""
    **⚠️ Важно:**
    - Пороги могут варьироваться в зависимости от региона и погодных условий
    - При высокой влажности пороги для болезней снижаются
    - Экономический порог зависит от стоимости урожая и затрат на обработку
    - Рекомендуется проводить мониторинг каждые 5-7 дней в критические периоды
    """)

# Футер
st.markdown("---")
st.markdown("🐛 **Фитосанитарный мониторинг** | Версия 1.0")
