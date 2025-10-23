"""
Snow Retention - Учет снегозадержания
"""
import streamlit as st
import pandas as pd
import json
from datetime import date
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from modules.database import get_db, Farm, Field, Operation, SnowRetentionDetails, Machinery, Implements
from modules.auth import require_auth, require_farm_binding, filter_query_by_farm, get_user_display_name, get_current_user, is_admin

st.set_page_config(page_title="Снегозадержание", page_icon="❄️", layout="wide")
require_auth()
require_farm_binding()

st.title("❄️ Учет снегозадержания")
st.caption(f"Пользователь: **{get_user_display_name()}**")

db = next(get_db())

# Загрузка справочника тракторов
tractors_ref = {}
try:
    tractors_path = Path('data/tractors.json')
    if tractors_path.exists():
        with open(tractors_path, 'r', encoding='utf-8') as f:
            tractors_ref = json.load(f)
except Exception as e:
    pass  # Справочник опционален

user = get_current_user()
farm = db.query(Farm).first() if is_admin() else db.query(Farm).filter(Farm.id == user.get("farm_id")).first()

if not farm:
    st.warning("⚠️ Сначала создайте хозяйство!")
    st.stop()

fields = filter_query_by_farm(db.query(Field), Field).all()
if not fields:
    st.warning("⚠️ Сначала добавьте поля!")
    st.stop()

tab1, tab2 = st.tabs(["📝 Регистрация", "📊 История"])

with tab1:
    st.subheader("Регистрация снегозадержания")

    with st.form("snow_retention_form"):
        col1, col2 = st.columns(2)

        with col1:
            field_options = {f"{f.field_code} - {f.name}": f for f in fields}
            selected_field = field_options[st.selectbox("Поле *", list(field_options.keys()))]

            operation_date = st.date_input("Дата *", value=date.today())
            end_date = st.date_input("Дата окончания", value=None)

            method = st.selectbox(
                "Метод *",
                ['snow_plowing', 'barriers', 'vegetation', 'other'],
                format_func=lambda x: {
                    'snow_plowing': 'Снегопахание (валкование)',
                    'barriers': 'Установка щитов/кулис',
                    'vegetation': 'Растительные кулисы',
                    'other': 'Другое'
                }[x]
            )

        with col2:
            area_processed = st.number_input("Площадь (га) *", min_value=0.1, max_value=selected_field.area_ha, value=selected_field.area_ha, step=0.1)

            snow_depth_cm = st.number_input("Глубина снега (см)", min_value=0.0, value=None, step=1.0, help="Глубина снежного покрова")

            number_of_passes = st.number_input("Количество проходов", min_value=1, value=1, step=1, help="Количество проходов снегопаха")

        st.markdown("---")
        st.markdown("### 🚜 Техника")

        machinery_list = filter_query_by_farm(db.query(Machinery).filter(Machinery.status == 'active'), Machinery).all()
        implements_list = filter_query_by_farm(db.query(Implements).filter(Implements.status == 'active'), Implements).all()

        # Pre-load machinery attributes
        tractors = [m for m in machinery_list if m.machinery_type == 'tractor']
        machinery_options = {}
        machinery_details = {}  # Для хранения деталей техники

        if tractors:
            for m in tractors:
                # Eagerly access attributes while still in session
                m_brand = m.brand or ''
                m_model = m.model
                m_year = m.year

                display_text = f"{m_brand} {m_model}"
                machinery_options[display_text] = (m.id, m_year)

                # Ищем технику в справочнике
                ref_key = f"{m_brand} {m_model}"
                if ref_key in tractors_ref:
                    machinery_details[display_text] = tractors_ref[ref_key]

        # Pre-load implement attributes
        snow_plows = [impl for impl in implements_list if impl.implement_type == 'snow_plow']
        implement_options = {}
        if snow_plows:
            for i in snow_plows:
                # Eagerly access attributes while still in session
                display_text = f"{i.brand or ''} {i.model}"
                implement_options[display_text] = (i.id, i.year)

        col_tech1, col_tech2, col_tech3 = st.columns(3)

        with col_tech1:
            selected_machinery_display = st.selectbox("Трактор", ["Не выбрано"] + list(machinery_options.keys()))

            if selected_machinery_display != "Не выбрано":
                selected_machinery_id, machine_year = machinery_options[selected_machinery_display]

                # Показываем характеристики из справочника
                if selected_machinery_display in machinery_details:
                    ref_data = machinery_details[selected_machinery_display]
                    st.success(f"💪 {ref_data['мощность_лс']} л.с. | 🏷️ {ref_data['класс']} | 🚜 {ref_data['тип']}")

                    if ref_data.get('применение'):
                        applications = ', '.join(ref_data['применение'])
                        st.info(f"🔧 Применение: {applications}")
                else:
                    st.caption(f"Год выпуска: {machine_year or 'не указан'}")
            else:
                selected_machinery_id = None
                machine_year = None

        with col_tech2:
            selected_implement_display = st.selectbox("Снегопах", ["Не выбрано"] + list(implement_options.keys()))

            if selected_implement_display != "Не выбрано":
                selected_implement_id, implement_year = implement_options[selected_implement_display]
            else:
                selected_implement_id = None
                implement_year = None

        with col_tech3:
            work_speed_kmh = st.number_input("Скорость (км/ч)", min_value=0.0, value=None, step=0.5)

        notes = st.text_area("Примечания")

        submitted = st.form_submit_button("✅ Зарегистрировать", use_container_width=True, type="primary")

        if submitted:
            try:
                operation = Operation(
                    farm_id=farm.id, field_id=selected_field.id, operation_type="snow_retention",
                    operation_date=operation_date, end_date=end_date, area_processed_ha=area_processed,
                    machine_id=selected_machinery_id,
                    implement_id=selected_implement_id,
                    machine_year=machine_year, implement_year=implement_year,
                    work_speed_kmh=work_speed_kmh, notes=notes
                )
                db.add(operation)
                db.flush()

                snow_retention_details = SnowRetentionDetails(
                    operation_id=operation.id, method=method,
                    snow_depth_cm=snow_depth_cm, number_of_passes=number_of_passes
                )
                db.add(snow_retention_details)
                db.commit()

                st.success(f"✅ Снегозадержание зарегистрировано! Обработано {area_processed} га")
                st.balloons()
            except Exception as e:
                db.rollback()
                st.error(f"❌ Ошибка: {str(e)}")

with tab2:
    st.subheader("История снегозадержания")

    operations = db.query(Operation, Field, SnowRetentionDetails).join(Field).outerjoin(SnowRetentionDetails).filter(
        Operation.operation_type == "snow_retention", Field.farm_id == farm.id
    ).order_by(Operation.operation_date.desc()).all()

    if operations:
        data = [{
            'Дата': op[0].operation_date.strftime('%Y-%m-%d'),
            'Поле': op[1].name or op[1].field_code,
            'Метод': {
                'snow_plowing': 'Снегопахание',
                'barriers': 'Щиты/кулисы',
                'vegetation': 'Растительные кулисы',
                'other': 'Другое'
            }.get(op[2].method if op[2] else None, '-'),
            'Глубина снега (см)': op[2].snow_depth_cm if op[2] else '-',
            'Площадь (га)': op[0].area_processed_ha
        } for op in operations]

        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Всего операций", len(operations))
        with col2:
            total_area = sum([op[0].area_processed_ha for op in operations if op[0].area_processed_ha])
            st.metric("Обработано всего", f"{total_area:,.1f} га")
    else:
        st.info("📭 История пуста")
