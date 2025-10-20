"""
Farm Setup - Регистрация хозяйства
"""
import streamlit as st
from datetime import date
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from modules.database import get_db, Farm, User
from modules.validators import DataValidator
from modules.auth import (
    require_auth,
    filter_query_by_farm,
    get_current_user,
    get_user_display_name,
    can_edit_data,
    can_delete_data,
    is_admin
)

# Настройка страницы
st.set_page_config(page_title="Регистрация хозяйства", page_icon="🏢", layout="wide")

# Требуем авторизацию
require_auth()

st.title("🏢 Регистрация хозяйства")
st.caption(f"Пользователь: **{get_user_display_name()}**")

# Инициализация
validator = DataValidator()
db = next(get_db())

# Получение хозяйства с учетом прав доступа
user = get_current_user()
if is_admin():
    # Админ может выбирать хозяйства
    all_farms = db.query(Farm).all()
    if all_farms:
        farm_names = {f.name: f.id for f in all_farms}
        # По умолчанию выбираем первое хозяйство, а не "Создать новое"
        selected_farm_name = st.selectbox(
            "Выберите хозяйство для просмотра/редактирования",
            options=list(farm_names.keys()) + ["Создать новое"],
            index=0  # Первое хозяйство по умолчанию
        )

        if selected_farm_name == "Создать новое":
            existing_farm = None
        else:
            existing_farm = db.query(Farm).filter(Farm.id == farm_names[selected_farm_name]).first()
    else:
        existing_farm = None
else:
    # Фермер видит только свое хозяйство
    existing_farm = filter_query_by_farm(db.query(Farm), Farm).first()

