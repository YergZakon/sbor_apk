"""
Harvest - Учет уборки урожая
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

from modules.database import get_db, Farm, Field, Operation, HarvestData, SowingDetail, Machinery, Implements
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
from modules.validators import DataValidator
from utils.formatters import format_date, format_area, format_number
from utils.charts import create_bar_chart, create_grouped_bar_chart, create_scatter_chart

# Настройка страницы
st.set_page_config(page_title="Уборка урожая", page_icon="🚜", layout="wide")

# Требуем авторизацию и привязку к хозяйству
require_auth()
require_farm_binding()

st.title("🚜 Учет уборки урожая")
st.caption(f"Пользователь: **{get_user_display_name()}**")

# Инициализация валидатора
validator = DataValidator()

# Загрузка справочника культур
def load_crops_reference():
    """Загрузка справочника культур из JSON"""
    reference_path = Path(__file__).parent.parent / "data" / "crops.json"
    try:
        with open(reference_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Справочник культур не найден!")
        return {}

crops_ref = load_crops_reference()

# Загрузка справочника комбайнов
combines_ref = {}
try:
    combines_path = Path(__file__).parent.parent / "data" / "combines.json"
    if combines_path.exists():
        with open(combines_path, 'r', encoding='utf-8') as f:
            combines_ref = json.load(f)
except Exception as e:
    pass  # Справочник опционален

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
    st.warning("⚠️ Сначала создайте хозяйство на странице импорта!")
    st.stop()

# Получение списка полей
fields = filter_query_by_farm(db.query(Field), Field).all()
if not fields:
    st.warning("⚠️ Сначала добавьте поля на странице 'Поля'!")
    st.stop()

# Табы
tab1, tab2, tab3, tab4 = st.tabs(["📝 Регистрация уборки", "📊 История уборки", "📈 Анализ урожайности", "🎯 Целевые показатели"])

# ========================================
# TAB 1: Регистрация уборки
# ========================================
with tab1:
    st.subheader("Регистрация уборки урожая")

    with st.form("harvest_form"):
        col1, col2 = st.columns(2)

        with col1:
            # Выбор поля
            field_options = {f"{f.field_code} - {f.name}": f for f in fields}
            selected_field_name = st.selectbox(
                "Поле *",
                options=list(field_options.keys()),
                help="Выберите поле для регистрации уборки"
            )
            selected_field = field_options[selected_field_name]

            # Дата начала уборки
            harvest_date = st.date_input(
                "Дата начала уборки *",
                value=date.today(),
                help="Дата начала уборки урожая"
            )

            # Дата окончания уборки
            end_date = st.date_input(
                "Дата окончания уборки",
                value=None,
                help="Дата окончания уборки (для многодневных работ)"
            )

            # Получение посевов на этом поле
            sowings = db.query(Operation, SowingDetail).join(
                SowingDetail, Operation.id == SowingDetail.operation_id
            ).filter(
                Operation.field_id == selected_field.id,
                Operation.operation_type == "sowing"
            ).order_by(Operation.operation_date.desc()).all()

            if sowings:
                sowing_options = {}
                for op, sowing in sowings:
                    key = f"{sowing.crop} - {sowing.variety} (посев {format_date(op.operation_date)})"
                    sowing_options[key] = (op, sowing)

                selected_sowing_name = st.selectbox(
                    "Посев *",
                    options=list(sowing_options.keys()),
                    help="Выберите посев для учета урожая"
                )
                _, selected_sowing = sowing_options[selected_sowing_name]
                crop_name = selected_sowing.crop
                variety_name = selected_sowing.variety
            else:
                st.warning("⚠️ На этом поле нет зарегистрированных посевов. Укажите культуру вручную.")
                crop_name = st.selectbox(
                    "Культура *",
                    options=list(crops_ref.keys()),
                    help="Выберите культуру",
                    key="harvest_crop_select"
                )

                varieties = list(crops_ref[crop_name].get("сорта", [])) if crop_name in crops_ref else []
                variety_name = st.selectbox(
                    "Сорт",
                    options=["Не указан"] + varieties,
                    help="Выберите сорт",
                    key="harvest_variety_select"
                ) if varieties else "Не указан"

            # Убранная площадь
            area_harvested = st.number_input(
                "Убранная площадь (га) *",
                min_value=0.1,
                max_value=selected_field.area_ha,
                value=selected_field.area_ha,
                step=0.1,
                help=f"Площадь поля: {format_area(selected_field.area_ha)}"
            )

        with col2:
            # Урожайность
            yield_t_ha = st.number_input(
                "Урожайность (т/га) *",
                min_value=0.1,
                max_value=15.0,
                value=2.0,
                step=0.1,
                help="Фактическая урожайность"
            )

            # Валовой сбор (автоматический расчет)
            total_yield_t = area_harvested * yield_t_ha
            st.metric("Валовой сбор", f"{format_number(total_yield_t, 2)} т")

            # Влажность зерна
            moisture_percent = st.number_input(
                "Влажность (%)",
                min_value=0.0,
                max_value=40.0,
                value=14.0,
                step=0.5,
                help="Влажность зерна при уборке"
            )

            # Засоренность
            weed_content_percent = st.number_input(
                "Засоренность (%)",
                min_value=0.0,
                max_value=20.0,
                value=2.0,
                step=0.5,
                help="Процент сорной примеси"
            )

            # Натура зерна
            test_weight = st.number_input(
                "Натура зерна (г/л)",
                min_value=500,
                max_value=900,
                value=750,
                step=10,
                help="Натура зерна (объемная масса)"
            )

        # Техника для уборки
        st.markdown("---")
        st.markdown("### 🚜 Техника для уборки")

        # Получение списка комбайнов и агрегатов
        machinery_list = filter_query_by_farm(db.query(Machinery).filter(Machinery.status == 'active'), Machinery).all()
        implements_list = filter_query_by_farm(db.query(Implements).filter(Implements.status == 'active'), Implements).all()

        combines = [m for m in machinery_list if m.machinery_type == 'combine']

        # Pre-load machinery attributes
        machinery_options = {}
        machinery_details = {}  # Для хранения деталей комбайнов

        if combines:
            for m in combines:
                # Eagerly access attributes while still in session
                m_brand = m.brand or ''
                m_model = m.model
                m_year = m.year

                display_text = f"{m_brand} {m_model} ({m_year or '-'})"
                machinery_options[display_text] = (m.id, m_year)

                # Ищем комбайн в справочнике для показа характеристик
                ref_key = f"{m_brand} {m_model}"
                if ref_key in combines_ref:
                    machinery_details[display_text] = combines_ref[ref_key]

        col_tech1, col_tech2, col_tech3 = st.columns(3)

        with col_tech1:
            selected_machinery_display = st.selectbox(
                "Комбайн",
                options=["Не выбрано"] + list(machinery_options.keys()),
                help="Выберите комбайн для уборки",
                key="harvest_machinery"
            )

            if selected_machinery_display != "Не выбрано":
                selected_machinery_id, machine_year = machinery_options[selected_machinery_display]

                # Показываем характеристики из справочника
                if selected_machinery_display in machinery_details:
                    ref_data = machinery_details[selected_machinery_display]
                    st.success(f"💪 {ref_data['мощность_лс']} л.с. | 🏷️ {ref_data['класс']} | ⚙️ {ref_data['молотильный_аппарат']}")

                    # Показываем подходящие культуры
                    if ref_data.get('культуры'):
                        cultures = ', '.join(ref_data['культуры'])
                        st.info(f"🌾 Подходит для: {cultures}")
                else:
                    st.caption(f"Год выпуска: {machine_year or 'не указан'}")
            else:
                selected_machinery_id = None
                machine_year = None

        with col_tech2:
            # Селектор жатки/хедера
            headers = [impl for impl in implements_list if impl.implement_type in ['header', 'picker']]
            implement_options = {}
            if headers:
                for i in headers:
                    display_text = f"{i.brand or ''} {i.model} ({i.working_width_m or '-'}м)"
                    implement_options[display_text] = (i.id, i.year)

            selected_implement_display = st.selectbox(
                "Жатка/Хедер",
                options=["Не выбрано"] + list(implement_options.keys()),
                help="Выберите жатку или хедер (опционально)",
                key="harvest_implement"
            )

            if selected_implement_display != "Не выбрано":
                selected_implement_id, implement_year = implement_options[selected_implement_display]
            else:
                selected_implement_id = None
                implement_year = None

        with col_tech3:
            # Способ уборки
            harvest_method = st.selectbox(
                "Способ уборки",
                options=[
                    "Прямое комбайнирование",
                    "Подбор валков (двухфазная)",
                    "Другое"
                ],
                help="Способ уборки урожая",
                key="harvest_method"
            )

            # Преобразуем в код для БД
            harvest_method_code = {
                "Прямое комбайнирование": "direct_combining",
                "Подбор валков (двухфазная)": "swath_pickup",
                "Другое": "other"
            }.get(harvest_method, "direct_combining")

            work_speed_kmh = st.number_input(
                "Рабочая скорость (км/ч)",
                min_value=0.0,
                max_value=15.0,
                value=None,
                step=0.5,
                help="Скорость движения комбайна при уборке",
                key="harvest_speed"
            )

        # Качество зерна
        st.markdown("---")
        st.markdown("### 🌾 Параметры качества")

        col3, col4, col5 = st.columns(3)

        with col3:
            protein_percent = st.number_input(
                "Белок (%)",
                min_value=0.0,
                max_value=25.0,
                value=12.5,
                step=0.1,
                help="Содержание белка в зерне"
            )

        with col4:
            gluten_percent = st.number_input(
                "Клейковина (%)",
                min_value=0.0,
                max_value=50.0,
                value=25.0,
                step=0.5,
                help="Содержание клейковины (для пшеницы)"
            )

        with col5:
            falling_number = st.number_input(
                "Число падения (сек)",
                min_value=0,
                max_value=600,
                value=300,
                step=10,
                help="Число падения (активность амилазы)"
            )

        # Рекомендуемая урожайность из справочника
        st.markdown("---")
        st.markdown("### 📊 Сравнение с целевыми показателями")

        if crop_name in crops_ref:
            crop_data = crops_ref[crop_name]
            typical_yields = crop_data.get("урожайность_типичная", {})

            if typical_yields:
                min_yield = typical_yields.get("мин", 0)
                max_yield = typical_yields.get("макс", 0)
                avg_yield = typical_yields.get("средняя", 0)

                col6, col7, col8 = st.columns(3)

                with col6:
                    st.metric("Минимальная", f"{min_yield} т/га")
                with col7:
                    st.metric("Средняя", f"{avg_yield} т/га", delta=f"{yield_t_ha - avg_yield:+.2f} т/га")
                with col8:
                    st.metric("Максимальная", f"{max_yield} т/га")

                # Индикатор
                if yield_t_ha >= avg_yield:
                    st.success(f"✅ Урожайность выше средней на {((yield_t_ha/avg_yield - 1) * 100):.1f}%")
                else:
                    st.warning(f"⚠️ Урожайность ниже средней на {((1 - yield_t_ha/avg_yield) * 100):.1f}%")

        # Экономические показатели
        st.markdown("---")
        st.markdown("### 💰 Экономические показатели")

        col9, col10 = st.columns(2)

        with col9:
            price_per_ton = st.number_input(
                "Цена реализации (тг/т)",
                min_value=0,
                max_value=200000,
                value=75000,
                step=1000,
                help="Цена реализации зерна"
            )

        with col10:
            total_revenue = total_yield_t * price_per_ton
            st.metric("Выручка с поля", f"{format_number(total_revenue, 0)} тг")

        # Примечание
        notes = st.text_area(
            "Примечание",
            height=80,
            help="Дополнительная информация об уборке"
        )

        # Кнопка отправки
        submitted = st.form_submit_button("✅ Зарегистрировать уборку", use_container_width=True)

        if submitted:
            # Валидация
            errors = []

            # Проверка даты
            is_valid, msg = validator.validate_date(harvest_date)
            if not is_valid:
                errors.append(f"Дата: {msg}")

            # Проверка площади
            is_valid, msg = validator.validate_area(area_harvested)
            if not is_valid:
                errors.append(f"Площадь: {msg}")

            if area_harvested > selected_field.area_ha:
                errors.append(f"Убранная площадь ({area_harvested} га) превышает площадь поля ({selected_field.area_ha} га)")

            # Проверка урожайности
            is_valid, msg = validator.validate_yield(yield_t_ha, "wheat")
            if not is_valid:
                errors.append(f"Урожайность: {msg}")

            # Проверка влажности
            if moisture_percent > 30:
                errors.append("Влажность слишком высокая (>30%)")

            if errors:
                st.error("❌ Ошибки валидации:\n" + "\n".join(f"- {e}" for e in errors))
            else:
                try:
                    # Создаем операцию
                    # Добавляем информацию о способе уборки в примечания
                    harvest_notes = f"Способ уборки: {harvest_method}"
                    if notes:
                        harvest_notes = f"{harvest_notes}\n{notes}"

                    operation = Operation(
                        farm_id=farm.id,
                        field_id=selected_field.id,
                        operation_type="harvest",
                        operation_date=harvest_date,
                        end_date=end_date if end_date else None,
                        area_processed_ha=area_harvested,
                        machine_id=selected_machinery_id,
                        implement_id=selected_implement_id,  # Добавлен implement (жатка/хедер)
                        machine_year=machine_year,
                        implement_year=implement_year if selected_implement_id else None,  # Добавлен год агрегата
                        work_speed_kmh=work_speed_kmh if work_speed_kmh else None,
                        notes=harvest_notes
                    )
                    db.add(operation)
                    db.flush()

                    # Создаем данные уборки
                    harvest_data = HarvestData(
                        operation_id=operation.id,
                        crop=crop_name,
                        variety=variety_name if variety_name != "Не указан" else None,
                        yield_t_ha=yield_t_ha,
                        total_yield_t=total_yield_t,
                        moisture_percent=moisture_percent,
                        protein_percent=protein_percent if protein_percent > 0 else None,
                        gluten_percent=gluten_percent if gluten_percent > 0 else None,
                        test_weight_g_l=test_weight if test_weight > 0 else None,
                        falling_number=falling_number if falling_number > 0 else None,
                        weed_content_percent=weed_content_percent if weed_content_percent > 0 else None
                    )
                    db.add(harvest_data)

                    db.commit()

                    st.success(f"✅ Уборка зарегистрирована! Валовой сбор: {format_number(total_yield_t, 2)} т")
                    st.balloons()

                except Exception as e:
                    db.rollback()
                    st.error(f"❌ Ошибка при сохранении: {str(e)}")

# ========================================
# TAB 2: История уборки
# ========================================
with tab2:
    st.subheader("История уборки урожая")

    # Фильтры
    col1, col2, col3 = st.columns(3)

    with col1:
        filter_field = st.selectbox(
            "Фильтр по полю",
            options=["Все поля"] + [f"{f.field_code} - {f.name}" for f in fields],
            key="filter_field_history"
        )

    with col2:
        all_crops = list(crops_ref.keys())
        filter_crop = st.selectbox(
            "Фильтр по культуре",
            options=["Все культуры"] + all_crops,
            key="filter_crop_history"
        )

    with col3:
        filter_year = st.selectbox(
            "Фильтр по году",
            options=["Все годы"] + list(range(datetime.now().year, datetime.now().year - 10, -1)),
            key="filter_year_history"
        )

    # Получение данных
    query = db.query(Operation, HarvestData, Field).join(
        HarvestData, Operation.id == HarvestData.operation_id
    ).join(
        Field, Operation.field_id == Field.id
    ).filter(
        Operation.operation_type == "harvest",
        Field.farm_id == farm.id  # КРИТИЧЕСКИЙ ФИЛЬТР: только операции текущего хозяйства
    )

    # Применение фильтров
    if filter_field != "Все поля":
        field_code = filter_field.split(" - ")[0]
        query = query.filter(Field.field_code == field_code)

    if filter_crop != "Все культуры":
        query = query.filter(HarvestData.crop == filter_crop)

    if filter_year != "Все годы":
        from sqlalchemy import extract
        query = query.filter(extract('year', Operation.operation_date) == filter_year)

    harvests = query.order_by(Operation.operation_date.desc()).all()

    if harvests:
        st.metric("Всего уборок", len(harvests))

        # Таблица
        data = []
        for op, harvest, field in harvests:
            data.append({
                "Дата": format_date(op.operation_date),
                "Поле": f"{field.field_code} - {field.name}",
                "Культура": harvest.crop,
                "Сорт": harvest.variety or "-",
                "Площадь (га)": format_area(op.area_processed_ha),
                "Урожайность (т/га)": format_number(harvest.yield_t_ha, 2),
                "Валовой сбор (т)": format_number(harvest.total_yield_t, 2),
                "Влажность (%)": format_number(harvest.moisture_percent, 1) if harvest.moisture_percent else "-",
                "Белок (%)": format_number(harvest.protein_percent, 1) if harvest.protein_percent else "-"
            })

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Экспорт
        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                "📥 Скачать CSV",
                csv,
                "harvest_history.csv",
                "text/csv",
                use_container_width=True
            )

        # Статистика
        st.markdown("---")
        st.markdown("### 📊 Статистика")

        col1, col2, col3, col4 = st.columns(4)

        total_area = sum(op.area_processed_ha for op, _, _ in harvests)
        total_yield = sum(harvest.total_yield_t for _, harvest, _ in harvests)
        avg_yield = total_yield / total_area if total_area > 0 else 0
        max_yield = max(harvest.yield_t_ha for _, harvest, _ in harvests)

        with col1:
            st.metric("Убрано площади", format_area(total_area))
        with col2:
            st.metric("Валовой сбор", f"{format_number(total_yield, 2)} т")
        with col3:
            st.metric("Средняя урожайность", f"{format_number(avg_yield, 2)} т/га")
        with col4:
            st.metric("Максимальная урожайность", f"{format_number(max_yield, 2)} т/га")

        # Графики
        col1, col2 = st.columns(2)

        with col1:
            # График по культурам
            crop_data = {}
            for _, harvest, _ in harvests:
                crop = harvest.crop
                crop_data[crop] = crop_data.get(crop, 0) + harvest.total_yield_t

            fig_crop = px.pie(
                values=list(crop_data.values()),
                names=list(crop_data.keys()),
                title="Валовой сбор по культурам (т)"
            )
            st.plotly_chart(fig_crop, use_container_width=True)

        with col2:
            # График урожайности по полям
            field_yields = {}
            field_areas = {}
            for op, harvest, field in harvests:
                field_name = f"{field.field_code}"
                if field_name not in field_yields:
                    field_yields[field_name] = 0
                    field_areas[field_name] = 0
                field_yields[field_name] += harvest.total_yield_t
                field_areas[field_name] += op.area_processed_ha

            # Средняя урожайность по полям
            avg_yields_by_field = {k: field_yields[k] / field_areas[k] for k in field_yields.keys()}

            fig_fields = px.bar(
                x=list(avg_yields_by_field.keys()),
                y=list(avg_yields_by_field.values()),
                title="Средняя урожайность по полям (т/га)",
                labels={"x": "Поля", "y": "Урожайность (т/га)"}
            )
            st.plotly_chart(fig_fields, use_container_width=True)

    else:
        st.info("📭 Пока нет записей об уборке урожая")

# ========================================
# TAB 3: Анализ урожайности
# ========================================
with tab3:
    st.subheader("Анализ урожайности")

    # Получение всех уборок
    all_harvests = db.query(Operation, HarvestData, Field).join(
        HarvestData, Operation.id == HarvestData.operation_id
    ).join(
        Field, Operation.field_id == Field.id
    ).filter(
        Operation.operation_type == "harvest",
        Field.farm_id == farm.id  # КРИТИЧЕСКИЙ ФИЛЬТР: только операции текущего хозяйства
    ).all()

    if all_harvests:
        # Анализ по годам
        st.markdown("### 📅 Динамика по годам")

        yearly_data = {}
        for op, harvest, field in all_harvests:
            year = op.operation_date.year
            if year not in yearly_data:
                yearly_data[year] = {"total_yield": 0, "total_area": 0}
            yearly_data[year]["total_yield"] += harvest.total_yield_t
            yearly_data[year]["total_area"] += op.area_processed_ha

        years = sorted(yearly_data.keys())
        avg_yields_by_year = [yearly_data[y]["total_yield"] / yearly_data[y]["total_area"] for y in years]
        total_yields_by_year = [yearly_data[y]["total_yield"] for y in years]

        col1, col2 = st.columns(2)

        with col1:
            fig_year_avg = go.Figure()
            fig_year_avg.add_trace(go.Scatter(
                x=years,
                y=avg_yields_by_year,
                mode='lines+markers',
                name='Средняя урожайность',
                line=dict(color='green', width=3),
                marker=dict(size=10)
            ))
            fig_year_avg.update_layout(
                title="Средняя урожайность по годам",
                xaxis_title="Год",
                yaxis_title="Урожайность (т/га)"
            )
            st.plotly_chart(fig_year_avg, use_container_width=True)

        with col2:
            fig_year_total = go.Figure()
            fig_year_total.add_trace(go.Bar(
                x=years,
                y=total_yields_by_year,
                name='Валовой сбор',
                marker_color='orange'
            ))
            fig_year_total.update_layout(
                title="Валовой сбор по годам",
                xaxis_title="Год",
                yaxis_title="Валовой сбор (т)"
            )
            st.plotly_chart(fig_year_total, use_container_width=True)

        # Анализ по культурам
        st.markdown("---")
        st.markdown("### 🌾 Анализ по культурам")

        crop_analysis = {}
        for op, harvest, field in all_harvests:
            crop = harvest.crop
            if crop not in crop_analysis:
                crop_analysis[crop] = {"yields": [], "areas": []}
            crop_analysis[crop]["yields"].append(harvest.yield_t_ha)
            crop_analysis[crop]["areas"].append(op.area_processed_ha)

        # Средняя урожайность по культурам
        crop_avg_yields = {crop: sum(data["yields"]) / len(data["yields"]) for crop, data in crop_analysis.items()}
        crop_total_areas = {crop: sum(data["areas"]) for crop, data in crop_analysis.items()}

        col1, col2 = st.columns(2)

        with col1:
            fig_crop_yield = px.bar(
                x=list(crop_avg_yields.keys()),
                y=list(crop_avg_yields.values()),
                title="Средняя урожайность по культурам (т/га)",
                labels={"x": "Культуры", "y": "Урожайность (т/га)"},
                color=list(crop_avg_yields.values()),
                color_continuous_scale="Greens"
            )
            st.plotly_chart(fig_crop_yield, use_container_width=True)

        with col2:
            fig_crop_area = px.pie(
                values=list(crop_total_areas.values()),
                names=list(crop_total_areas.keys()),
                title="Распределение площадей по культурам"
            )
            st.plotly_chart(fig_crop_area, use_container_width=True)

        # Корреляция качества и урожайности
        st.markdown("---")
        st.markdown("### 🔬 Качество зерна vs Урожайность")

        # Данные для scatter plot
        yields_for_scatter = []
        proteins_for_scatter = []
        crops_for_scatter = []

        for op, harvest, field in all_harvests:
            if harvest.protein_percent:
                yields_for_scatter.append(harvest.yield_t_ha)
                proteins_for_scatter.append(harvest.protein_percent)
                crops_for_scatter.append(harvest.crop)

        if yields_for_scatter:
            fig_scatter = px.scatter(
                x=yields_for_scatter,
                y=proteins_for_scatter,
                color=crops_for_scatter,
                title="Зависимость содержания белка от урожайности",
                labels={"x": "Урожайность (т/га)", "y": "Белок (%)"},
                hover_data={"Культура": crops_for_scatter}
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

    else:
        st.info("📭 Нет данных для анализа")

# ========================================
# TAB 4: Целевые показатели
# ========================================
with tab4:
    st.subheader("Целевые показатели урожайности")

    st.markdown("""
    ### 🎯 Целевые показатели для Акмолинской области

    Рекомендуемые показатели урожайности основных культур в условиях
    Акмолинской области при соблюдении агротехнологий:
    """)

    # Таблица целевых показателей
    target_data = []
    for crop_name, crop_info in crops_ref.items():
        typical_yields = crop_info.get("урожайность_типичная", {})
        if typical_yields:
            target_data.append({
                "Культура": crop_name,
                "Минимум (т/га)": typical_yields.get("мин", "-"),
                "Средняя (т/га)": typical_yields.get("средняя", "-"),
                "Максимум (т/га)": typical_yields.get("макс", "-"),
                "Условие": typical_yields.get("условие", "-")
            })

    if target_data:
        df_targets = pd.DataFrame(target_data)
        st.dataframe(df_targets, use_container_width=True, hide_index=True)

    # Факторы влияния
    st.markdown("---")
    st.markdown("### 🌟 Факторы, влияющие на урожайность")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Природно-климатические:**
        - Количество осадков за вегетацию
        - Температурный режим
        - Заморозки в критические периоды
        - Влагозапасы в почве
        - Засухи и суховеи
        """)

    with col2:
        st.markdown("""
        **Агротехнические:**
        - Сроки посева
        - Норма высева
        - Качество семян
        - Система удобрений (NPK)
        - Защита от болезней и вредителей
        - Качество обработки почвы
        """)

    # Рекомендации
    st.markdown("---")
    st.markdown("### 💡 Рекомендации для повышения урожайности")

    st.info("""
    1. **Оптимизация питания:**
       - Внесение удобрений на основе агрохимического анализа
       - Соблюдение баланса NPK
       - Подкормки в критические фазы

    2. **Защита растений:**
       - Своевременная обработка против болезней и вредителей
       - Контроль сорняков (гербициды)
       - Мониторинг фитосанитарного состояния

    3. **Агротехника:**
       - Соблюдение севооборота
       - Качественная подготовка почвы
       - Оптимальные сроки сева
       - Использование качественных семян

    4. **Влагосбережение:**
       - Снегозадержание
       - Минимизация обработки почвы
       - Мульчирование пожнивными остатками
    """)

# Футер
st.markdown("---")
st.markdown("🚜 **Учет уборки урожая** | Версия 1.0")
