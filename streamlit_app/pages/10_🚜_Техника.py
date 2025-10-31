"""
Equipment - Управление техникой и агрегатами
Добавление, редактирование, просмотр техники (тракторы, комбайны) и агрегатов (сеялки, культиваторы)
"""
import streamlit as st
import pandas as pd
import json
from pathlib import Path
from sqlalchemy.orm import Session
from modules.database import SessionLocal, Farm, Machinery, Implements
from modules.auth import (
    require_auth,
    require_farm_binding,
    filter_query_by_farm,
    get_user_display_name,
    can_edit_data,
    can_delete_data
)
from modules.validators import validator
from modules.config import settings
from datetime import datetime

# Настройка страницы
st.set_page_config(page_title="Техника", page_icon="🚜", layout="wide")

# Требуем авторизацию и привязку к хозяйству
require_auth()
require_farm_binding()

# Заголовок
st.title("🚜 Управление техникой и агрегатами")
st.caption(f"Пользователь: **{get_user_display_name()}**")

# Получение сессии БД
db = SessionLocal()

# Загрузка справочников техники
tractors_ref = {}
combines_ref = {}
implements_ref = {}

try:
    tractors_path = Path('data/tractors.json')
    if tractors_path.exists():
        with open(tractors_path, 'r', encoding='utf-8') as f:
            tractors_ref = json.load(f)
except Exception as e:
    st.warning(f"⚠️ Не удалось загрузить справочник тракторов: {e}")

try:
    combines_path = Path('data/combines.json')
    if combines_path.exists():
        with open(combines_path, 'r', encoding='utf-8') as f:
            combines_ref = json.load(f)
except Exception as e:
    st.warning(f"⚠️ Не удалось загрузить справочник комбайнов: {e}")

try:
    implements_path = Path('data/implements.json')
    if implements_path.exists():
        with open(implements_path, 'r', encoding='utf-8') as f:
            implements_ref = json.load(f)
except Exception as e:
    st.warning(f"⚠️ Не удалось загрузить справочник агрегатов: {e}")

