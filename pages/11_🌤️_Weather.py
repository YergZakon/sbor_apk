"""
Weather - Метеорологические данные
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

# Добавляем путь к модулям
import sys
sys.path.append(str(Path(__file__).parent.parent))

from modules.database import get_db, Farm, Field, WeatherData
from modules.validators import DataValidator
from utils.formatters import format_date, format_number

# Настройка страницы
st.set_page_config(page_title="Метеоданные", page_icon="🌤️", layout="wide")

st.title("🌤️ Метеорологические данные")

# Инициализация валидатора
validator = DataValidator()

# Подключение к БД
db = next(get_db())

# Проверка наличия хозяйства
farm = db.query(Farm).first()
if not farm:
    st.warning("⚠️ Сначала создайте хозяйство на странице Farm Setup!")
    st.stop()

# Получение списка полей
fields = db.query(Field).filter(Field.farm_id == farm.id).all()

# Табы
tab1, tab2, tab3, tab4 = st.tabs(["📝 Регистрация данных", "📊 История погоды", "📈 Анализ", "🌡️ Агроклиматические показатели"])

# ========================================
# TAB 1: Регистрация данных
# ========================================
with tab1:
    st.subheader("Регистрация метеорологических данных")

    with st.form("weather_form"):
        col1, col2 = st.columns(2)

        with col1:
            # Дата наблюдения
            observation_date = st.date_input(
                "Дата наблюдения *",
                value=date.today(),
                help="Дата метеорологических наблюдений"
            )

            # Температура
            st.markdown("#### 🌡️ Температура")

            temp_max = st.number_input(
                "Максимальная температура (°C) *",
                min_value=-50.0,
                max_value=50.0,
                value=20.0,
                step=0.5,
                help="Максимальная температура воздуха за сутки"
            )

            temp_min = st.number_input(
                "Минимальная температура (°C) *",
                min_value=-50.0,
                max_value=50.0,
                value=10.0,
                step=0.5,
                help="Минимальная температура воздуха за сутки"
            )

            temp_avg = (temp_max + temp_min) / 2
            st.metric("Средняя температура", f"{temp_avg:.1f}°C")

            # Почвенная температура
            soil_temp = st.number_input(
                "Температура почвы на 10 см (°C)",
                min_value=-20.0,
                max_value=50.0,
                value=15.0,
                step=0.5,
                help="Температура почвы на глубине 10 см"
            )

        with col2:
            # Осадки
            st.markdown("#### 🌧️ Осадки")

            precipitation = st.number_input(
                "Количество осадков (мм) *",
                min_value=0.0,
                max_value=200.0,
                value=0.0,
                step=0.1,
                help="Сумма осадков за сутки"
            )

            # Влажность
            humidity = st.number_input(
                "Относительная влажность воздуха (%)",
                min_value=0,
                max_value=100,
                value=60,
                step=5,
                help="Средняя относительная влажность"
            )

            # Ветер
            st.markdown("#### 💨 Ветер")

            wind_speed = st.number_input(
                "Скорость ветра (м/с)",
                min_value=0.0,
                max_value=50.0,
                value=3.0,
                step=0.5,
                help="Средняя скорость ветра"
            )

            wind_direction = st.selectbox(
                "Направление ветра",
                options=["С", "СВ", "В", "ЮВ", "Ю", "ЮЗ", "З", "СЗ", "Штиль"],
                help="Преобладающее направление ветра"
            )

        # Дополнительные параметры
        st.markdown("---")
        st.markdown("### ☁️ Дополнительные параметры")

        col3, col4, col5 = st.columns(3)

        with col3:
            cloudiness = st.slider(
                "Облачность (баллы 0-10)",
                min_value=0,
                max_value=10,
                value=5,
                help="0 - ясно, 10 - сплошная облачность"
            )

        with col4:
            sunshine_hours = st.number_input(
                "Солнечное сияние (часы)",
                min_value=0.0,
                max_value=24.0,
                value=8.0,
                step=0.5,
                help="Продолжительность солнечного сияния"
            )

        with col5:
            pressure = st.number_input(
                "Атмосферное давление (гПа)",
                min_value=900,
                max_value=1100,
                value=1013,
                step=1,
                help="Атмосферное давление"
            )

        # Явления погоды
        st.markdown("---")
        weather_phenomena = st.multiselect(
            "Явления погоды",
            options=[
                "Дождь",
                "Ливень",
                "Гроза",
                "Град",
                "Снег",
                "Туман",
                "Роса",
                "Иней",
                "Заморозок",
                "Суховей"
            ],
            help="Выберите наблюдавшиеся явления"
        )

        # Примечание
        notes = st.text_area(
            "Примечание",
            height=80,
            help="Дополнительная информация"
        )

        # Кнопка отправки
        submitted = st.form_submit_button("✅ Сохранить данные", use_container_width=True)

        if submitted:
            # Валидация
            errors = []

            # Проверка даты
            is_valid, msg = validator.validate_date(observation_date)
            if not is_valid:
                errors.append(f"Дата: {msg}")

            # Проверка температуры
            if temp_min > temp_max:
                errors.append("Минимальная температура не может быть выше максимальной")

            if errors:
                st.error("❌ Ошибки валидации:\n" + "\n".join(f"- {e}" for e in errors))
            else:
                try:
                    # Создаем запись погоды
                    weather = WeatherData(
                        farm_id=farm.id,
                        observation_date=observation_date,
                        temp_max_c=temp_max,
                        temp_min_c=temp_min,
                        temp_avg_c=temp_avg,
                        soil_temp_c=soil_temp if soil_temp else None,
                        precipitation_mm=precipitation,
                        humidity_percent=humidity if humidity else None,
                        wind_speed_ms=wind_speed if wind_speed else None,
                        wind_direction=wind_direction if wind_direction != "Штиль" else None,
                        cloudiness_score=cloudiness if cloudiness else None,
                        sunshine_hours=sunshine_hours if sunshine_hours else None,
                        pressure_hpa=pressure if pressure else None,
                        weather_phenomena=", ".join(weather_phenomena) if weather_phenomena else None,
                        notes=notes if notes else None
                    )
                    db.add(weather)
                    db.commit()

                    st.success(f"✅ Метеоданные сохранены на {format_date(observation_date)}")
                    st.balloons()

                except Exception as e:
                    db.rollback()
                    st.error(f"❌ Ошибка при сохранении: {str(e)}")

# ========================================
# TAB 2: История погоды
# ========================================
with tab2:
    st.subheader("История метеорологических данных")

    # Фильтры
    col1, col2 = st.columns(2)

    with col1:
        filter_year = st.selectbox(
            "Год",
            options=["Все годы"] + list(range(datetime.now().year, datetime.now().year - 10, -1)),
            key="filter_year_history"
        )

    with col2:
        filter_month = st.selectbox(
            "Месяц",
            options=["Все месяцы", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"],
            key="filter_month_history"
        )

    # Получение данных
    query = db.query(WeatherData).filter(WeatherData.farm_id == farm.id)

    # Применение фильтров
    if filter_year != "Все годы":
        from sqlalchemy import extract
        query = query.filter(extract('year', WeatherData.observation_date) == filter_year)

    if filter_month != "Все месяцы":
        months = {
            "Январь": 1, "Февраль": 2, "Март": 3, "Апрель": 4,
            "Май": 5, "Июнь": 6, "Июль": 7, "Август": 8,
            "Сентябрь": 9, "Октябрь": 10, "Ноябрь": 11, "Декабрь": 12
        }
        from sqlalchemy import extract
        query = query.filter(extract('month', WeatherData.observation_date) == months[filter_month])

    weather_records = query.order_by(WeatherData.observation_date.desc()).all()

    if weather_records:
        st.metric("Всего записей", len(weather_records))

        # Таблица
        data = []
        for w in weather_records:
            data.append({
                "Дата": format_date(w.observation_date),
                "T макс (°C)": format_number(w.temp_max_c, 1),
                "T мин (°C)": format_number(w.temp_min_c, 1),
                "T средн (°C)": format_number(w.temp_avg_c, 1),
                "Осадки (мм)": format_number(w.precipitation_mm, 1),
                "Влажность (%)": w.humidity_percent or "-",
                "Ветер (м/с)": format_number(w.wind_speed_ms, 1) if w.wind_speed_ms else "-",
                "Явления": w.weather_phenomena or "-"
            })

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Экспорт
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            "📥 Скачать CSV",
            csv,
            "weather_history.csv",
            "text/csv"
        )

        # Статистика
        st.markdown("---")
        st.markdown("### 📊 Статистика за период")

        col1, col2, col3, col4 = st.columns(4)

        avg_temp = sum(w.temp_avg_c for w in weather_records) / len(weather_records)
        total_precip = sum(w.precipitation_mm for w in weather_records)
        max_temp_record = max(w.temp_max_c for w in weather_records)
        min_temp_record = min(w.temp_min_c for w in weather_records)

        with col1:
            st.metric("Средняя температура", f"{avg_temp:.1f}°C")
        with col2:
            st.metric("Сумма осадков", f"{total_precip:.1f} мм")
        with col3:
            st.metric("Макс. температура", f"{max_temp_record:.1f}°C")
        with col4:
            st.metric("Мин. температура", f"{min_temp_record:.1f}°C")

    else:
        st.info("📭 Нет метеорологических данных за выбранный период")

# ========================================
# TAB 3: Анализ
# ========================================
with tab3:
    st.subheader("Анализ метеорологических данных")

    # Получение всех данных для анализа
    all_weather = db.query(WeatherData).filter(
        WeatherData.farm_id == farm.id
    ).order_by(WeatherData.observation_date).all()

    if len(all_weather) < 7:
        st.warning("⚠️ Недостаточно данных для анализа. Необходимо минимум 7 дней.")
    else:
        # График температуры
        st.markdown("### 🌡️ Динамика температуры")

        dates = [w.observation_date for w in all_weather]
        temp_max = [w.temp_max_c for w in all_weather]
        temp_min = [w.temp_min_c for w in all_weather]
        temp_avg = [w.temp_avg_c for w in all_weather]

        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(x=dates, y=temp_max, mode='lines', name='T макс', line=dict(color='red')))
        fig_temp.add_trace(go.Scatter(x=dates, y=temp_avg, mode='lines', name='T средн', line=dict(color='orange')))
        fig_temp.add_trace(go.Scatter(x=dates, y=temp_min, mode='lines', name='T мин', line=dict(color='blue')))

        fig_temp.update_layout(
            title="Температура воздуха",
            xaxis_title="Дата",
            yaxis_title="Температура (°C)",
            hovermode='x unified'
        )
        st.plotly_chart(fig_temp, use_container_width=True)

        # График осадков
        st.markdown("---")
        st.markdown("### 🌧️ Осадки")

        precip = [w.precipitation_mm for w in all_weather]

        fig_precip = go.Figure()
        fig_precip.add_trace(go.Bar(x=dates, y=precip, name='Осадки', marker_color='lightblue'))

        fig_precip.update_layout(
            title="Суточные осадки",
            xaxis_title="Дата",
            yaxis_title="Осадки (мм)",
            hovermode='x unified'
        )
        st.plotly_chart(fig_precip, use_container_width=True)

        # Сумма осадков за периоды
        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            # Последние 7 дней
            last_7_days = all_weather[-7:] if len(all_weather) >= 7 else all_weather
            precip_7d = sum(w.precipitation_mm for w in last_7_days)
            st.metric("Осадки за 7 дней", f"{precip_7d:.1f} мм")

        with col2:
            # Последние 30 дней
            last_30_days = all_weather[-30:] if len(all_weather) >= 30 else all_weather
            precip_30d = sum(w.precipitation_mm for w in last_30_days)
            st.metric("Осадки за 30 дней", f"{precip_30d:.1f} мм")

        # Сумма эффективных температур
        st.markdown("---")
        st.markdown("### ∑ Сумма эффективных температур (СЭТ)")

        st.info("""
        **Сумма эффективных температур** (СЭТ) - сумма среднесуточных температур выше биологического минимума (+5°C или +10°C).
        Используется для прогнозирования фаз развития растений.
        """)

        # СЭТ выше 5°C
        set_5 = sum(max(0, w.temp_avg_c - 5) for w in all_weather)
        # СЭТ выше 10°C
        set_10 = sum(max(0, w.temp_avg_c - 10) for w in all_weather)

        col1, col2 = st.columns(2)

        with col1:
            st.metric("∑T > 5°C", f"{set_5:.0f}°C")
            st.caption("Для культур умеренного пояса")

        with col2:
            st.metric("∑T > 10°C", f"{set_10:.0f}°C")
            st.caption("Для теплолюбивых культур")

# ========================================
# TAB 4: Агроклиматические показатели
# ========================================
with tab4:
    st.subheader("Агроклиматические показатели")

    st.markdown("### 📚 Справочная информация")

    st.markdown("#### 🌡️ Потребность в тепле (СЭТ > 10°C)")

    crop_requirements = pd.DataFrame({
        "Культура": [
            "Яровая пшеница",
            "Ячмень яровой",
            "Овес",
            "Горох",
            "Подсолнечник",
            "Кукуруза (зерно)",
            "Соя"
        ],
        "СЭТ (°C)": [
            "1200-1600",
            "1000-1400",
            "1000-1500",
            "1200-1600",
            "1800-2200",
            "2200-2600",
            "1800-2500"
        ],
        "Вегетационный период (дней)": [
            "85-100",
            "75-90",
            "80-110",
            "70-90",
            "100-130",
            "120-150",
            "110-140"
        ]
    })
    st.dataframe(crop_requirements, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("#### 💧 Коэффициент увлажнения (КУ)")

    st.info("""
    **Коэффициент увлажнения** = Сумма осадков / Испаряемость

    - **КУ > 1.0** - избыточное увлажнение
    - **КУ 0.6-1.0** - достаточное увлажнение
    - **КУ 0.3-0.6** - недостаточное увлажнение (засушливо)
    - **КУ < 0.3** - очень засушливо
    """)

    st.markdown("**Для Акмолинской области:**")
    st.write("- Средний КУ: 0.4-0.7 (зона рискованного земледелия)")
    st.write("- Годовая сумма осадков: 250-350 мм")
    st.write("- За вегетационный период: 150-200 мм")

    st.markdown("---")
    st.markdown("#### ❄️ Критические температуры")

    critical_temps = pd.DataFrame({
        "Фаза развития": [
            "Всходы пшеницы",
            "Кущение пшеницы",
            "Цветение пшеницы",
            "Всходы подсолнечника",
            "Цветение подсолнечника"
        ],
        "Критическая T (°C)": [
            "-9 до -10",
            "-16 до -18",
            "-1 до -2",
            "-5 до -6",
            "-1 до -2"
        ],
        "Последствия": [
            "Гибель всходов",
            "Повреждение узла кущения",
            "Стерильность пыльцы",
            "Гибель растений",
            "Пустозерность"
        ]
    })
    st.dataframe(critical_temps, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.warning("""
    **⚠️ Важные периоды для мониторинга погоды:**
    - **Весенние заморозки** (май) - опасны для всходов
    - **Суховеи** (июнь-июль) - критичны для цветения и налива
    - **Осадки во время уборки** (август-сентябрь) - влияют на качество зерна
    - **Зимние температуры** (для озимых) - морозостойкость
    """)

# Футер
st.markdown("---")
st.markdown("🌤️ **Метеорологические данные** | Версия 1.0")
