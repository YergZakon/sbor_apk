"""
Fields - Управление полями
Добавление, редактирование, просмотр полей
"""
import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from modules.database import SessionLocal, Farm, Field, Operation
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
import json
from pathlib import Path

# Настройка страницы
st.set_page_config(page_title="Поля", page_icon="🌱", layout="wide")

# Требуем авторизацию и привязку к хозяйству
require_auth()
require_farm_binding()

# Заголовок
st.title("🌱 Управление полями")
st.caption(f"Пользователь: **{get_user_display_name()}**")

# Получение сессии БД
db = SessionLocal()

try:
    # Проверка наличия хозяйства
    from modules.auth import get_current_user, is_admin
    user = get_current_user()

    if is_admin():
        # Админ может выбрать хозяйство (если нужно, добавьте селектор)
        farm = db.query(Farm).first()
    else:
        # Фермер работает со своим хозяйством
        user_farm_id = user.get("farm_id") if user else None
        if user_farm_id:
            farm = db.query(Farm).filter(Farm.id == user_farm_id).first()
        else:
            farm = None

    if not farm:
        st.error("❌ Хозяйство не найдено. Обратитесь к администратору для привязки к хозяйству.")
        st.stop()

    # ============================================================================
    # СПИСОК ПОЛЕЙ
    # ============================================================================

    st.markdown("### 📋 Список полей")

    # Получение полей для текущего хозяйства
    fields = filter_query_by_farm(db.query(Field), Field).all()

    if fields:
        # Создание DataFrame для отображения
        fields_data = []
        for field in fields:
            fields_data.append({
                'ID': field.id,
                'Код': field.field_code,
                'Название': field.name or '-',
                'Площадь (га)': field.area_ha or 0,
                'Тип почвы': field.soil_type or '-',
                'pH': field.ph_water or '-',
                'Гумус (%)': field.humus_pct or '-',
                'Координаты': f"{field.center_lat}, {field.center_lon}" if field.center_lat and field.center_lon else 'Не указаны'
            })

        df_fields = pd.DataFrame(fields_data)

        # Отображение таблицы
        st.dataframe(df_fields, use_container_width=True, hide_index=True)

        # Статистика
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Всего полей", len(fields))
        with col2:
            total_area = sum([f.area_ha for f in fields if f.area_ha])
            st.metric("Общая площадь", f"{total_area:,.1f} га")
        with col3:
            avg_area = total_area / len(fields) if fields else 0
            st.metric("Средняя площадь", f"{avg_area:,.1f} га")
        with col4:
            fields_with_coords = sum([1 for f in fields if f.center_lat and f.center_lon])
            st.metric("С координатами", f"{fields_with_coords}/{len(fields)}")

    else:
        st.info("Поля еще не добавлены. Добавьте первое поле ниже.")

    st.markdown("---")

    # ============================================================================
    # ДОБАВЛЕНИЕ НОВОГО ПОЛЯ
    # ============================================================================

    st.markdown("### ➕ Добавить новое поле")

    # Справочник типов почв: объединяем статический список и JSON-справочник (если есть)
    soil_types_set = set(settings.SOIL_TYPES)
    soil_types_path = Path('data/soil_types.json')
    if soil_types_path.exists():
        try:
            with open(soil_types_path, 'r', encoding='utf-8') as f:
                soil_types_json = json.load(f)
                soil_types_set.update(list(soil_types_json.keys()))
        except Exception:
            pass
    soil_types_options = ["Не указан"] + sorted(soil_types_set)

    with st.form("add_field_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Основная информация")

            field_name = st.text_input(
                "Название поля*",
                placeholder="Например: Центральное",
                help="Удобное название для идентификации поля"
            )

            area_ha = st.number_input(
                "Площадь (га)*",
                min_value=0.1,
                max_value=10000.0,
                step=0.1,
                value=100.0,
                help="Фактическая обрабатываемая площадь"
            )

            cadastral_number = st.text_input(
                "Кадастровый номер",
                placeholder="XX:XX:XXXXXX:XX",
                help="Опционально: кадастровый номер участка"
            )

            with st.expander("📍 Координаты (опционально)", expanded=False):
                center_lat = st.number_input(
                    "Широта",
                    min_value=40.0,
                    max_value=56.0,
                    value=51.1801,
                    step=0.0001,
                    format="%.4f",
                    help="GPS координата центра поля"
                )

                center_lon = st.number_input(
                    "Долгота",
                    min_value=46.0,
                    max_value=88.0,
                    value=71.4460,
                    step=0.0001,
                    format="%.4f",
                    help="GPS координата центра поля"
                )

        with col2:
            st.markdown("#### Характеристики почвы")

            soil_type = st.selectbox(
                "Тип почвы",
                options=soil_types_options,
                help="Тип почвы по классификации"
            )

            soil_texture = st.selectbox(
                "Гранулометрический состав",
                options=["Не указан"] + settings.SOIL_TEXTURES,
                help="Механический состав почвы"
            )

            relief = st.selectbox(
                "Рельеф",
                options=["Не указан"] + settings.RELIEF_TYPES,
                help="Тип рельефа поля"
            )

            slope_degree = st.number_input(
                "Уклон (градусы)",
                min_value=0.0,
                max_value=45.0,
                value=None,
                step=0.1,
                help="Степень уклона поля"
            )

            with st.expander("🧪 Агрохимические показатели (опционально)", expanded=False):
                col2_1, col2_2 = st.columns(2)

                with col2_1:
                    ph_water = st.number_input(
                        "pH водный",
                        min_value=4.0,
                        max_value=9.5,
                        value=6.5,
                        step=0.1,
                        help="pH почвы (водная вытяжка)"
                    )

                    humus_pct = st.number_input(
                        "Гумус (%)",
                        min_value=0.1,
                        max_value=12.0,
                        value=3.0,
                        step=0.1,
                        help="Содержание гумуса в процентах"
                    )

                with col2_2:
                    p2o5_mg_kg = st.number_input(
                        "P2O5 (мг/кг)",
                        min_value=0.0,
                        max_value=500.0,
                        value=50.0,
                        step=1.0,
                        help="Подвижный фосфор"
                    )

                    k2o_mg_kg = st.number_input(
                        "K2O (мг/кг)",
                        min_value=0.0,
                        max_value=1000.0,
                        value=150.0,
                        step=1.0,
                        help="Обменный калий"
                    )

        # Кнопка отправки
        submitted = st.form_submit_button("Добавить поле", use_container_width=True, type="primary")

        if submitted:
            # Валидация
            errors = []

            if not field_name:
                errors.append("Название поля обязательно")

            if area_ha <= 0:
                errors.append("Площадь должна быть больше 0")

            # Валидация координат
            if center_lat and center_lon:
                is_valid, msg = validator.validate_coordinates(center_lat, center_lon)
                if not is_valid:
                    errors.append(msg)

            # Валидация pH
            if ph_water:
                is_valid, msg = validator.validate_ph(ph_water)
                if not is_valid:
                    errors.append(msg)

            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Генерация кода поля (находим максимальный номер и добавляем 1)
                existing_codes = db.query(Field.field_code).filter(
                    Field.field_code.like('field_%')
                ).all()

                # Извлекаем числа из кодов и находим максимальное
                max_number = 0
                for (code,) in existing_codes:
                    try:
                        number = int(code.split('_')[1])
                        max_number = max(max_number, number)
                    except (ValueError, IndexError):
                        continue

                field_number = max_number + 1
                field_code = f"field_{field_number:03d}"

                # Создание поля
                new_field = Field(
                    farm_id=farm.id,
                    field_code=field_code,
                    name=field_name,
                    cadastral_number=cadastral_number if cadastral_number else None,
                    area_ha=area_ha,
                    center_lat=center_lat if center_lat else None,
                    center_lon=center_lon if center_lon else None,
                    soil_type=soil_type if soil_type != "Не указан" else None,
                    soil_texture=soil_texture if soil_texture != "Не указан" else None,
                    relief=relief if relief != "Не указан" else None,
                    slope_degree=slope_degree if slope_degree > 0 else None,
                    ph_water=ph_water if ph_water else None,
                    humus_pct=humus_pct if humus_pct else None,
                    p2o5_mg_kg=p2o5_mg_kg if p2o5_mg_kg else None,
                    k2o_mg_kg=k2o_mg_kg if k2o_mg_kg else None,
                )

                db.add(new_field)
                db.commit()

                st.success(f"✅ Поле '{field_name}' успешно добавлено! Код поля: {field_code}")
                st.balloons()

                # Перезагрузка страницы
                st.rerun()

    st.markdown("---")

    # ============================================================================
    # РЕДАКТИРОВАНИЕ ПОЛЯ
    # ============================================================================

    if fields:
        st.markdown("### ✏️ Редактирование поля")

        selected_field = st.selectbox(
            "Выберите поле для редактирования:",
            options=fields,
            format_func=lambda x: f"{x.field_code} - {x.name or 'Без названия'} ({x.area_ha} га)"
        )

        if selected_field:
            with st.expander("📝 Редактировать поле", expanded=False):
                with st.form(f"edit_field_{selected_field.id}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        edit_name = st.text_input("Название", value=selected_field.name or "", key=f"edit_name_{selected_field.id}")
                        edit_area = st.number_input("Площадь (га)", value=float(selected_field.area_ha or 0), min_value=0.1, step=0.1, key=f"edit_area_{selected_field.id}")
                        edit_cadastral = st.text_input("Кадастровый номер", value=selected_field.cadastral_number or "", key=f"edit_cadastral_{selected_field.id}")

                    with col2:
                        edit_soil_type = st.selectbox(
                            "Тип почвы",
                            options=soil_types_options,
                            index=(soil_types_options.index(selected_field.soil_type)
                                   if (selected_field.soil_type and selected_field.soil_type in soil_types_options)
                                   else 0)
                        )
                        edit_ph = st.number_input("pH водный", value=float(selected_field.ph_water or 0), min_value=4.0, max_value=9.5, step=0.1)
                        edit_humus = st.number_input("Гумус (%)", value=float(selected_field.humus_pct or 0), min_value=0.0, max_value=12.0, step=0.1)

                    col_buttons = st.columns([1, 1, 2])

                    with col_buttons[0]:
                        update_btn = st.form_submit_button("💾 Сохранить", use_container_width=True, type="primary")

                    with col_buttons[1]:
                        delete_btn = st.form_submit_button("🗑️ Удалить", use_container_width=True, type="secondary")

                    if update_btn:
                        # Получаем объект поля из текущей сессии для обновления
                        field_to_update = db.query(Field).filter(Field.id == selected_field.id).first()

                        if field_to_update:
                            # Обновляем атрибуты
                            field_to_update.name = edit_name
                            field_to_update.area_ha = edit_area
                            field_to_update.cadastral_number = edit_cadastral if edit_cadastral else None
                            field_to_update.soil_type = edit_soil_type if edit_soil_type != "Не указан" else None
                            field_to_update.ph_water = edit_ph if edit_ph > 0 else None
                            field_to_update.humus_pct = edit_humus if edit_humus > 0 else None

                            db.commit()
                            st.success("✅ Поле обновлено!")
                            st.rerun()
                        else:
                            st.error("❌ Ошибка: поле не найдено в базе данных")

                    if delete_btn:
                        # Проверка на связанные данные
                        field_id = selected_field.id
                        operations_count = db.query(Operation).filter(Operation.field_id == field_id).count()

                        if operations_count > 0:
                            st.error(f"❌ Невозможно удалить поле: есть связанные данные ({operations_count} операций)")
                        else:
                            # Получаем объект из текущей сессии перед удалением
                            field_to_delete = db.query(Field).filter(Field.id == field_id).first()
                            if field_to_delete:
                                db.delete(field_to_delete)
                                db.commit()
                                st.success("✅ Поле удалено!")
                                st.rerun()

    st.markdown("---")

    # ============================================================================
    # КАРТА ПОЛЕЙ (если есть координаты)
    # ============================================================================

    fields_with_coords = [f for f in fields if f.center_lat and f.center_lon]

    if fields_with_coords:
        st.markdown("### 🗺️ Карта полей")

        # Создание DataFrame для карты
        map_data = pd.DataFrame([
            {
                'lat': f.center_lat,
                'lon': f.center_lon,
                'name': f.name or f.field_code,
                'area': f.area_ha
            }
            for f in fields_with_coords
        ])

        # Отображение карты
        st.map(map_data, size='area', zoom=10)

        st.info(f"📍 На карте отображено {len(fields_with_coords)} из {len(fields)} полей")

finally:
    db.close()

# Sidebar
with st.sidebar:
    st.markdown("### ℹ️ Справка")
    st.info("""
    **Управление полями** позволяет:
    - Добавлять новые поля
    - Редактировать существующие
    - Просматривать список всех полей
    - Отображать поля на карте

    **Обязательные поля:**
    - Название
    - Площадь (га)

    **Рекомендуется указать:**
    - GPS-координаты
    - Тип почвы
    - Агрохимические показатели
    """)

    st.markdown("### 📊 Типы почв")
    with st.expander("Показать список"):
        for soil in settings.SOIL_TYPES:
            st.markdown(f"- {soil}")

    st.markdown("### 🎯 Рекомендации")
    st.markdown("""
    - Добавьте GPS-координаты для отображения на карте
    - Проведите агрохимический анализ
    - Обновляйте данные ежегодно
    """)
