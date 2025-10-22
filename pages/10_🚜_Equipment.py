"""
Equipment - Управление техникой и агрегатами
Добавление, редактирование, просмотр техники (тракторы, комбайны) и агрегатов (сеялки, культиваторы)
"""
import streamlit as st
import pandas as pd
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
        st.caption("Тракторы, комбайны, самоходные опрыскиватели, дроны, системы орошения")

        # Список техники
        machinery_list = filter_query_by_farm(db.query(Machinery), Machinery).all()

        if machinery_list:
            # Создание DataFrame
            machinery_data = []
            for m in machinery_list:
                machinery_data.append({
                    'ID': m.id,
                    'Тип': {
                        'tractor': 'Трактор',
                        'combine': 'Комбайн',
                        'self_propelled_sprayer': 'Самоходный опрыскиватель',
                        'drone': 'Дрон',
                        'irrigation_system': 'Система орошения',
                        'other': 'Другое'
                    }.get(m.machinery_type, m.machinery_type),
                    'Марка': m.brand or '-',
                    'Модель': m.model,
                    'Год': m.year or '-',
                    'Рег. номер': m.registration_number or '-',
                    'Мощность (л.с.)': m.engine_power_hp or '-',
                    'Топливо': m.fuel_type or '-',
                    'Статус': {
                        'active': '✅ Активна',
                        'maintenance': '🔧 Ремонт',
                        'inactive': '❌ Неактивна',
                        'sold': '💰 Продана'
                    }.get(m.status, m.status),
                    'Стоимость': f"{m.current_value:,.0f} тг" if m.current_value else '-'
                })

            df_machinery = pd.DataFrame(machinery_data)
            st.dataframe(df_machinery, use_container_width=True, hide_index=True)

            # Статистика
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Всего единиц", len(machinery_list))
            with col2:
                active_count = len([m for m in machinery_list if m.status == 'active'])
                st.metric("Активных", active_count)
            with col3:
                total_value = sum([m.current_value for m in machinery_list if m.current_value])
                st.metric("Общая стоимость", f"{total_value:,.0f} тг")
            with col4:
                total_power = sum([m.engine_power_hp for m in machinery_list if m.engine_power_hp])
                st.metric("Общая мощность", f"{total_power:,.0f} л.с.")
        else:
            st.info("Техника не добавлена. Добавьте первую единицу техники ниже.")

        st.markdown("---")

        # ============================================================================
        # ФОРМА ДОБАВЛЕНИЯ/РЕДАКТИРОВАНИЯ ТЕХНИКИ
        # ============================================================================

        st.markdown("### ➕ Добавить технику")

        with st.form("add_machinery_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                machinery_type = st.selectbox(
                    "Тип техники *",
                    options=['tractor', 'combine', 'self_propelled_sprayer', 'drone', 'irrigation_system', 'other'],
                    format_func=lambda x: {
                        'tractor': 'Трактор',
                        'combine': 'Комбайн',
                        'self_propelled_sprayer': 'Самоходный опрыскиватель',
                        'drone': 'Дрон',
                        'irrigation_system': 'Система орошения',
                        'other': 'Другое'
                    }[x]
                )

                brand = st.text_input("Марка", placeholder="Например: John Deere, Case IH, МТЗ")
                model = st.text_input("Модель *", placeholder="Например: 8R 370, Axial-Flow 9250")
                year = st.number_input("Год выпуска", min_value=1950, max_value=datetime.now().year, value=None, step=1)
                registration_number = st.text_input("Регистрационный номер", placeholder="Например: А123ВС 01")

            with col2:
                engine_power_hp = st.number_input("Мощность двигателя (л.с.)", min_value=0.0, value=None, step=10.0)
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
                    index=None
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

            machinery_to_delete = st.selectbox(
                "Выберите технику для удаления",
                options=machinery_list,
                format_func=lambda m: f"{m.brand or ''} {m.model} ({m.year or '-'}) - {m.registration_number or 'без номера'}"
            )

            if st.button("🗑️ Удалить выбранную технику", type="secondary"):
                try:
                    db.delete(machinery_to_delete)
                    db.commit()
                    st.success("✅ Техника удалена")
                    st.rerun()
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
            # Создание DataFrame
            implements_data = []
            for impl in implements_list:
                implements_data.append({
                    'ID': impl.id,
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
                        'other': 'Другое'
                    }.get(impl.implement_type, impl.implement_type),
                    'Марка': impl.brand or '-',
                    'Модель': impl.model,
                    'Год': impl.year or '-',
                    'Ширина захвата (м)': impl.working_width_m or '-',
                    'Статус': {
                        'active': '✅ Активен',
                        'maintenance': '🔧 Ремонт',
                        'inactive': '❌ Неактивен',
                        'sold': '💰 Продан'
                    }.get(impl.status, impl.status),
                    'Стоимость': f"{impl.current_value:,.0f} тг" if impl.current_value else '-'
                })

            df_implements = pd.DataFrame(implements_data)
            st.dataframe(df_implements, use_container_width=True, hide_index=True)

            # Статистика
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Всего единиц", len(implements_list))
            with col2:
                active_count = len([i for i in implements_list if i.status == 'active'])
                st.metric("Активных", active_count)
            with col3:
                total_value = sum([i.current_value for i in implements_list if i.current_value])
                st.metric("Общая стоимость", f"{total_value:,.0f} тг")
        else:
            st.info("Агрегаты не добавлены. Добавьте первый агрегат ниже.")

        st.markdown("---")

        # ============================================================================
        # ФОРМА ДОБАВЛЕНИЯ/РЕДАКТИРОВАНИЯ АГРЕГАТОВ
        # ============================================================================

        st.markdown("### ➕ Добавить агрегат")

        with st.form("add_implement_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                implement_type = st.selectbox(
                    "Тип агрегата *",
                    options=['seeder', 'planter', 'plow', 'cultivator', 'harrow', 'disc',
                            'deep_loosener', 'roller', 'sprayer_trailer', 'fertilizer_spreader',
                            'stubble_breaker', 'snow_plow', 'other'],
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
                        'other': 'Другое'
                    }[x]
                )

                impl_brand = st.text_input("Марка", placeholder="Например: Amazone, Horsch, БДТ")
                impl_model = st.text_input("Модель *", placeholder="Например: Cirrus 6003, Pronto 9 DC")
                impl_year = st.number_input("Год выпуска", min_value=1950, max_value=datetime.now().year, value=None, step=1, key="impl_year")
                working_width_m = st.number_input("Ширина захвата (м)", min_value=0.0, value=None, step=0.5)

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

            implement_to_delete = st.selectbox(
                "Выберите агрегат для удаления",
                options=implements_list,
                format_func=lambda i: f"{i.brand or ''} {i.model} ({i.year or '-'}) - {i.working_width_m or '-'}м"
            )

            if st.button("🗑️ Удалить выбранный агрегат", type="secondary"):
                try:
                    db.delete(implement_to_delete)
                    db.commit()
                    st.success("✅ Агрегат удалён")
                    st.rerun()
                except Exception as e:
                    db.rollback()
                    st.error(f"❌ Ошибка при удалении: {e}")

finally:
    db.close()
