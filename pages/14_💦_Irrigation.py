"""
Irrigation - Учет орошения
"""
import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from modules.database import get_db, Farm, Field, Operation, IrrigationDetails, Machinery
from modules.auth import require_auth, require_farm_binding, filter_query_by_farm, get_user_display_name, get_current_user, is_admin

st.set_page_config(page_title="Орошение", page_icon="💦", layout="wide")
require_auth()
require_farm_binding()

st.title("💦 Учет орошения")
st.caption(f"Пользователь: **{get_user_display_name()}**")

db = next(get_db())
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
    st.subheader("Регистрация орошения")

    with st.form("irrigation_form"):
        col1, col2 = st.columns(2)

        with col1:
            field_options = {f"{f.field_code} - {f.name}": f for f in fields}
            selected_field = field_options[st.selectbox("Поле *", list(field_options.keys()))]

            operation_date = st.date_input("Дата *", value=date.today())
            end_date = st.date_input("Дата окончания", value=None)

            irrigation_type = st.selectbox(
                "Тип орошения *",
                ['sprinkler', 'drip', 'furrow', 'flood', 'center_pivot'],
                format_func=lambda x: {
                    'sprinkler': 'Дождевание',
                    'drip': 'Капельное',
                    'furrow': 'По бороздам',
                    'flood': 'Затопление',
                    'center_pivot': 'Круговое дождевание'
                }[x]
            )

        with col2:
            area_processed = st.number_input("Площадь (га) *", min_value=0.1, max_value=selected_field.area_ha, value=selected_field.area_ha, step=0.1)
            water_volume_m3 = st.number_input("Объем воды (м³)", min_value=0.0, value=1000.0, step=100.0)

            water_rate_m3_ha = water_volume_m3 / area_processed if area_processed > 0 else 0
            st.metric("Норма полива", f"{water_rate_m3_ha:.1f} м³/га")

            water_source = st.selectbox("Источник воды", ["Скважина", "Река", "Канал", "Водохранилище", "Другое"], index=None)

        st.markdown("---")
        st.markdown("### 🚜 Оборудование")

        machinery_list = filter_query_by_farm(db.query(Machinery).filter(Machinery.status == 'active'), Machinery).all()
        irrigation_systems = [m for m in machinery_list if m.machinery_type == 'irrigation_system']

        col_tech1, col_tech2 = st.columns(2)

        with col_tech1:
            selected_machinery = st.selectbox("Система орошения", [None] + irrigation_systems, format_func=lambda m: "Не выбрано" if m is None else f"{m.brand or ''} {m.model}")
            machine_year = selected_machinery.year if selected_machinery else None

        with col_tech2:
            soil_moisture_before = st.number_input("Влажность почвы до (%)", min_value=0.0, max_value=100.0, value=None, step=1.0)

        notes = st.text_area("Примечания")

        submitted = st.form_submit_button("✅ Зарегистрировать", use_container_width=True, type="primary")

        if submitted:
            try:
                operation = Operation(
                    farm_id=farm.id, field_id=selected_field.id, operation_type="irrigation",
                    operation_date=operation_date, end_date=end_date, area_processed_ha=area_processed,
                    machine_id=selected_machinery.id if selected_machinery else None,
                    machine_year=machine_year, notes=notes
                )
                db.add(operation)
                db.flush()

                irrigation_details = IrrigationDetails(
                    operation_id=operation.id, irrigation_type=irrigation_type,
                    water_volume_m3=water_volume_m3, water_rate_m3_ha=water_rate_m3_ha,
                    water_source=water_source, soil_moisture_before=soil_moisture_before
                )
                db.add(irrigation_details)
                db.commit()

                st.success(f"✅ Орошение зарегистрировано! Полито {area_processed} га, использовано {water_volume_m3} м³ воды")
                st.balloons()
            except Exception as e:
                db.rollback()
                st.error(f"❌ Ошибка: {str(e)}")

with tab2:
    st.subheader("История орошений")

    operations = db.query(Operation, Field, IrrigationDetails).join(Field).outerjoin(IrrigationDetails).filter(
        Operation.operation_type == "irrigation", Field.farm_id == farm.id
    ).order_by(Operation.operation_date.desc()).all()

    if operations:
        data = [{
            'Дата': op[0].operation_date.strftime('%Y-%m-%d'),
            'Поле': op[1].name or op[1].field_code,
            'Тип': {
                'sprinkler': 'Дождевание', 'drip': 'Капельное', 'furrow': 'По бороздам',
                'flood': 'Затопление', 'center_pivot': 'Круговое'
            }.get(op[2].irrigation_type if op[2] else None, '-'),
            'Объем (м³)': op[2].water_volume_m3 if op[2] else '-',
            'Площадь (га)': op[0].area_processed_ha
        } for op in operations]

        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Всего поливов", len(operations))
        with col2:
            total_area = sum([op[0].area_processed_ha for op in operations if op[0].area_processed_ha])
            st.metric("Полито всего", f"{total_area:,.1f} га")
        with col3:
            total_water = sum([op[2].water_volume_m3 for op in operations if op[2] and op[2].water_volume_m3])
            st.metric("Использовано воды", f"{total_water:,.0f} м³")
    else:
        st.info("📭 История пуста")