if existing_farm:
    st.success(f"✅ Хозяйство уже зарегистрировано: **{existing_farm.name}**")

    st.markdown("---")
    st.markdown("### 📋 Информация о хозяйстве")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        **Основная информация:**
        - **БИН:** {existing_farm.bin}
        - **Название:** {existing_farm.name}
        - **Руководитель:** {existing_farm.director_name or "-"}
        - **Регион:** {existing_farm.region or "-"}
        - **Район:** {existing_farm.district or "-"}
        """)

    with col2:
        st.markdown(f"""
        **Контактные данные:**
        - **Телефон:** {existing_farm.phone or "-"}
        - **Email:** {existing_farm.email or "-"}
        - **Адрес:** {existing_farm.address or "-"}
        """)

    st.markdown(f"""
    **Земельные ресурсы:**
    - **Всего земель:** {existing_farm.total_area_ha or 0:.2f} га
    - **Пашня:** {existing_farm.arable_area_ha or 0:.2f} га
    - **Залежь:** {existing_farm.fallow_area_ha or 0:.2f} га
    - **Пастбища:** {existing_farm.pasture_area_ha or 0:.2f} га
    - **Сенокосы:** {existing_farm.hayfield_area_ha or 0:.2f} га
    """)

    st.markdown("---")

    # Кнопка редактирования (доступна для админов и фермеров)
    if can_edit_data():
        if st.button("✏️ Редактировать данные хозяйства"):
            st.session_state.edit_mode = True
    else:
        st.info("ℹ️ У вас нет прав на редактирование данных хозяйства")

    # Кнопка удаления (только для админов)
    if can_delete_data():
        with st.expander("⚠️ Удалить хозяйство (опасно!)"):
            st.warning("Это действие удалит ВСЕ данные хозяйства, включая поля и операции!")
            confirm_delete = st.text_input("Введите БИН хозяйства для подтверждения удаления:")

            if st.button("🗑️ Удалить хозяйство", type="secondary"):
                if confirm_delete == existing_farm.bin:
                    try:
                        db.delete(existing_farm)
                        db.commit()
                        st.success("✅ Хозяйство удалено!")
                        st.rerun()
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ Ошибка при удалении: {str(e)}")
                else:
                    st.error("❌ БИН не совпадает!")

else:
    if can_edit_data():
        st.info("ℹ️ Хозяйство еще не зарегистрировано. Заполните форму ниже или импортируйте данные из Excel.")
        st.session_state.edit_mode = True
    else:
        st.warning("⚠️ У вас нет прав на создание хозяйства. Обратитесь к администратору.")

# Форма регистрации/редактирования (только для админов и фермеров)
if can_edit_data() and (not existing_farm or st.session_state.get('edit_mode', False)):

    st.markdown("---")
    st.markdown("### 📝 Форма регистрации")

    with st.form("farm_registration_form"):
        st.markdown("#### 1️⃣ Идентификация")

        col1, col2 = st.columns(2)

        with col1:
            bin_number = st.text_input(
                "БИН (ИИН) *",
                value=existing_farm.bin if existing_farm else "",
                max_chars=12,
                help="12-значный БИН или ИИН хозяйства"
            )

            farm_name = st.text_input(
                "Название хозяйства *",
                value=existing_farm.name if existing_farm else "",
                help="Полное название фермерского хозяйства"
            )

            director_name = st.text_input(
                "ФИО руководителя *",
                value=existing_farm.director_name if existing_farm else "",
                help="Фамилия Имя Отчество руководителя"
            )

        with col2:
            region = st.selectbox(
                "Область *",
                options=["Акмолинская", "Алматинская", "Актюбинская", "Атырауская",
                        "Восточно-Казахстанская", "Жамбылская", "Западно-Казахстанская",
                        "Карагандинская", "Костанайская", "Кызылординская", "Мангистауская",
                        "Павлодарская", "Северо-Казахстанская", "Туркестанская", "Улытауская"],
                index=0 if not existing_farm else ["Акмолинская", "Алматинская", "Актюбинская", "Атырауская",
                        "Восточно-Казахстанская", "Жамбылская", "Западно-Казахстанская",
                        "Карагандинская", "Костанайская", "Кызылординская", "Мангистауская",
                        "Павлодарская", "Северо-Казахстанская", "Туркестанская", "Улытауская"].index(existing_farm.region) if existing_farm.region else 0,
                help="Область Казахстана"
            )

            district = st.text_input(
                "Район",
                value=existing_farm.district if existing_farm else "",
                help="Район области"
            )

            village = st.text_input(
                "Населенный пункт",
                value=existing_farm.village if existing_farm else "",
                help="Село/поселок"
            )

        st.markdown("---")
        st.markdown("#### 2️⃣ Контактные данные")

        col3, col4 = st.columns(2)

        with col3:
            phone = st.text_input(
                "Телефон *",
                value=existing_farm.phone if existing_farm else "",
                placeholder="+7 (7xx) xxx-xx-xx",
                help="Контактный телефон"
            )

            email = st.text_input(
                "Email",
                value=existing_farm.email if existing_farm else "",
                placeholder="example@mail.ru",
                help="Электронная почта"
            )

        with col4:
            address = st.text_area(
                "Юридический адрес",
                value=existing_farm.address if existing_farm else "",
                height=100,
                help="Полный юридический адрес"
            )

        st.markdown("---")
        st.markdown("#### 3️⃣ Земельные ресурсы")

        col5, col6 = st.columns(2)

        with col5:
            total_area = st.number_input(
                "Общая площадь земель (га) *",
                min_value=0.0,
                max_value=500000.0,
                value=float(existing_farm.total_area_ha) if existing_farm and existing_farm.total_area_ha else 0.0,
                step=10.0,
                help="Общая площадь земельных ресурсов"
            )

            arable_area = st.number_input(
                "Пашня (га) *",
                min_value=0.0,
                max_value=total_area,
                value=float(existing_farm.arable_area_ha) if existing_farm and existing_farm.arable_area_ha else 0.0,
                step=10.0,
                help="Площадь пахотных земель"
            )

            fallow_area = st.number_input(
                "Залежь (га)",
                min_value=0.0,
                max_value=total_area,
                value=float(existing_farm.fallow_area_ha) if existing_farm and existing_farm.fallow_area_ha else 0.0,
                step=10.0,
                help="Площадь залежных земель"
            )

        with col6:
            pasture_area = st.number_input(
                "Пастбища (га)",
                min_value=0.0,
                max_value=total_area,
                value=float(existing_farm.pasture_area_ha) if existing_farm and existing_farm.pasture_area_ha else 0.0,
                step=10.0,
                help="Площадь пастбищ"
            )

            hayfield_area = st.number_input(
                "Сенокосы (га)",
                min_value=0.0,
                max_value=total_area,
                value=float(existing_farm.hayfield_area_ha) if existing_farm and existing_farm.hayfield_area_ha else 0.0,
                step=10.0,
                help="Площадь сенокосных угодий"
            )

        # Проверка суммы площадей
        sum_areas = arable_area + fallow_area + pasture_area + hayfield_area
        if sum_areas > total_area:
            st.warning(f"⚠️ Сумма площадей ({sum_areas:.2f} га) превышает общую площадь ({total_area:.2f} га)")

        st.markdown("---")

        # Кнопка отправки
        submitted = st.form_submit_button(
            "✅ Сохранить хозяйство" if existing_farm else "✅ Зарегистрировать хозяйство",
            use_container_width=True,
            type="primary"
        )

        if submitted:
            # Валидация
            errors = []

            # Проверка БИН
            is_valid, msg = validator.validate_bin(bin_number)
            if not is_valid:
                errors.append(f"БИН: {msg}")

            # Проверка на уникальность БИН (только для новых хозяйств или при изменении БИН)
            if not existing_farm or (existing_farm and existing_farm.bin != bin_number):
                bin_exists = db.query(Farm).filter(Farm.bin == bin_number).first()
                if bin_exists:
                    errors.append(f"Хозяйство с БИН {bin_number} уже зарегистрировано в системе")

            # Проверка названия
            if not farm_name or len(farm_name) < 3:
                errors.append("Название хозяйства должно содержать минимум 3 символа")

            # Проверка руководителя
            if not director_name or len(director_name) < 5:
                errors.append("ФИО руководителя должно содержать минимум 5 символов")

            # Проверка телефона
            is_valid, msg = validator.validate_phone(phone)
            if not is_valid:
                errors.append(f"Телефон: {msg}")

            # Проверка email (если указан)
            if email:
                is_valid, msg = validator.validate_email(email)
                if not is_valid:
                    errors.append(f"Email: {msg}")

            # Проверка площадей
            if total_area <= 0:
                errors.append("Общая площадь должна быть больше 0")

            if arable_area <= 0:
                errors.append("Площадь пашни должна быть больше 0")

            if sum_areas > total_area:
                errors.append(f"Сумма площадей ({sum_areas:.2f} га) превышает общую площадь ({total_area:.2f} га)")

            if errors:
                st.error("❌ Ошибки валидации:\n" + "\n".join(f"- {e}" for e in errors))
            else:
                try:
                    if existing_farm:
                        # Обновление существующего хозяйства
                        existing_farm.bin = bin_number
                        existing_farm.name = farm_name
                        existing_farm.director_name = director_name
                        existing_farm.region = region
                        existing_farm.district = district if district else None
                        existing_farm.village = village if village else None
                        existing_farm.phone = phone
                        existing_farm.email = email if email else None
                        existing_farm.address = address if address else None
                        existing_farm.total_area_ha = total_area
                        existing_farm.arable_area_ha = arable_area
                        existing_farm.fallow_area_ha = fallow_area if fallow_area > 0 else None
                        existing_farm.pasture_area_ha = pasture_area if pasture_area > 0 else None
                        existing_farm.hayfield_area_ha = hayfield_area if hayfield_area > 0 else None

                        db.commit()
                        st.success("✅ Данные хозяйства обновлены!")
                    else:
                        # Создание нового хозяйства
                        new_farm = Farm(
                            bin=bin_number,
                            name=farm_name,
                            director_name=director_name,
                            region=region,
                            district=district if district else None,
                            village=village if village else None,
                            phone=phone,
                            email=email if email else None,
                            address=address if address else None,
                            total_area_ha=total_area,
                            arable_area_ha=arable_area,
                            fallow_area_ha=fallow_area if fallow_area > 0 else None,
                            pasture_area_ha=pasture_area if pasture_area > 0 else None,
                            hayfield_area_ha=hayfield_area if hayfield_area > 0 else None
                        )
                        db.add(new_farm)
                        db.commit()
                        db.refresh(new_farm)  # Получить ID созданного хозяйства

                        # Автоматически привязать текущего фермера к созданному хозяйству
                        if not is_admin() and user:
                            current_user_id = user.get("id")
                            db_user = db.query(User).filter(User.id == current_user_id).first()
                            if db_user and not db_user.farm_id:
                                db_user.farm_id = new_farm.id
                                db.commit()
                                # Обновляем farm_id в session_state
                                st.session_state["user"]["farm_id"] = new_farm.id
                                st.success("✅ Хозяйство успешно зарегистрировано и привязано к вашему аккаунту!")
                            else:
                                st.success("✅ Хозяйство успешно зарегистрировано!")
                        else:
                            st.success("✅ Хозяйство успешно зарегистрировано!")

                    st.balloons()
                    st.session_state.edit_mode = False
                    st.rerun()

                except Exception as e:
                    db.rollback()
                    st.error(f"❌ Ошибка при сохранении: {str(e)}")

# Боковая панель с подсказками
with st.sidebar:
    st.markdown("### 💡 Подсказки")

    st.info("""
    **Обязательные поля:**
    - БИН (12 цифр)
    - Название хозяйства
    - ФИО руководителя
    - Область
    - Телефон
    - Общая площадь
    - Площадь пашни

    **Как заполнять:**
    - БИН без пробелов и тире
    - Телефон: +7 (7xx) xxx-xx-xx
    - Площади в гектарах
    """)

    st.markdown("---")

    st.markdown("### 📥 Альтернативный способ")
    st.info("""
    Вы можете импортировать данные хозяйства из Excel файла.

    Перейдите на страницу **"Импорт"** и выберите тип **"01 - Общая информация хозяйства"**.
    """)

# Футер
st.markdown("---")
st.markdown("🏢 **Регистрация хозяйства** | Версия 1.0")
