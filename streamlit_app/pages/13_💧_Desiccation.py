"""
Desiccation - Учет десикации (предуборочного подсушивания)
"""
import streamlit as st
import pandas as pd
import json
from datetime import date
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from modules.database import get_db, Farm, Field, Operation, DesiccationDetails, Machinery, Implements
from modules.auth import require_auth, require_farm_binding, filter_query_by_farm, get_user_display_name, get_current_user, is_admin

st.set_page_config(page_title="Десикация", page_icon="💧", layout="wide")
require_auth()
require_farm_binding()

st.title("💧 Учет десикации")
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
    st.subheader("Регистрация десикации")

    with st.form("desiccation_form"):
        col1, col2 = st.columns(2)

        with col1:
            field_options = {f"{f.field_code} - {f.name}": f for f in fields}
            selected_field = field_options[st.selectbox("Поле *", list(field_options.keys()))]

            operation_date = st.date_input("Дата *", value=date.today())
            end_date = st.date_input("Дата окончания", value=None)

            product_name = st.text_input("Препарат *", placeholder="Например: Раундап")
            active_ingredient = st.text_input("Действующее вещество", placeholder="Например: Глифосат")

        with col2:
            area_processed = st.number_input("Площадь (га) *", min_value=0.1, max_value=selected_field.area_ha, value=selected_field.area_ha, step=0.1)
            rate_per_ha = st.number_input("Норма расхода (л/га)", min_value=0.0, value=2.0, step=0.1)
            target_moisture_percent = st.number_input("Целевая влажность (%)", min_value=0.0, max_value=100.0, value=14.0, step=0.5)
            application_method = st.selectbox("Способ применения", ["Наземное опрыскивание", "Авиационное опрыскивание"])

        st.markdown("---")
        st.markdown("### 🚜 Техника")

        machinery_list = filter_query_by_farm(db.query(Machinery).filter(Machinery.status == 'active'), Machinery).all()
        implements_list = filter_query_by_farm(db.query(Implements).filter(Implements.status == 'active'), Implements).all()

        # Pre-load machinery attributes
        spray_machinery = [m for m in machinery_list if m.machinery_type in ['tractor', 'self_propelled_sprayer', 'drone']]
        machinery_options = {}
        machinery_details = {}  # Для хранения деталей техники

        if spray_machinery:
            for m in spray_machinery:
                # Eagerly access attributes while still in session
                m_brand = m.brand or ''
                m_model = m.model
                m_year = m.year
                m_type = m.machinery_type

                display_text = f"{m_brand} {m_model}"
                machinery_options[display_text] = (m.id, m_year, m_type)

                # Ищем технику в справочнике
                ref_key = f"{m_brand} {m_model}"
                if ref_key in tractors_ref:
                    machinery_details[display_text] = tractors_ref[ref_key]

        # Pre-load implement attributes
        sprayers = [impl for impl in implements_list if impl.implement_type == 'sprayer_trailer']
        implement_options = {}
        if sprayers:
            for i in sprayers:
                # Eagerly access attributes while still in session
                display_text = f"{i.brand or ''} {i.model}"
                implement_options[display_text] = (i.id, i.year)

        col_tech1, col_tech2, col_tech3 = st.columns(3)

        with col_tech1:
            selected_machinery_display = st.selectbox("Техника", ["Не выбрано"] + list(machinery_options.keys()))

            if selected_machinery_display != "Не выбрано":
                selected_machinery_id, machine_year, machinery_type = machinery_options[selected_machinery_display]

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
                machinery_type = None

        with col_tech2:
            needs_implement = selected_machinery_id and machinery_type == 'tractor'
            if needs_implement:
                selected_implement_display = st.selectbox("Опрыскиватель", ["Не выбрано"] + list(implement_options.keys()))

                if selected_implement_display != "Не выбрано":
                    selected_implement_id, implement_year = implement_options[selected_implement_display]
                else:
                    selected_implement_id = None
                    implement_year = None
            else:
                selected_implement_id = None
                implement_year = None
                st.info("Агрегат не требуется")

        with col_tech3:
            work_speed_kmh = st.number_input("Скорость (км/ч)", min_value=0.0, value=None, step=0.5)

        notes = st.text_area("Примечания")

        submitted = st.form_submit_button("✅ Зарегистрировать", use_container_width=True, type="primary")

        if submitted:
            if not product_name:
                st.error("❌ Укажите препарат")
            else:
                try:
                    operation = Operation(
                        farm_id=farm.id, field_id=selected_field.id, operation_type="desiccation",
                        operation_date=operation_date, end_date=end_date, area_processed_ha=area_processed,
                        machine_id=selected_machinery_id,
                        implement_id=selected_implement_id,
                        machine_year=machine_year, implement_year=implement_year,
                        work_speed_kmh=work_speed_kmh, notes=notes
                    )
                    db.add(operation)
                    db.flush()

                    desiccation_details = DesiccationDetails(
                        operation_id=operation.id, product_name=product_name,
                        active_ingredient=active_ingredient, rate_per_ha=rate_per_ha,
                        target_moisture_percent=target_moisture_percent, application_method=application_method
                    )
                    db.add(desiccation_details)
                    db.commit()

                    st.success(f"✅ Десикация зарегистрирована! Обработано {area_processed} га")
                    st.balloons()
                except Exception as e:
                    db.rollback()
                    st.error(f"❌ Ошибка: {str(e)}")

with tab2:
    st.subheader("История десикаций")

    operations = db.query(Operation, Field, DesiccationDetails).join(Field).outerjoin(DesiccationDetails).filter(
        Operation.operation_type == "desiccation", Field.farm_id == farm.id
    ).order_by(Operation.operation_date.desc()).all()

    if operations:
        data = [{
            'Дата': op[0].operation_date.strftime('%Y-%m-%d'),
            'Поле': op[1].name or op[1].field_code,
            'Препарат': op[2].product_name if op[2] else '-',
            'Норма (л/га)': op[2].rate_per_ha if op[2] else '-',
            'Площадь (га)': op[0].area_processed_ha
        } for op in operations]

        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Всего обработок", len(operations))
        with col2:
            total_area = sum([op[0].area_processed_ha for op in operations if op[0].area_processed_ha])
            st.metric("Обработано всего", f"{total_area:,.1f} га")
    else:
        st.info("📭 История пуста")