try:
    # Проверка наличия хозяйства
    from modules.auth import get_current_user, is_admin
    user = get_current_user()

    if is_admin():
        farm = db.query(Farm).first()
    else:
        user_farm_id = user.get("farm_id") if user else None
        if user_farm_id:
            farm = db.query(Farm).filter(Farm.id == user_farm_id).first()
        else:
            farm = None

    if not farm:
        st.error("❌ Хозяйство не найдено. Обратитесь к администратору для привязки к хозяйству.")
        st.stop()

    # ============================================================================
    # ВКЛАДКИ ДЛЯ ТЕХНИКИ И АГРЕГАТОВ
    # ============================================================================

    tab1, tab2 = st.tabs(["🚜 Техника", "🔧 Агрегаты"])

    # ============================================================================
    # ВКЛАДКА 1: ТЕХНИКА (MACHINERY)
    # ============================================================================

    with tab1:
        st.markdown("### 🚜 Техника")
        st.caption("Тракторы, комбайны, самоходные опрыскиватели, самоходные косилки, дроны, системы орошения")

        # Список техники
        machinery_list = filter_query_by_farm(db.query(Machinery), Machinery).all()

        if machinery_list:
            # Pre-load all attributes to avoid DetachedInstanceError
            machinery_data = []
            active_count = 0
            total_value = 0
            total_power = 0

            for m in machinery_list:
                # Eagerly access all attributes while in session
                m_id = m.id
                m_type = m.machinery_type
                m_brand = m.brand
                m_model = m.model
                m_year = m.year
                m_reg = m.registration_number
                m_power = m.engine_power_hp
                m_fuel = m.fuel_type
                m_status = m.status
                m_value = m.current_value

                # Count for statistics
                if m_status == 'active':
                    active_count += 1
                if m_value:
                    total_value += m_value
                if m_power:
                    total_power += m_power

                machinery_data.append({
                    'ID': m_id,
                    'Тип': {
                    'tractor': 'Трактор',
                    'combine': 'Комбайн',
                    'self_propelled_sprayer': 'Самоходный опрыскиватель',
                    'self_propelled_mower': 'Самоходная косилка',
                    'drone': 'Дрон',
                    'irrigation_system': 'Система орошения',
                    'other': 'Другое'
                    }.get(m_type, m_type),
                    'Марка': m_brand or '-',
                    'Модель': m_model,
                    'Год': str(m_year) if m_year else '-',
                    'Рег. номер': m_reg or '-',
                    'Мощность (л.с.)': str(m_power) if m_power else '-',
                    'Топливо': m_fuel or '-',
                    'Статус': {
                        'active': '✅ Активна',
                        'maintenance': '🔧 Ремонт',
                        'inactive': '❌ Неактивна',
                        'sold': '💰 Продана'
                    }.get(m_status, m_status),
                    'Стоимость': f"{m_value:,.0f} тг" if m_value else '-'
                })

            df_machinery = pd.DataFrame(machinery_data)
            st.dataframe(df_machinery, width='stretch', hide_index=True)

            # Статистика
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Всего единиц", len(machinery_list))
            with col2:
                st.metric("Активных", active_count)
            with col3:
                st.metric("Общая стоимость", f"{total_value:,.0f} тг")
            with col4:
                st.metric("Общая мощность", f"{total_power:,.0f} л.с.")
        else:
            st.info("Техника не добавлена. Добавьте первую единицу техники ниже.")

        st.markdown("---")

        # ============================================================================
        # ФОРМА ДОБАВЛЕНИЯ/РЕДАКТИРОВАНИЯ ТЕХНИКИ
        # ============================================================================

        st.markdown("### ➕ Добавить технику")

        # Режим добавления
        add_mode = st.radio(
            "Режим добавления",
            options=["Из справочника", "Вручную"],
            horizontal=True,
            help="Выберите модель из справочника для автозаполнения или введите данные вручную"
        )

        # Выбор типа техники (вне формы для динамического обновления)
        machinery_type = st.selectbox(
            "Тип техники *",
            options=['tractor', 'combine', 'self_propelled_sprayer', 'self_propelled_mower', 'drone', 'irrigation_system', 'other'],
            format_func=lambda x: {
                'tractor': 'Трактор',
                'combine': 'Комбайн',
                'self_propelled_sprayer': 'Самоходный опрыскиватель',
                'self_propelled_mower': 'Самоходная косилка',
                'drone': 'Дрон',
                'irrigation_system': 'Система орошения',
                'other': 'Другое'
            }[x],
            key="machinery_type_select"
        )

        # Автозаполнение из справочника (вне формы для динамического обновления)
        selected_ref_model = None
        ref_data = None

        if add_mode == "Из справочника":
            if machinery_type == 'tractor' and tractors_ref:
                st.markdown("**📚 Выбор из справочника тракторов**")

                col_ref1, col_ref2 = st.columns(2)

                with col_ref1:
                    # Выбор производителя
                    brands = sorted(set(v['производитель'] for v in tractors_ref.values()))
                    selected_brand = st.selectbox("Производитель", brands, key="tractor_brand")

                with col_ref2:
                    # Фильтрация моделей по производителю
                    filtered_models = {k: v for k, v in tractors_ref.items() if v['производитель'] == selected_brand}

                    if filtered_models:
                        selected_ref_model = st.selectbox("Модель из справочника", list(filtered_models.keys()), key="tractor_model")
                        ref_data = filtered_models[selected_ref_model]

                # Показать характеристики
                if ref_data:
                    st.success(f"💪 Мощность: {ref_data['мощность_лс']} л.с. | "
                               f"🏷️ Класс: {ref_data['класс']} | "
                               f"🚜 Тип: {ref_data['тип']}")

            elif machinery_type == 'combine' and combines_ref:
                st.markdown("**📚 Выбор из справочника комбайнов**")

                col_ref1, col_ref2 = st.columns(2)

                with col_ref1:
                    # Выбор производителя
                    brands = sorted(set(v['производитель'] for v in combines_ref.values()))
                    selected_brand = st.selectbox("Производитель", brands, key="combine_brand")

                with col_ref2:
                    # Фильтрация моделей по производителю
                    filtered_models = {k: v for k, v in combines_ref.items() if v['производитель'] == selected_brand}

                    if filtered_models:
                        selected_ref_model = st.selectbox("Модель из справочника", list(filtered_models.keys()), key="combine_model")
                        ref_data = filtered_models[selected_ref_model]

                # Показать характеристики
                if ref_data:
                    st.success(f"💪 Мощность: {ref_data['мощность_лс']} л.с. | "
                               f"🏷️ Класс: {ref_data['класс']} | "
                               f"⚙️ Молотилка: {ref_data['молотильный_аппарат']}")
            else:
                st.info("💡 Справочник недоступен для этого типа техники. Используйте ручной ввод ниже.")

        st.markdown("---")

        # ФОРМА (данные предзаполнены из выбора выше)
        with st.form("add_machinery_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                # Поля для ручного ввода или переопределения
                if ref_data:
                    brand = st.text_input("Марка", value=ref_data['производитель'], disabled=True)
                    model = st.text_input("Модель *", value=ref_data['модель'], disabled=True)
                    engine_power_hp_default = float(ref_data['мощность_лс'])
                else:
                    brand = st.text_input("Марка", placeholder="Например: John Deere, Case IH, МТЗ")
                    model = st.text_input("Модель *", placeholder="Например: 8R 370, Axial-Flow 9250")
                    engine_power_hp_default = None

                year = st.number_input("Год выпуска", min_value=1950, max_value=datetime.now().year, value=None, step=1)
                registration_number = st.text_input("Регистрационный номер", placeholder="Например: А123ВС 01")

            with col2:
                engine_power_hp = st.number_input(
                    "Мощность двигателя (л.с.)",
                    min_value=0.0,
                    value=engine_power_hp_default,
                    step=10.0
                )

                # Автозаполнение топлива
                fuel_default_index = 0 if ref_data and ref_data.get('топливо') == 'Дизель' else None

                fuel_type = st.selectbox(
                    "Тип топлива",
                    options=['diesel', 'gasoline', 'electric', 'hybrid', 'gas', 'other'],
                    format_func=lambda x: {
                        'diesel': 'Дизель',
                        'gasoline': 'Бензин',
                        'electric': 'Электро',
                        'hybrid': 'Гибрид',
                        'gas': 'Газ',
                        'other': 'Другое'
                    }.get(x, x),
                    index=fuel_default_index
                )

                purchase_date = st.date_input("Дата покупки", value=None)
                purchase_price = st.number_input("Цена покупки (тенге)", min_value=0.0, value=None, step=100000.0)
                current_value = st.number_input("Текущая стоимость (тенге)", min_value=0.0, value=None, step=100000.0)

                status = st.selectbox(
                    "Статус",
                    options=['active', 'maintenance', 'inactive', 'sold'],
                    format_func=lambda x: {
                        'active': '✅ Активна',
                        'maintenance': '🔧 На ремонте',
                        'inactive': '❌ Неактивна',
                        'sold': '💰 Продана'
                    }[x]
                )

            notes = st.text_area("Примечания", placeholder="Дополнительная информация о технике")

            submitted = st.form_submit_button("✅ Добавить технику", use_container_width=True, type="primary")

            if submitted:
                if not model:
                    st.error("❌ Укажите модель техники")
                elif not can_edit_data():
                    st.error("❌ У вас нет прав на добавление данных")
                else:
                    try:
                        new_machinery = Machinery(
                            farm_id=farm.id,
                            machinery_type=machinery_type,
                            brand=brand if brand else None,
                            model=model,
                            year=year if year else None,
                            registration_number=registration_number if registration_number else None,
                            engine_power_hp=engine_power_hp if engine_power_hp else None,
                            fuel_type=fuel_type if fuel_type else None,
                            purchase_date=purchase_date if purchase_date else None,
                            purchase_price=purchase_price if purchase_price else None,
                            current_value=current_value if current_value else None,
                            status=status,
                            notes=notes if notes else None
                        )

                        db.add(new_machinery)
                        db.commit()

                        st.success(f"✅ Техника {brand} {model} успешно добавлена!")
                        st.rerun()
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ Ошибка при добавлении техники: {e}")

        st.markdown("---")

        # ============================================================================
        # УДАЛЕНИЕ ТЕХНИКИ
        # ============================================================================

        if machinery_list and can_delete_data():
            st.markdown("### 🗑️ Удалить технику")

            # Pre-load attributes for delete selectbox
            machinery_delete_options = {}
            for m in machinery_list:
                display = f"{m.brand or ''} {m.model} ({m.year or '-'}) - {m.registration_number or 'без номера'}"
                machinery_delete_options[display] = m.id

            selected_machinery_to_delete = st.selectbox(
                "Выберите технику для удаления",
                options=list(machinery_delete_options.keys()),
                key="delete_machinery_select"
            )

            if st.button("🗑️ Удалить выбранную технику", type="secondary"):
                try:
                    machinery_id_to_delete = machinery_delete_options[selected_machinery_to_delete]
                    machinery_obj = db.query(Machinery).filter(Machinery.id == machinery_id_to_delete).first()
                    if machinery_obj:
                        db.delete(machinery_obj)
                        db.commit()
                        st.success("✅ Техника удалена")
                        st.rerun()
                    else:
                        st.error("❌ Техника не найдена")
                except Exception as e:
                    db.rollback()
                    st.error(f"❌ Ошибка при удалении: {e}")

    # ============================================================================
    # ВКЛАДКА 2: АГРЕГАТЫ (IMPLEMENTS)
    # ============================================================================

    with tab2:
        st.markdown("### 🔧 Агрегаты")
        st.caption("Сеялки, плуги, культиваторы, бороны, прицепные опрыскиватели и другие навесные орудия")

        # Список агрегатов
        implements_list = filter_query_by_farm(db.query(Implements), Implements).all()

        if implements_list:
            # Pre-load all attributes to avoid DetachedInstanceError
            implements_data = []
            active_impl_count = 0
            total_impl_value = 0

            for impl in implements_list:
                # Eagerly access all attributes while in session
                impl_id = impl.id
                impl_type = impl.implement_type
                impl_brand = impl.brand
                impl_model = impl.model
                impl_year = impl.year
                impl_width = impl.working_width_m
                impl_status = impl.status
                impl_value = impl.current_value

                # Count for statistics
                if impl_status == 'active':
                    active_impl_count += 1
                if impl_value:
                    total_impl_value += impl_value

                implements_data.append({
                    'ID': impl_id,
                    'Тип': {
                        'seeder': 'Сеялка',
                        'planter': 'Сажалка',
                        'plow': 'Плуг',
                        'cultivator': 'Культиватор',
                        'harrow': 'Борона',
                        'disc': 'Дисковая борона',
                        'deep_loosener': 'Глубокорыхлитель',
                        'roller': 'Каток',
                        'sprayer_trailer': 'Прицепной опрыскиватель',
                        'fertilizer_spreader': 'Разбрасыватель удобрений',
                        'stubble_breaker': 'Стерневая борона',
                        'snow_plow': 'Снегозадержатель',
                        'header': 'Жатка',
                        'mower': 'Косилка',
                        'baler': 'Пресс-подборщик',
                        'other': 'Другое'
                    }.get(impl_type, impl_type),
                    'Марка': impl_brand or '-',
                    'Модель': impl_model,
                    'Год': str(impl_year) if impl_year else '-',
                    'Ширина захвата (м)': str(impl_width) if impl_width else '-',
                    'Статус': {
                        'active': '✅ Активен',
                        'maintenance': '🔧 Ремонт',
                        'inactive': '❌ Неактивен',
                        'sold': '💰 Продан'
                    }.get(impl_status, impl_status),
                    'Стоимость': f"{impl_value:,.0f} тг" if impl_value else '-'
                })

            df_implements = pd.DataFrame(implements_data)
            st.dataframe(df_implements, width='stretch', hide_index=True)

            # Статистика
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Всего единиц", len(implements_list))
            with col2:
                st.metric("Активных", active_impl_count)
            with col3:
                st.metric("Общая стоимость", f"{total_impl_value:,.0f} тг")
        else:
            st.info("Агрегаты не добавлены. Добавьте первый агрегат ниже.")

        st.markdown("---")

        # ============================================================================
        # ФОРМА ДОБАВЛЕНИЯ/РЕДАКТИРОВАНИЯ АГРЕГАТОВ
        # ============================================================================

        st.markdown("### ➕ Добавить агрегат")

        # Режим добавления
        add_impl_mode = st.radio(
            "Режим добавления",
            options=["Из справочника", "Вручную"],
            horizontal=True,
            help="Выберите модель из справочника для автозаполнения или введите данные вручную",
            key="impl_add_mode"
        )

        # Выбор типа агрегата (вне формы для динамического обновления)
        implement_type = st.selectbox(
            "Тип агрегата *",
            options=['seeder', 'planter', 'plow', 'cultivator', 'harrow', 'disc',
                    'deep_loosener', 'roller', 'sprayer_trailer', 'fertilizer_spreader',
                    'stubble_breaker', 'snow_plow', 'header', 'mower', 'baler', 'other'],
            format_func=lambda x: {
                'seeder': 'Сеялка',
                'planter': 'Сажалка',
                'plow': 'Плуг',
                'cultivator': 'Культиватор',
                'harrow': 'Борона',
                'disc': 'Дисковая борона',
                'deep_loosener': 'Глубокорыхлитель',
                'roller': 'Каток',
                'sprayer_trailer': 'Прицепной опрыскиватель',
                'fertilizer_spreader': 'Разбрасыватель удобрений',
                'stubble_breaker': 'Стерневая борона',
                'snow_plow': 'Снегозадержатель',
                'header': 'Жатка',
                'mower': 'Косилка',
                'baler': 'Пресс-подборщик',
                'other': 'Другое'
            }[x],
            key="implement_type_select"
        )

        # Автозаполнение из справочника (вне формы для динамического обновления)
        selected_impl_ref_model = None
        impl_ref_data = None

        if add_impl_mode == "Из справочника" and implements_ref:
            # Фильтрация по типу оборудования
            filtered_by_type = {k: v for k, v in implements_ref.items() if v.get('тип_оборудования') == implement_type}

            if filtered_by_type:
                st.markdown("**📚 Выбор из справочника агрегатов**")

                col_ref1, col_ref2 = st.columns(2)

                with col_ref1:
                    # Выбор производителя
                    brands = sorted(set(v['производитель'] for v in filtered_by_type.values()))
                    selected_impl_brand = st.selectbox("Производитель", brands, key="impl_brand_ref")

                with col_ref2:
                    # Фильтрация моделей по производителю
                    filtered_models = {k: v for k, v in filtered_by_type.items() if v['производитель'] == selected_impl_brand}

                    if filtered_models:
                        selected_impl_ref_model = st.selectbox("Модель из справочника", list(filtered_models.keys()), key="impl_model_ref")
                        impl_ref_data = filtered_models[selected_impl_ref_model]

                # Показать характеристики
                if impl_ref_data:
                    # Формируем строку характеристик в зависимости от типа
                    specs = []
                    if 'ширина_захвата_м' in impl_ref_data and impl_ref_data['ширина_захвата_м']:
                        specs.append(f"📏 Ширина: {impl_ref_data['ширина_захвата_м']} м")
                    if 'категория' in impl_ref_data:
                        specs.append(f"🏷️ {impl_ref_data['категория']}")
                    if 'тип' in impl_ref_data:
                        specs.append(f"⚙️ {impl_ref_data['тип']}")
                    if 'применение' in impl_ref_data:
                        specs.append(f"🌾 {impl_ref_data['применение']}")

                    if specs:
                        st.success(" | ".join(specs))
            else:
                st.info("💡 Справочник недоступен для этого типа агрегата. Используйте ручной ввод ниже.")
        elif add_impl_mode == "Из справочника":
            st.info("💡 Справочник агрегатов не загружен. Используйте ручной ввод ниже.")

        st.markdown("---")

        # ФОРМА (данные предзаполнены из выбора выше)
        with st.form("add_implement_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                # Поля для ручного ввода или переопределения
                if impl_ref_data:
                    impl_brand = st.text_input("Марка", value=impl_ref_data['производитель'], disabled=True)
                    impl_model = st.text_input("Модель *", value=impl_ref_data['модель'], disabled=True)

                    # Попытка извлечь ширину захвата
                    width_str = str(impl_ref_data.get('ширина_захвата_м', ''))
                    try:
                        # Если диапазон, берем первое значение
                        if '-' in width_str:
                            working_width_default = float(width_str.split('-')[0])
                        elif 'рядов' in width_str or 'ряд' in width_str:
                            # Для кукурузных жаток и т.д. - просто None
                            working_width_default = None
                        else:
                            working_width_default = float(width_str)
                    except:
                        working_width_default = None
                else:
                    impl_brand = st.text_input("Марка", placeholder="Например: Amazone, Horsch, БДТ")
                    impl_model = st.text_input("Модель *", placeholder="Например: Cirrus 6003, Pronto 9 DC")
                    working_width_default = None

                impl_year = st.number_input("Год выпуска", min_value=1950, max_value=datetime.now().year, value=None, step=1, key="impl_year")
                working_width_m = st.number_input("Ширина захвата (м)", min_value=0.0, value=working_width_default, step=0.5)

            with col2:
                impl_purchase_date = st.date_input("Дата покупки", value=None, key="impl_purchase_date")
                impl_purchase_price = st.number_input("Цена покупки (тенге)", min_value=0.0, value=None, step=50000.0, key="impl_purchase_price")
                impl_current_value = st.number_input("Текущая стоимость (тенге)", min_value=0.0, value=None, step=50000.0, key="impl_current_value")

                impl_status = st.selectbox(
                    "Статус",
                    options=['active', 'maintenance', 'inactive', 'sold'],
                    format_func=lambda x: {
                        'active': '✅ Активен',
                        'maintenance': '🔧 На ремонте',
                        'inactive': '❌ Неактивен',
                        'sold': '💰 Продан'
                    }[x],
                    key="impl_status"
                )

            impl_notes = st.text_area("Примечания", placeholder="Дополнительная информация об агрегате", key="impl_notes")

            impl_submitted = st.form_submit_button("✅ Добавить агрегат", use_container_width=True, type="primary")

            if impl_submitted:
                if not impl_model:
                    st.error("❌ Укажите модель агрегата")
                elif not can_edit_data():
                    st.error("❌ У вас нет прав на добавление данных")
                else:
                    try:
                        new_implement = Implements(
                            farm_id=farm.id,
                            implement_type=implement_type,
                            brand=impl_brand if impl_brand else None,
                            model=impl_model,
                            year=impl_year if impl_year else None,
                            working_width_m=working_width_m if working_width_m else None,
                            purchase_date=impl_purchase_date if impl_purchase_date else None,
                            purchase_price=impl_purchase_price if impl_purchase_price else None,
                            current_value=impl_current_value if impl_current_value else None,
                            status=impl_status,
                            notes=impl_notes if impl_notes else None
                        )

                        db.add(new_implement)
                        db.commit()

                        st.success(f"✅ Агрегат {impl_brand} {impl_model} успешно добавлен!")
                        st.rerun()
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ Ошибка при добавлении агрегата: {e}")

        st.markdown("---")

        # ============================================================================
        # УДАЛЕНИЕ АГРЕГАТОВ
        # ============================================================================

        if implements_list and can_delete_data():
            st.markdown("### 🗑️ Удалить агрегат")

            # Pre-load attributes for delete selectbox
            implement_delete_options = {}
            for i in implements_list:
                display = f"{i.brand or ''} {i.model} ({i.year or '-'}) - {i.working_width_m or '-'}м"
                implement_delete_options[display] = i.id

            selected_implement_to_delete = st.selectbox(
                "Выберите агрегат для удаления",
                options=list(implement_delete_options.keys()),
                key="delete_implement_select"
            )

            if st.button("🗑️ Удалить выбранный агрегат", type="secondary"):
                try:
                    implement_id_to_delete = implement_delete_options[selected_implement_to_delete]
                    implement_obj = db.query(Implements).filter(Implements.id == implement_id_to_delete).first()
                    if implement_obj:
                        db.delete(implement_obj)
                        db.commit()
                        st.success("✅ Агрегат удалён")
                        st.rerun()
                    else:
                        st.error("❌ Агрегат не найден")
                except Exception as e:
                    db.rollback()
                    st.error(f"❌ Ошибка при удалении: {e}")

finally:
    db.close()
