"""
Fallow - Учет обработки паров
"""
import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from modules.database import get_db, Farm, Field, Operation, FallowDetails, Machinery, Implements
from modules.auth import require_auth, require_farm_binding, filter_query_by_farm, get_user_display_name, get_current_user, is_admin

st.set_page_config(page_title="Обработка паров", page_icon="🌾", layout="wide")
require_auth()
require_farm_binding()

st.title("🌾 Учет обработки паров")
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
    st.subheader("Регистрация обработки паров")

    with st.form("fallow_form"):
        col1, col2 = st.columns(2)

        with col1:
            field_options = {f"{f.field_code} - {f.name}": f for f in fields}
            selected_field = field_options[st.selectbox("Поле *", list(field_options.keys()))]

            operation_date = st.date_input("Дата *", value=date.today())
            end_date = st.date_input("Дата окончания", value=None)

            fallow_type = st.selectbox(
                "Тип пара *",
                ['black', 'early', 'green', 'cultivated'],
                format_func=lambda x: {
                    'black': 'Чистый пар',
                    'early': 'Ранний пар',
                    'green': 'Зеленый пар',
                    'cultivated': 'Обработанный пар'
                }[x]
            )

        with col2:
            area_processed = st.number_input("Площадь (га) *", min_value=0.1, max_value=selected_field.area_ha, value=selected_field.area_ha, step=0.1)

            processing_depth_cm = st.number_input("Глубина обработки (см)", min_value=0.0, value=None, step=1.0, help="Глубина обработки паровых полей")

            number_of_treatments = st.number_input("Количество обработок", min_value=1, value=1, step=1, help="Количество обработок паровых полей")

        st.markdown("---")
        st.markdown("### 🚜 Техника")

        machinery_list = filter_query_by_farm(db.query(Machinery).filter(Machinery.status == 'active'), Machinery).all()
        implements_list = filter_query_by_farm(db.query(Implements).filter(Implements.status == 'active'), Implements).all()

        col_tech1, col_tech2, col_tech3 = st.columns(3)

        with col_tech1:
            tractors = [m for m in machinery_list if m.machinery_type == 'tractor']
            selected_machinery = st.selectbox("Трактор", [None] + tractors, format_func=lambda m: "Не выбрано" if m is None else f"{m.brand or ''} {m.model}")
            machine_year = selected_machinery.year if selected_machinery else None

        with col_tech2:
            fallow_implements = [impl for impl in implements_list if impl.implement_type in ['cultivator', 'harrow', 'disc', 'plow']]
            selected_implement = st.selectbox("Агрегат", [None] + fallow_implements, format_func=lambda i: "Не выбрано" if i is None else f"{i.brand or ''} {i.model}")
            implement_year = selected_implement.year if selected_implement else None

        with col_tech3:
            work_speed_kmh = st.number_input("Скорость (км/ч)", min_value=0.0, value=None, step=0.5)

        notes = st.text_area("Примечания")

        submitted = st.form_submit_button("✅ Зарегистрировать", use_container_width=True, type="primary")

        if submitted:
            try:
                operation = Operation(
                    farm_id=farm.id, field_id=selected_field.id, operation_type="fallow",
                    operation_date=operation_date, end_date=end_date, area_processed_ha=area_processed,
                    machine_id=selected_machinery.id if selected_machinery else None,
                    implement_id=selected_implement.id if selected_implement else None,
                    machine_year=machine_year, implement_year=implement_year,
                    work_speed_kmh=work_speed_kmh, notes=notes
                )
                db.add(operation)
                db.flush()

                fallow_details = FallowDetails(
                    operation_id=operation.id, fallow_type=fallow_type,
                    processing_depth_cm=processing_depth_cm, number_of_treatments=number_of_treatments
                )
                db.add(fallow_details)
                db.commit()

                st.success(f"✅ Обработка паров зарегистрирована! Обработано {area_processed} га")
                st.balloons()
            except Exception as e:
                db.rollback()
                st.error(f"❌ Ошибка: {str(e)}")

with tab2:
    st.subheader("История обработки паров")

    operations = db.query(Operation, Field, FallowDetails).join(Field).outerjoin(FallowDetails).filter(
        Operation.operation_type == "fallow", Field.farm_id == farm.id
    ).order_by(Operation.operation_date.desc()).all()

    if operations:
        data = [{
            'Дата': op[0].operation_date.strftime('%Y-%m-%d'),
            'Поле': op[1].name or op[1].field_code,
            'Тип пара': {
                'black': 'Чистый',
                'early': 'Ранний',
                'green': 'Зеленый',
                'cultivated': 'Обработанный'
            }.get(op[2].fallow_type if op[2] else None, '-'),
            'Глубина (см)': op[2].processing_depth_cm if op[2] else '-',
            'Обработок': op[2].number_of_treatments if op[2] else '-',
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
