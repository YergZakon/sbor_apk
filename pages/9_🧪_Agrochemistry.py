"""
Agrochemistry - Агрохимические анализы почвы
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

# Добавляем путь к модулям
import sys
sys.path.append(str(Path(__file__).parent.parent))

from modules.database import get_db, Farm, Field, Operation, AgrochemicalAnalysis
from modules.validators import DataValidator
from modules.config import Settings
from utils.formatters import format_date, format_area, format_number
from utils.charts import create_heatmap, create_grouped_bar_chart

# Настройка страницы
st.set_page_config(page_title="Агрохимия", page_icon="🧪", layout="wide")

st.title("🧪 Агрохимические анализы почвы")

# Инициализация
validator = DataValidator()
settings = Settings()

# Подключение к БД
db = next(get_db())

# Проверка наличия хозяйства
farm = db.query(Farm).first()
if not farm:
    st.warning("⚠️ Сначала создайте хозяйство на странице импорта!")
    st.stop()

# Получение списка полей
fields = db.query(Field).filter(Field.farm_id == farm.id).all()
if not fields:
    st.warning("⚠️ Сначала добавьте поля на странице 'Поля'!")
    st.stop()

# Табы
tab1, tab2, tab3, tab4 = st.tabs(["📝 Регистрация анализа", "📊 История анализов", "🗺️ Карта плодородия", "📚 Нормативы"])

# ========================================
# TAB 1: Регистрация анализа
# ========================================
with tab1:
    st.subheader("Регистрация агрохимического анализа")

    with st.form("agrochemical_form"):
        col1, col2 = st.columns(2)

        with col1:
            # Выбор поля
            field_options = {f"{f.field_code} - {f.name}": f for f in fields}
            selected_field_name = st.selectbox(
                "Поле *",
                options=list(field_options.keys()),
                help="Выберите поле для анализа"
            )
            selected_field = field_options[selected_field_name]

            # Дата анализа
            analysis_date = st.date_input(
                "Дата отбора проб *",
                value=date.today(),
                help="Дата отбора почвенных проб"
            )

            # Глубина отбора
            sample_depth = st.number_input(
                "Глубина отбора (см) *",
                min_value=0,
                max_value=100,
                value=20,
                step=5,
                help="Глубина отбора почвенного образца"
            )

            # pH
            st.markdown("#### Кислотность почвы")

            ph_water = st.number_input(
                "pH водный",
                min_value=3.0,
                max_value=10.0,
                value=7.0,
                step=0.1,
                help="pH водной вытяжки"
            )

            ph_salt = st.number_input(
                "pH солевой",
                min_value=3.0,
                max_value=10.0,
                value=6.5,
                step=0.1,
                help="pH солевой вытяжки (KCl)"
            )

        with col2:
            # Гумус
            st.markdown("#### Органическое вещество")

            humus_percent = st.number_input(
                "Гумус (%)",
                min_value=0.0,
                max_value=15.0,
                value=3.0,
                step=0.1,
                help="Содержание гумуса в почве"
            )

            # Азот
            st.markdown("#### Элементы питания")

            nitrogen_total = st.number_input(
                "Азот общий (%)",
                min_value=0.0,
                max_value=1.0,
                value=0.15,
                step=0.01,
                help="Общий азот в почве"
            )

            # Фосфор
            p2o5_mg_kg = st.number_input(
                "P₂O₅ (мг/кг)",
                min_value=0.0,
                max_value=500.0,
                value=50.0,
                step=5.0,
                help="Подвижный фосфор"
            )

            # Калий
            k2o_mg_kg = st.number_input(
                "K₂O (мг/кг)",
                min_value=0.0,
                max_value=1000.0,
                value=200.0,
                step=10.0,
                help="Обменный калий"
            )

        # Дополнительные элементы
        st.markdown("---")
        st.markdown("### 🔬 Дополнительные элементы")

        col3, col4, col5, col6 = st.columns(4)

        with col3:
            mobile_s = st.number_input(
                "Сера подвижная (мг/кг)",
                min_value=0.0,
                max_value=100.0,
                value=10.0,
                step=1.0
            )

        with col4:
            ca_mg_kg = st.number_input(
                "Кальций (мг/кг)",
                min_value=0.0,
                max_value=5000.0,
                value=1500.0,
                step=50.0
            )

        with col5:
            mg_mg_kg = st.number_input(
                "Магний (мг/кг)",
                min_value=0.0,
                max_value=500.0,
                value=100.0,
                step=10.0
            )

        with col6:
            na_mg_kg = st.number_input(
                "Натрий (мг/кг)",
                min_value=0.0,
                max_value=500.0,
                value=50.0,
                step=5.0
            )

        # Оценка и рекомендации
        st.markdown("---")
        st.markdown("### 📊 Автоматическая оценка параметров")

        col7, col8, col9 = st.columns(3)

        with col7:
            # Оценка pH
            if ph_water < 5.5:
                ph_assessment = "🔴 Кислая (требуется известкование)"
            elif ph_water < 6.5:
                ph_assessment = "🟡 Слабокислая"
            elif ph_water <= 7.5:
                ph_assessment = "🟢 Нейтральная (оптимально)"
            else:
                ph_assessment = "🟡 Слабощелочная"

            st.metric("Оценка pH", ph_assessment)

        with col8:
            # Оценка гумуса
            if humus_percent < 2.0:
                humus_assessment = "🔴 Очень низкое"
            elif humus_percent < 3.0:
                humus_assessment = "🟡 Низкое"
            elif humus_percent <= 5.0:
                humus_assessment = "🟢 Среднее"
            else:
                humus_assessment = "🟢 Высокое"

            st.metric("Содержание гумуса", humus_assessment)

        with col9:
            # Оценка обеспеченности фосфором
            if p2o5_mg_kg < 20:
                p_assessment = "🔴 Очень низкая"
            elif p2o5_mg_kg < 40:
                p_assessment = "🟡 Низкая"
            elif p2o5_mg_kg <= 80:
                p_assessment = "🟢 Средняя"
            else:
                p_assessment = "🟢 Повышенная"

            st.metric("Обеспеченность P₂O₅", p_assessment)

        # Примечание
        notes = st.text_area(
            "Примечание",
            height=80,
            help="Дополнительная информация об анализе"
        )

        # Кнопка отправки
        submitted = st.form_submit_button("✅ Сохранить анализ", use_container_width=True)

        if submitted:
            # Валидация
            errors = []

            # Проверка даты
            is_valid, msg = validator.validate_date(analysis_date)
            if not is_valid:
                errors.append(f"Дата: {msg}")

            # Проверка pH
            is_valid, msg = validator.validate_ph(ph_water)
            if not is_valid:
                errors.append(f"pH водный: {msg}")

            # Проверка гумуса
            is_valid, msg = validator.validate_percentage(humus_percent)
            if not is_valid:
                errors.append(f"Гумус: {msg}")

            if errors:
                st.error("❌ Ошибки валидации:\n" + "\n".join(f"- {e}" for e in errors))
            else:
                try:
                    # Создаем операцию
                    operation = Operation(
                        farm_id=farm.id,
                        field_id=selected_field.id,
                        operation_type="soil_analysis",
                        operation_date=analysis_date,
                        area_processed_ha=selected_field.area_ha,
                        notes=notes
                    )
                    db.add(operation)
                    db.flush()

                    # Создаем анализ
                    analysis = AgrochemicalAnalysis(
                        operation_id=operation.id,
                        sample_depth_cm=sample_depth,
                        ph_water=ph_water,
                        ph_salt=ph_salt,
                        humus_percent=humus_percent,
                        nitrogen_total_percent=nitrogen_total,
                        p2o5_mg_kg=p2o5_mg_kg,
                        k2o_mg_kg=k2o_mg_kg,
                        mobile_s_mg_kg=mobile_s if mobile_s > 0 else None,
                        ca_mg_kg=ca_mg_kg if ca_mg_kg > 0 else None,
                        mg_mg_kg=mg_mg_kg if mg_mg_kg > 0 else None,
                        na_mg_kg=na_mg_kg if na_mg_kg > 0 else None
                    )
                    db.add(analysis)

                    # Обновляем данные поля
                    selected_field.ph_water = ph_water
                    selected_field.humus_pct = humus_percent
                    selected_field.p2o5_mg_kg = p2o5_mg_kg
                    selected_field.k2o_mg_kg = k2o_mg_kg

                    db.commit()

                    st.success("✅ Анализ сохранен! Данные поля обновлены.")
                    st.balloons()

                except Exception as e:
                    db.rollback()
                    st.error(f"❌ Ошибка при сохранении: {str(e)}")

# ========================================
# TAB 2: История анализов
# ========================================
with tab2:
    st.subheader("История агрохимических анализов")

    # Фильтры
    col1, col2 = st.columns(2)

    with col1:
        filter_field = st.selectbox(
            "Фильтр по полю",
            options=["Все поля"] + [f"{f.field_code} - {f.name}" for f in fields],
            key="filter_field_history"
        )

    with col2:
        filter_year = st.selectbox(
            "Фильтр по году",
            options=["Все годы"] + list(range(datetime.now().year, datetime.now().year - 10, -1)),
            key="filter_year_history"
        )

    # Получение данных
    query = db.query(Operation, AgrochemicalAnalysis, Field).join(
        AgrochemicalAnalysis, Operation.id == AgrochemicalAnalysis.operation_id
    ).join(
        Field, Operation.field_id == Field.id
    ).filter(
        Operation.operation_type == "soil_analysis"
    )

    # Применение фильтров
    if filter_field != "Все поля":
        field_code = filter_field.split(" - ")[0]
        query = query.filter(Field.field_code == field_code)

    if filter_year != "Все годы":
        from sqlalchemy import extract
        query = query.filter(extract('year', Operation.operation_date) == filter_year)

    analyses = query.order_by(Operation.operation_date.desc()).all()

    if analyses:
        st.metric("Всего анализов", len(analyses))

        # Таблица
        data = []
        for op, analysis, field in analyses:
            data.append({
                "Дата": format_date(op.operation_date),
                "Поле": f"{field.field_code} - {field.name}",
                "pH водн": format_number(analysis.ph_water, 1),
                "Гумус (%)": format_number(analysis.humus_percent, 2),
                "P₂O₅ (мг/кг)": format_number(analysis.p2o5_mg_kg, 1),
                "K₂O (мг/кг)": format_number(analysis.k2o_mg_kg, 1),
                "Глубина (см)": analysis.sample_depth_cm
            })

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Экспорт
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            "📥 Скачать CSV",
            csv,
            "agrochemistry_history.csv",
            "text/csv"
        )

        # Статистика
        st.markdown("---")
        st.markdown("### 📊 Средние показатели")

        col1, col2, col3, col4 = st.columns(4)

        avg_ph = sum(a.ph_water for _, a, _ in analyses) / len(analyses)
        avg_humus = sum(a.humus_percent for _, a, _ in analyses) / len(analyses)
        avg_p = sum(a.p2o5_mg_kg for _, a, _ in analyses) / len(analyses)
        avg_k = sum(a.k2o_mg_kg for _, a, _ in analyses) / len(analyses)

        with col1:
            st.metric("pH водный", f"{avg_ph:.1f}")
        with col2:
            st.metric("Гумус", f"{avg_humus:.2f}%")
        with col3:
            st.metric("P₂O₅", f"{avg_p:.1f} мг/кг")
        with col4:
            st.metric("K₂O", f"{avg_k:.1f} мг/кг")

        # Графики
        st.markdown("---")
        st.markdown("### 📈 Динамика показателей")

        # Группировка по полям
        field_data = {}
        for op, analysis, field in analyses:
            field_name = f"{field.field_code}"
            if field_name not in field_data:
                field_data[field_name] = {
                    "pH": [],
                    "Гумус": [],
                    "P₂O₅": [],
                    "K₂O": []
                }
            field_data[field_name]["pH"].append(analysis.ph_water)
            field_data[field_name]["Гумус"].append(analysis.humus_percent)
            field_data[field_name]["P₂O₅"].append(analysis.p2o5_mg_kg)
            field_data[field_name]["K₂O"].append(analysis.k2o_mg_kg)

        # Средние по полям
        field_averages = {}
        for field_name, data in field_data.items():
            field_averages[field_name] = {
                "pH": sum(data["pH"]) / len(data["pH"]),
                "Гумус": sum(data["Гумус"]) / len(data["Гумус"]),
                "P₂O₅": sum(data["P₂O₅"]) / len(data["P₂O₅"]),
                "K₂O": sum(data["K₂O"]) / len(data["K₂O"])
            }

        col1, col2 = st.columns(2)

        with col1:
            # График pH по полям
            fig_ph = px.bar(
                x=list(field_averages.keys()),
                y=[field_averages[f]["pH"] for f in field_averages.keys()],
                title="pH по полям",
                labels={"x": "Поля", "y": "pH водный"},
                color=[field_averages[f]["pH"] for f in field_averages.keys()],
                color_continuous_scale="RdYlGn"
            )
            st.plotly_chart(fig_ph, use_container_width=True)

        with col2:
            # График гумуса по полям
            fig_humus = px.bar(
                x=list(field_averages.keys()),
                y=[field_averages[f]["Гумус"] for f in field_averages.keys()],
                title="Содержание гумуса по полям (%)",
                labels={"x": "Поля", "y": "Гумус (%)"},
                color=[field_averages[f]["Гумус"] for f in field_averages.keys()],
                color_continuous_scale="Greens"
            )
            st.plotly_chart(fig_humus, use_container_width=True)

        # График NPK
        fields_list = list(field_averages.keys())
        p_values = [field_averages[f]["P₂O₅"] for f in fields_list]
        k_values = [field_averages[f]["K₂O"] for f in fields_list]

        fig_npk = go.Figure(data=[
            go.Bar(name='P₂O₅', x=fields_list, y=p_values, marker_color='orange'),
            go.Bar(name='K₂O', x=fields_list, y=k_values, marker_color='green')
        ])
        fig_npk.update_layout(
            title="Обеспеченность P₂O₅ и K₂O по полям (мг/кг)",
            xaxis_title="Поля",
            yaxis_title="Содержание (мг/кг)",
            barmode='group'
        )
        st.plotly_chart(fig_npk, use_container_width=True)

    else:
        st.info("📭 Пока нет агрохимических анализов")

# ========================================
# TAB 3: Карта плодородия
# ========================================
with tab3:
    st.subheader("Карта плодородия полей")

    # Получение последних анализов по полям
    latest_analyses = {}
    for field in fields:
        last_analysis = db.query(Operation, AgrochemicalAnalysis).join(
            AgrochemicalAnalysis, Operation.id == AgrochemicalAnalysis.operation_id
        ).filter(
            Operation.field_id == field.id,
            Operation.operation_type == "soil_analysis"
        ).order_by(Operation.operation_date.desc()).first()

        if last_analysis:
            latest_analyses[field.field_code] = {
                "field": field,
                "analysis": last_analysis[1],
                "date": last_analysis[0].operation_date
            }

    if latest_analyses:
        # Таблица с картой
        st.markdown("### 🗺️ Текущее состояние полей")

        map_data = []
        for field_code, data in latest_analyses.items():
            field = data["field"]
            analysis = data["analysis"]

            # Определение балла плодородия (упрощенный)
            fertility_score = 0

            # pH (оптимум 6.5-7.5)
            if 6.5 <= analysis.ph_water <= 7.5:
                fertility_score += 25
            elif 6.0 <= analysis.ph_water <= 8.0:
                fertility_score += 15
            else:
                fertility_score += 5

            # Гумус (оптимум >3%)
            if analysis.humus_percent >= 4.0:
                fertility_score += 30
            elif analysis.humus_percent >= 3.0:
                fertility_score += 20
            elif analysis.humus_percent >= 2.0:
                fertility_score += 10
            else:
                fertility_score += 5

            # P₂O₅ (оптимум >40)
            if analysis.p2o5_mg_kg >= 80:
                fertility_score += 25
            elif analysis.p2o5_mg_kg >= 40:
                fertility_score += 15
            elif analysis.p2o5_mg_kg >= 20:
                fertility_score += 10
            else:
                fertility_score += 5

            # K₂O (оптимум >200)
            if analysis.k2o_mg_kg >= 300:
                fertility_score += 20
            elif analysis.k2o_mg_kg >= 200:
                fertility_score += 15
            elif analysis.k2o_mg_kg >= 100:
                fertility_score += 10
            else:
                fertility_score += 5

            map_data.append({
                "Поле": f"{field.field_code} - {field.name}",
                "pH": format_number(analysis.ph_water, 1),
                "Гумус (%)": format_number(analysis.humus_percent, 2),
                "P₂O₅": format_number(analysis.p2o5_mg_kg, 0),
                "K₂O": format_number(analysis.k2o_mg_kg, 0),
                "Балл плодородия": fertility_score,
                "Дата анализа": format_date(data["date"])
            })

        df_map = pd.DataFrame(map_data)
        st.dataframe(df_map, use_container_width=True, hide_index=True)

        # График плодородия
        fig_fertility = px.bar(
            df_map,
            x="Поле",
            y="Балл плодородия",
            title="Балл плодородия по полям (0-100)",
            color="Балл плодородия",
            color_continuous_scale="RdYlGn",
            range_color=[0, 100]
        )
        st.plotly_chart(fig_fertility, use_container_width=True)

    else:
        st.info("📭 Нет данных агрохимических анализов для построения карты")

# ========================================
# TAB 4: Нормативы
# ========================================
with tab4:
    st.subheader("Нормативы и рекомендации")

    st.markdown("### 📋 Градации агрохимических показателей")

    # pH
    st.markdown("#### 1. Кислотность почвы (pH)")
    ph_norms = pd.DataFrame({
        "pH водный": ["< 4.5", "4.5 - 5.5", "5.5 - 6.5", "6.5 - 7.5", "7.5 - 8.5", "> 8.5"],
        "Градация": [
            "Сильнокислая",
            "Среднекислая",
            "Слабокислая",
            "Нейтральная (оптимум)",
            "Слабощелочная",
            "Щелочная"
        ],
        "Рекомендации": [
            "Обязательное известкование",
            "Известкование рекомендуется",
            "Известкование при необходимости",
            "Корректировка не требуется",
            "Возможно подкисление",
            "Подкисление обязательно"
        ]
    })
    st.dataframe(ph_norms, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Гумус
    st.markdown("#### 2. Содержание гумуса")
    humus_norms = pd.DataFrame({
        "Содержание (%)": ["< 2.0", "2.0 - 3.0", "3.0 - 5.0", "5.0 - 7.0", "> 7.0"],
        "Градация": ["Очень низкое", "Низкое", "Среднее", "Повышенное", "Высокое"],
        "Рекомендации": [
            "Внесение органики обязательно",
            "Регулярное внесение органики",
            "Поддержание уровня",
            "Оптимальный уровень",
            "Оптимальный уровень"
        ]
    })
    st.dataframe(humus_norms, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Фосфор
    st.markdown("#### 3. Подвижный фосфор (P₂O₅)")
    p_norms = pd.DataFrame({
        "Содержание (мг/кг)": ["< 20", "20 - 40", "40 - 80", "80 - 150", "> 150"],
        "Градация": ["Очень низкая", "Низкая", "Средняя", "Повышенная", "Высокая"],
        "Доза P₂O₅ (кг/га)": ["60-90", "45-60", "30-45", "15-30", "0-15"]
    })
    st.dataframe(p_norms, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Калий
    st.markdown("#### 4. Обменный калий (K₂O)")
    k_norms = pd.DataFrame({
        "Содержание (мг/кг)": ["< 100", "100 - 200", "200 - 300", "300 - 500", "> 500"],
        "Градация": ["Очень низкая", "Низкая", "Средняя", "Повышенная", "Высокая"],
        "Доза K₂O (кг/га)": ["60-90", "45-60", "30-45", "15-30", "0-15"]
    })
    st.dataframe(k_norms, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Рекомендации
    st.markdown("### 💡 Общие рекомендации")

    st.info("""
    **Частота агрохимического обследования:**
    - Основное обследование: 1 раз в 5 лет
    - Контрольное обследование: 1 раз в 2-3 года
    - Отбор проб: осенью после уборки или ранней весной до внесения удобрений

    **Глубина отбора проб:**
    - Пахотный слой: 0-20 см (основная)
    - Подпахотный слой: 20-40 см (дополнительно)

    **Количество проб:**
    - На 1 га: 1 объединенная проба (из 15-20 точечных)
    - Равномерное размещение по полю

    **Корректировка питания:**
    - Известкование: при pH < 5.5
    - Органика: ежегодно или в севообороте
    - Фосфорные удобрения: основное внесение осенью
    - Калийные удобрения: основное внесение осенью
    """)

# Футер
st.markdown("---")
st.markdown("🧪 **Агрохимические анализы** | Версия 1.0")
