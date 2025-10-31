"""
Sowing - Учет посева
Регистрация посевных работ с автозаполнением рекомендуемых параметров
"""
import streamlit as st
import pandas as pd
import json
from datetime import datetime, date
from pathlib import Path
from sqlalchemy.orm import Session
from modules.database import SessionLocal, Farm, Field, Operation, SowingDetail, Machinery, Implements
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
from modules.validators import validator
from modules.config import settings
from utils.reference_loader import load_crops, load_tractors, load_reference

# Настройка страницы
st.set_page_config(page_title="Посев", page_icon="🌾", layout="wide")

# Требуем авторизацию и привязку к хозяйству
require_auth()
require_farm_binding()

# Заголовок
st.title("🌾 Учет посевных работ")
st.caption(f"Пользователь: **{get_user_display_name()}**")

# Получение сессии БД
db = SessionLocal()

# Загрузка справочников через универсальный загрузчик
crops_reference = load_crops()
tractors_ref = load_tractors()
seed_treatments_ref = load_reference('seed_treatments.json', show_error=False)

try:
    # Проверка наличия хозяйства
    user = get_current_user()

    if is_admin():
        farm = db.query(Farm).first()
    else:
        user_farm_id = user.get("farm_id") if user else None
        farm = db.query(Farm).filter(Farm.id == user_farm_id).first() if user_farm_id else None

    if not farm:
        st.error("❌ Сначала необходимо зарегистрировать хозяйство!")
        st.stop()

    # Получение полей
    fields = filter_query_by_farm(db.query(Field), Field).all()

    if not fields:
        st.warning("⚠️ Сначала добавьте поля в разделе 'Поля'")
        if st.button("➕ Перейти к добавлению полей"):
            st.switch_page("pages/2_🌱_Поля.py")
        st.stop()

    # ============================================================================
    # ФОРМА ДОБАВЛЕНИЯ ПОСЕВА
    # ============================================================================

    st.markdown("### ➕ Регистрация посева")

    with st.form("sowing_form"):
        # Базовая информация
        st.markdown("#### 📋 Основная информация")

        col1, col2, col3 = st.columns(3)

        with col1:
            # Выбор поля
            field_options = {f"{f.name or f.field_code} ({f.area_ha} га)": f for f in fields}
            selected_field_name = st.selectbox(
                "Поле*",
                options=list(field_options.keys()),
                help="Выберите поле для посева"
            )
            selected_field = field_options[selected_field_name]

        with col2:
            # Дата начала посева
            sowing_date = st.date_input(
                "Дата начала посева*",
                value=datetime.now().date(),
                max_value=datetime.now().date(),
                help="Дата начала посевных работ"
            )

        with col3:
            # Дата окончания посева
            end_date = st.date_input(
                "Дата окончания",
                value=None,
                max_value=datetime.now().date(),
                help="Дата окончания посевных работ (для многодневных операций)"
            )

        col1, col2 = st.columns(2)

        with col1:
            # Обработанная площадь
            area_processed = st.number_input(
                "Площадь посева (га)*",
                min_value=0.1,
                max_value=float(selected_field.area_ha),
                value=float(selected_field.area_ha),
                step=0.1,
                help="Фактически засеянная площадь"
            )

        with col2:
            # Рабочая скорость
            work_speed_kmh = st.number_input(
                "Рабочая скорость (км/ч)",
                min_value=0.0,
                max_value=25.0,
                value=None,
                step=0.5,
                help="Скорость движения агрегата во время посева"
            )

        st.markdown("---")
        st.markdown("#### 🌱 Культура и сорт")

        col1, col2 = st.columns(2)

        with col1:
            # Выбор культуры
            selected_crop = st.selectbox(
                "Культура*",
                options=list(crops_reference.keys()),
                help="Выберите культуру для посева",
                key="sowing_crop_select"
            )

            # Получение данных о культуре
            crop_data = crops_reference[selected_crop]

        with col2:
            # Выбор сорта (реактивный к выбранной культуре)
            varieties = crop_data.get("сорта", [])
            selected_variety = st.selectbox(
                "Сорт*",
                options=["Не указан"] + (varieties if varieties else []),
                help="Выберите сорт культуры",
                key="sowing_variety_select"
            )

        # Показать рекомендации
        with st.expander("💡 Рекомендации для " + selected_crop, expanded=True):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**Норма высева:**")
                norm = crop_data.get("норма_высева", {})
                st.info(f"Рекомендуемая: {norm.get('рекомендуемая', '-')} {norm.get('единица', 'кг/га')}")
                st.caption(f"Диапазон: {norm.get('мин', '-')} - {norm.get('макс', '-')} {norm.get('единица', '')}")

            with col2:
                st.markdown("**Глубина заделки:**")
                depth = crop_data.get("глубина_заделки", {})
                st.info(f"Оптимум: {depth.get('оптимум', '-')} {depth.get('единица', 'см')}")
                if 'диапазон' in depth:
                    st.caption(f"Диапазон: {depth['диапазон'][0]} - {depth['диапазон'][1]} {depth.get('единица', '')}")

            with col3:
                st.markdown("**Междурядье:**")
                spacing = crop_data.get("междурядье", {})
                if spacing:
                    st.info(f"{spacing.get('стандарт', '-')} {spacing.get('единица', 'см')}")
                else:
                    st.caption("Не указано")

        st.markdown("---")
        st.markdown("#### ⚙️ Параметры посева")

        col1, col2, col3, col4 = st.columns(4)

        # Получение рекомендуемых значений
        recommended_rate = crop_data.get("норма_высева", {}).get("рекомендуемая", 180)
        recommended_depth = crop_data.get("глубина_заделки", {}).get("оптимум", 5)
        recommended_spacing = crop_data.get("междурядье", {}).get("стандарт", 15)

        with col1:
            seeding_rate = st.number_input(
                f"Норма высева ({crop_data.get('норма_высева', {}).get('единица', 'кг/га')})*",
                min_value=1.0,
                max_value=500.0,
                value=float(recommended_rate),
                step=1.0,
                help="Фактическая норма высева"
            )

        with col2:
            seeding_depth = st.number_input(
                "Глубина заделки (см)*",
                min_value=1.0,
                max_value=15.0,
                value=float(recommended_depth),
                step=0.5,
                help="Глубина заделки семян"
            )

        with col3:
            row_spacing = st.number_input(
                "Междурядье (см)",
                min_value=10.0,
                max_value=100.0,
                value=float(recommended_spacing),
                step=5.0,
                help="Расстояние между рядами"
            )

        with col4:
            if seed_treatments_ref:
                seed_treatment_options = ["Не указан"] + list(seed_treatments_ref.keys())
                seed_treatment = st.selectbox(
                    "Протравитель",
                    options=seed_treatment_options,
                    help="Препарат для протравливания семян"
                )

                # Показываем информацию о выбранном протравителе
                if seed_treatment and seed_treatment != "Не указан":
                    treatment_data = seed_treatments_ref.get(seed_treatment, {})
                    if treatment_data:
                        st.caption(f"🧪 {treatment_data.get('действующее_вещество', '-')}")
                        st.caption(f"📊 Норма: {treatment_data.get('норма_применения', '-')}")
            else:
                seed_treatment = st.text_input(
                    "Протравитель",
                    placeholder="Например: Витавакс",
                    help="Препарат для протравливания семян"
                )

        st.markdown("---")
        st.markdown("#### 🌾 Семенной материал")

        col1, col2 = st.columns(2)

        with col1:
            seed_reproduction = st.selectbox(
                "Репродукция семян",
                options=['Элита', 'Суперэлита', '1-я репродукция', '2-я репродукция', '3-я репродукция', 'Гибрид F1', 'Гибрид F2', 'Гибрид F3', 'Другое'],
                index=None,
                help="Репродукция используемого семенного материала"
            )

        with col2:
            seed_origin_country = st.text_input(
                "Страна происхождения семян",
                placeholder="Например: Казахстан, Россия, Канада",
                help="Страна производства семенного материала"
            )

        # Совмещенный посев с удобрениями
        st.markdown("---")
        st.markdown("#### 🌱 Совмещенный посев с удобрениями")

        combined_with_fertilizer = st.checkbox(
            "Совмещенный посев с внесением удобрений",
            value=False,
            help="Отметьте, если удобрения вносились одновременно с посевом"
        )

        if combined_with_fertilizer:
            col1, col2 = st.columns(2)

            with col1:
                combined_fertilizer_name = st.text_input(
                    "Название удобрения",
                    placeholder="Например: Аммофос, NPK 16:16:16",
                    help="Название удобрения, внесенного при посеве"
                )

            with col2:
                combined_fertilizer_rate = st.number_input(
                    "Норма внесения (кг/га)",
                    min_value=0.0,
                    max_value=500.0,
                    value=None,
                    step=5.0,
                    help="Норма внесения удобрения при посеве"
                )
        else:
            combined_fertilizer_name = None
            combined_fertilizer_rate = None

        st.markdown("---")
        st.markdown("#### 🚜 Техника и агрегаты")

        # Получение списка техники и агрегатов
        machinery_list = filter_query_by_farm(db.query(Machinery).filter(Machinery.status == 'active'), Machinery).all()
        implements_list = filter_query_by_farm(db.query(Implements).filter(Implements.status == 'active'), Implements).all()

        col1, col2 = st.columns(2)

        with col1:
            # Create machinery options with pre-loaded attributes
            machinery_options = {}
            machinery_details = {}  # Для хранения деталей техники

            if machinery_list:
                for m in machinery_list:
                    # Eagerly access attributes while still in session
                    m_brand = m.brand or ''
                    m_model = m.model
                    m_year = m.year
                    m_power = m.engine_power_hp

                    display_text = f"{m_brand} {m_model} ({m_year or '-'})"
                    machinery_options[display_text] = (m.id, m_year)

                    # Ищем технику в справочнике для показа характеристик
                    ref_key = f"{m_brand} {m_model}"
                    if ref_key in tractors_ref:
                        machinery_details[display_text] = tractors_ref[ref_key]

            selected_machinery_display = st.selectbox(
                "Техника (трактор)",
                options=["Не выбрано"] + list(machinery_options.keys()),
                help="Выберите трактор или другую технику"
            )

            if selected_machinery_display != "Не выбрано":
                selected_machinery_id, machine_year = machinery_options[selected_machinery_display]

                # Показываем характеристики из справочника
                if selected_machinery_display in machinery_details:
                    ref_data = machinery_details[selected_machinery_display]
                    st.success(f"💪 {ref_data['мощность_лс']} л.с. | 🏷️ {ref_data['класс']} | 🚜 {ref_data['тип']}")

                    # Проверка пригодности для посева
                    if 'Посев' in ref_data.get('применение', []):
                        st.info("✅ Подходит для посевных работ")
                    else:
                        st.warning("⚠️ Не оптимальна для посева (см. применение в справочнике)")
                else:
                    st.caption(f"Год выпуска: {machine_year or 'не указан'}")
            else:
                selected_machinery_id = None
                machine_year = None

        with col2:
            # Фильтруем только сеялки и pre-load attributes
            implement_options = {}
            if implements_list:
                for impl in implements_list:
                    if impl.implement_type in ['seeder', 'planter']:
                        # Eagerly access attributes while still in session
                        display_text = f"{impl.brand or ''} {impl.model} ({impl.working_width_m or '-'}м)"
                        implement_options[display_text] = (impl.id, impl.year, impl.working_width_m)

            selected_implement_display = st.selectbox(
                "Агрегат (сеялка)",
                options=["Не выбрано"] + list(implement_options.keys()),
                help="Выберите сеялку или сажалку"
            )

            if selected_implement_display != "Не выбрано":
                selected_implement_id, implement_year, implement_width = implement_options[selected_implement_display]
                st.caption(f"Год выпуска: {implement_year or 'не указан'}, Ширина: {implement_width or '-'}м")
            else:
                selected_implement_id = None
                implement_year = None

        if not machinery_list and not implements_list:
            st.info("💡 Техника не добавлена. Перейдите в раздел 'Техника' для добавления.")

        st.markdown("---")

        with st.expander("🌤️ Условия посева (опционально)", expanded=False):
            col1, col2, col3 = st.columns(3)

            with col1:
                soil_temp = st.number_input(
                    "Температура почвы (°C)",
                    min_value=-5.0,
                    max_value=40.0,
                    value=10.0,
                    step=0.5,
                    help="Температура почвы на глубине посева"
                )

            with col2:
                soil_moisture = st.number_input(
                    "Влажность почвы (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=60.0,
                    step=1.0,
                    help="Влажность почвы в процентах"
                )

            with col3:
                weather_conditions = st.text_input(
                    "Погодные условия",
                    placeholder="Например: Ясно, +15°C",
                    help="Описание погоды во время посева"
                )

        st.markdown("---")
        st.markdown("#### 👤 Механизатор и примечания")

        col1, col2 = st.columns(2)

        with col1:
            operator = st.text_input(
                "Механизатор",
                placeholder="ФИО механизатора",
                help="Кто проводил посев"
            )

        with col2:
            notes = st.text_area(
                "Примечания",
                placeholder="Дополнительная информация...",
                help="Любые дополнительные заметки"
            )

        # Автоматические расчеты
        st.markdown("---")
        st.markdown("#### 🧮 Автоматические расчеты")

        col1, col2, col3 = st.columns(3)

        # Расчет потребности в семенах
        total_seeds_needed = area_processed * seeding_rate

        with col1:
            st.metric(
                "Потребность в семенах",
                f"{total_seeds_needed:,.1f} кг",
                help="Общая потребность в семенах для указанной площади"
            )

        with col2:
            # Расчет стоимости семян (примерная)
            seed_cost_per_kg = 150  # Примерная цена, можно сделать из справочника
            total_seed_cost = total_seeds_needed * seed_cost_per_kg
            st.metric(
                "Примерная стоимость семян",
                f"{total_seed_cost:,.0f} тг",
                help="Ориентировочная стоимость семян"
            )

        with col3:
            # Рекомендация NPK
            npk = crop_data.get("потребность_NPK", {})
            if npk:
                n = npk.get("N", 0)
                p = npk.get("P2O5", 0)
                k = npk.get("K2O", 0)
                st.metric(
                    "Рекомендация NPK",
                    f"N{n}:P{p}:K{k}",
                    help="Рекомендуемая потребность в удобрениях"
                )

        # Кнопка отправки
        st.markdown("---")
        submitted = st.form_submit_button("✅ Зарегистрировать посев", use_container_width=True, type="primary")

        if submitted:
            # Валидация
            errors = []

            if not selected_field:
                errors.append("Поле не выбрано")

            if not sowing_date:
                errors.append("Дата посева обязательна")

            if area_processed > selected_field.area_ha:
                errors.append(f"Площадь посева ({area_processed} га) превышает площадь поля ({selected_field.area_ha} га)")

            if seeding_rate <= 0:
                errors.append("Норма высева должна быть больше 0")

            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                try:
                    # Создание операции
                    new_operation = Operation(
                        farm_id=farm.id,
                        field_id=selected_field.id,
                        operation_type="sowing",
                        operation_date=sowing_date,
                        end_date=end_date if end_date else None,
                        crop=selected_crop,
                        variety=selected_variety if selected_variety != "Не указан" else None,
                        area_processed_ha=area_processed,
                        machine_id=selected_machinery_id if selected_machinery_id else None,
                        implement_id=selected_implement_id if selected_implement_id else None,
                        machine_year=machine_year,
                        implement_year=implement_year,
                        work_speed_kmh=work_speed_kmh if work_speed_kmh else None,
                        operator=operator if operator else None,
                        weather_conditions=weather_conditions if weather_conditions else None,
                        notes=notes if notes else None
                    )

                    db.add(new_operation)
                    db.flush()  # Получить ID операции

                    # Создание деталей посева
                    sowing_detail = SowingDetail(
                        operation_id=new_operation.id,
                        crop=selected_crop,
                        variety=selected_variety if selected_variety != "Не указан" else None,
                        seeding_rate_kg_ha=seeding_rate,
                        seeding_depth_cm=seeding_depth,
                        row_spacing_cm=row_spacing if row_spacing else None,
                        seed_treatment=seed_treatment if seed_treatment else None,
                        soil_temp_c=soil_temp if soil_temp else None,
                        soil_moisture_percent=soil_moisture if soil_moisture else None,
                        total_seeds_kg=total_seeds_needed,
                        seed_reproduction=seed_reproduction if seed_reproduction else None,
                        seed_origin_country=seed_origin_country if seed_origin_country else None,
                        combined_with_fertilizer=combined_with_fertilizer,
                        combined_fertilizer_name=combined_fertilizer_name if combined_with_fertilizer else None,
                        combined_fertilizer_rate_kg_ha=combined_fertilizer_rate if combined_with_fertilizer else None
                    )

                    db.add(sowing_detail)
                    db.commit()

                    st.success(f"✅ Посев успешно зарегистрирован!")
                    st.balloons()

                    # Показать сводку
                    with st.expander("📄 Сводка операции", expanded=True):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown(f"**Поле:** {selected_field.name or selected_field.field_code}")
                            st.markdown(f"**Дата:** {sowing_date}")
                            st.markdown(f"**Культура:** {selected_crop}")
                            st.markdown(f"**Сорт:** {selected_variety}")
                            st.markdown(f"**Площадь:** {area_processed} га")

                        with col2:
                            st.markdown(f"**Норма высева:** {seeding_rate} кг/га")
                            st.markdown(f"**Глубина:** {seeding_depth} см")
                            st.markdown(f"**Потребность в семенах:** {total_seeds_needed:,.1f} кг")
                            st.markdown(f"**Механизатор:** {operator or 'Не указан'}")

                    # Предложение перейти к следующему шагу
                    st.info("💡 Следующий шаг: Внесение удобрений. Используйте боковое меню для перехода.")

                except Exception as e:
                    db.rollback()
                    st.error(f"❌ Ошибка при сохранении: {str(e)}")

    st.markdown("---")

    # ============================================================================
    # ИСТОРИЯ ПОСЕВОВ
    # ============================================================================

    st.markdown("### 📜 История посевов")

    # Получение посевов
    sowing_operations = db.query(
        Operation.id,
        Operation.operation_date,
        Field.name.label('field_name'),
        Field.field_code,
        Operation.crop,
        Operation.variety,
        Operation.area_processed_ha,
        SowingDetail.seeding_rate_kg_ha,
        SowingDetail.seeding_depth_cm
    ).join(Field).outerjoin(SowingDetail).filter(
        Operation.operation_type == "sowing",
        Field.farm_id == farm.id  # КРИТИЧЕСКИЙ ФИЛЬТР: только операции текущего хозяйства
    ).order_by(Operation.operation_date.desc()).all()

    if sowing_operations:
        # Создание DataFrame
        df_sowing = pd.DataFrame(sowing_operations, columns=[
            'ID',
            'Дата',
            'Поле',
            'Код поля',
            'Культура',
            'Сорт',
            'Площадь (га)',
            'Норма высева (кг/га)',
            'Глубина (см)'
        ])

        # Форматирование
        df_sowing['Дата'] = pd.to_datetime(df_sowing['Дата']).dt.strftime('%Y-%m-%d')
        df_sowing = df_sowing.fillna('-')

        # Отображение
        st.dataframe(df_sowing, use_container_width=True, hide_index=True)

        # Статистика
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Всего посевов", len(sowing_operations))

        with col2:
            total_sown = sum([op.area_processed_ha for op in sowing_operations if op.area_processed_ha])
            st.metric("Засеяно всего", f"{total_sown:,.1f} га")

        with col3:
            unique_crops = len(set([op.crop for op in sowing_operations if op.crop]))
            st.metric("Культур", unique_crops)

        with col4:
            unique_fields = len(set([op.field_name for op in sowing_operations if op.field_name]))
            st.metric("Полей", unique_fields)

        # График по культурам
        if len(sowing_operations) > 0:
            crops_data = df_sowing[df_sowing['Культура'] != '-']['Культура'].value_counts()

            import plotly.express as px

            fig = px.pie(
                values=crops_data.values,
                names=crops_data.index,
                title='Распределение площадей по культурам',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("📭 История посевов пуста. Добавьте первый посев выше.")

finally:
    db.close()

# Sidebar
with st.sidebar:
    st.markdown("### ℹ️ Справка")
    st.info("""
    **Учет посева** позволяет регистрировать посевные работы с автоматическими подсказками.

    **Система автоматически:**
    - Подсказывает рекомендуемые параметры
    - Рассчитывает потребность в семенах
    - Показывает нормы NPK
    - Валидирует введенные данные

    **Обязательные поля:**
    - Поле
    - Дата посева
    - Культура и сорт
    - Норма высева
    - Глубина заделки
    """)

    st.markdown("### 📚 Справочник культур")
    st.markdown(f"Доступно **{len(crops_reference)}** культур:")
    for crop in list(crops_reference.keys())[:5]:
        st.markdown(f"- {crop}")
    if len(crops_reference) > 5:
        st.markdown(f"... и еще {len(crops_reference) - 5}")

    st.markdown("### 🎯 Рекомендации")
    st.markdown("""
    - Проводите посев в оптимальные сроки
    - Соблюдайте рекомендуемую норму высева
    - Учитывайте температуру и влажность почвы
    - Используйте качественный семенной материал
    """)
