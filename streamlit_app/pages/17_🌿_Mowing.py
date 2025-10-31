"""
Mowing - Учет укоса многолетних трав
"""
import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from modules.database import get_db, Farm, Field, Operation, MowingDetails, Machinery, Implements
from modules.auth import require_auth, require_farm_binding, filter_query_by_farm, get_user_display_name, get_current_user, is_admin
from utils.reference_loader import load_crops, load_tractors

st.set_page_config(page_title="Укос трав", page_icon="🌿", layout="wide")
require_auth()
require_farm_binding()

st.title("🌿 Учет укоса многолетних трав")
st.caption(f"Пользователь: **{get_user_display_name()}**")

db = next(get_db())

# Загрузка справочников
crops_ref = load_crops()
tractors_ref = load_tractors()

# Фильтруем только кормовые культуры из существующего справочника
forage_crops = {}
if crops_ref:
    forage_keywords = ['люцерна', 'эспарцет', 'донник', 'клевер', 'костер', 'житняк', 'трав']
    for crop_name, crop_data in crops_ref.items():
        crop_lower = crop_name.lower()
        if any(keyword in crop_lower for keyword in forage_keywords):
            forage_crops[crop_name] = crop_data

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
    st.subheader("Регистрация укоса")

    # Загружаем список предыдущих укосов ДО формы (для возможности связывания pickup с mowing)
    all_prev_mowings = db.query(Operation, MowingDetails, Field).join(
        MowingDetails, Operation.id == MowingDetails.operation_id
    ).join(
        Field, Operation.field_id == Field.id
    ).filter(
        Operation.operation_type == "mowing",
        MowingDetails.harvest_phase == "mowing",
        Field.farm_id == farm.id
    ).order_by(Operation.operation_date.desc()).all()

    with st.form("mowing_form"):
        col1, col2 = st.columns(2)

        with col1:
            field_options = {f"{f.field_code} - {f.name}": f for f in fields}
            selected_field = field_options[st.selectbox("Поле *", list(field_options.keys()))]

            operation_date = st.date_input("Дата *", value=date.today())
            end_date = st.date_input("Дата окончания", value=None, help="Для многодневных работ")

            # Культура - используем существующий crops.json
            if forage_crops:
                crop = st.selectbox(
                    "Культура *",
                    options=list(forage_crops.keys()),
                    help="Выберите кормовую культуру"
                )
            else:
                crop = st.text_input("Культура *", placeholder="Например: Люцерна")

            # Номер укоса
            mowing_number = st.selectbox(
                "Номер укоса *",
                options=[1, 2, 3, 4],
                help="Какой по счету укос в этом сезоне"
            )

        with col2:
            area_processed = st.number_input(
                "Площадь (га) *",
                min_value=0.1,
                max_value=selected_field.area_ha,
                value=selected_field.area_ha,
                step=0.1
            )

            # Фаза уборки
            harvest_phase = st.selectbox(
                "Фаза уборки *",
                options=["Укос (скашивание)", "Подбор валков"],
                help="Укос = скашивание и укладка в валки. Подбор = подбор высушенных валков"
            )

            harvest_phase_code = "mowing" if harvest_phase == "Укос (скашивание)" else "pickup"

            # Если это подбор, предлагаем выбрать связанную операцию укоса
            linked_operation_id = None
            if harvest_phase_code == "pickup" and all_prev_mowings:
                # Фильтруем укосы по выбранному полю и номеру укоса
                filtered_mowings = [
                    (op, md, f) for op, md, f in all_prev_mowings
                    if f.id == selected_field.id and md.mowing_number == mowing_number
                ]

                if filtered_mowings:
                    prev_options = {
                        f"{op.operation_date.strftime('%Y-%m-%d')} - {md.crop}": op.id
                        for op, md, f in filtered_mowings
                    }
                    selected_prev = st.selectbox(
                        "Связанный укос (опционально)",
                        options=["Не указан"] + list(prev_options.keys()),
                        help="Выберите операцию укоса, валки которой подбираете"
                    )
                    if selected_prev != "Не указан":
                        linked_operation_id = prev_options[selected_prev]

        st.markdown("---")
        st.markdown("### 📊 Урожайность и качество")

        col3, col4, col5 = st.columns(3)

        with col3:
            yield_green_mass = st.number_input(
                "Урожайность зеленой массы (т/га)",
                min_value=0.0,
                max_value=100.0,
                value=None,
                step=0.5,
                help="Для фазы укоса"
            )

            yield_hay = st.number_input(
                "Урожайность сена (т/га)",
                min_value=0.0,
                max_value=20.0,
                value=None,
                step=0.1,
                help="Для фазы подбора (после сушки)"
            )

        with col4:
            moisture_pct = st.number_input(
                "Влажность (%)",
                min_value=0.0,
                max_value=100.0,
                value=None,
                step=1.0,
                help="Влажность при укосе/подборе"
            )

            quality_class = st.selectbox(
                "Класс качества",
                options=["Не указан", "1-й класс", "2-й класс", "3-й класс", "Неклассное"],
                help="Класс качества сена"
            )

        with col5:
            plant_height = st.number_input(
                "Высота растений (см)",
                min_value=0.0,
                max_value=200.0,
                value=None,
                step=5.0,
                help="Высота растений при укосе"
            )

            stubble_height = st.number_input(
                "Высота среза (см)",
                min_value=0.0,
                max_value=50.0,
                value=None,
                step=1.0,
                help="Высота стерни после укоса"
            )

        st.markdown("---")
        st.markdown("### 🚜 Техника")

        machinery_list = filter_query_by_farm(db.query(Machinery).filter(Machinery.status == 'active'), Machinery).all()
        implements_list = filter_query_by_farm(db.query(Implements).filter(Implements.status == 'active'), Implements).all()

        # Pre-load machinery attributes
        tractors = [m for m in machinery_list if m.machinery_type == 'tractor']
        self_propelled_mowers = [m for m in machinery_list if m.machinery_type == 'self_propelled_mower']

        machinery_options = {}
        machinery_details = {}

        for m in tractors + self_propelled_mowers:
            m_brand = m.brand or ''
            m_model = m.model
            m_year = m.year
            m_type = m.machinery_type

            type_label = "Трактор" if m_type == 'tractor' else "Самоходная косилка"
            display_text = f"{m_brand} {m_model} ({type_label})"
            machinery_options[display_text] = (m.id, m_year, m_type)

            ref_key = f"{m_brand} {m_model}"
            if ref_key in tractors_ref:
                machinery_details[display_text] = tractors_ref[ref_key]

        # Pre-load implement attributes (косилки, пресс-подборщики)
        mowers = [impl for impl in implements_list if impl.implement_type in ['mower', 'baler']]
        implement_options = {}
        if mowers:
            for i in mowers:
                impl_type_label = "Косилка" if i.implement_type == 'mower' else "Пресс-подборщик"
                display_text = f"{i.brand or ''} {i.model} ({impl_type_label})"
                implement_options[display_text] = (i.id, i.year)

        col_tech1, col_tech2, col_tech3 = st.columns(3)

        with col_tech1:
            selected_machinery_display = st.selectbox("Техника", ["Не выбрано"] + list(machinery_options.keys()))

            if selected_machinery_display != "Не выбрано":
                selected_machinery_id, machine_year, machinery_type = machinery_options[selected_machinery_display]

                if selected_machinery_display in machinery_details:
                    ref_data = machinery_details[selected_machinery_display]
                    st.success(f"💪 {ref_data['мощность_лс']} л.с. | 🏷️ {ref_data['класс']} | 🚜 {ref_data['тип']}")
                else:
                    st.caption(f"Год выпуска: {machine_year or 'не указан'}")
            else:
                selected_machinery_id = None
                machine_year = None
                machinery_type = None

        with col_tech2:
            # Агрегат нужен только для тракторов
            needs_implement = machinery_type == 'tractor'
            if needs_implement:
                selected_implement_display = st.selectbox("Агрегат", ["Не выбрано"] + list(implement_options.keys()))

                if selected_implement_display != "Не выбрано":
                    selected_implement_id, implement_year = implement_options[selected_implement_display]
                else:
                    selected_implement_id = None
                    implement_year = None
            else:
                if machinery_type == 'self_propelled_mower':
                    st.info("✅ Самоходная косилка - агрегат не требуется")
                selected_implement_id = None
                implement_year = None

        with col_tech3:
            work_speed_kmh = st.number_input("Скорость (км/ч)", min_value=0.0, value=None, step=0.5)

        notes = st.text_area("Примечания")

        submitted = st.form_submit_button("✅ Зарегистрировать", use_container_width=True, type="primary")

        if submitted:
            try:
                operation = Operation(
                    farm_id=farm.id,
                    field_id=selected_field.id,
                    operation_type="mowing",
                    operation_date=operation_date,
                    end_date=end_date,
                    area_processed_ha=area_processed,
                    machine_id=selected_machinery_id,
                    implement_id=selected_implement_id,
                    machine_year=machine_year,
                    implement_year=implement_year,
                    work_speed_kmh=work_speed_kmh,
                    notes=notes
                )
                db.add(operation)
                db.flush()

                mowing_details = MowingDetails(
                    operation_id=operation.id,
                    crop=crop,
                    mowing_number=mowing_number,
                    yield_green_mass_t_ha=yield_green_mass,
                    yield_hay_t_ha=yield_hay,
                    moisture_pct=moisture_pct,
                    quality_class=quality_class if quality_class != "Не указан" else None,
                    harvest_phase=harvest_phase_code,
                    linked_operation_id=linked_operation_id,
                    plant_height_cm=plant_height,
                    stubble_height_cm=stubble_height
                )
                db.add(mowing_details)
                db.commit()

                phase_msg = "укос" if harvest_phase_code == "mowing" else "подбор валков"
                st.success(f"✅ {phase_msg.capitalize()} зарегистрирован! Обработано {area_processed} га")
                st.balloons()
                st.rerun()

            except Exception as e:
                db.rollback()
                st.error(f"❌ Ошибка: {str(e)}")

with tab2:
    st.subheader("История укосов")

    operations = db.query(Operation, Field, MowingDetails).join(Field).outerjoin(
        MowingDetails, Operation.id == MowingDetails.operation_id
    ).filter(
        Operation.operation_type == "mowing",
        Field.farm_id == farm.id
    ).order_by(Operation.operation_date.desc()).all()

    if operations:
        data = []
        for op, field, md in operations:
            phase_label = {"mowing": "Укос", "pickup": "Подбор"}.get(md.harvest_phase if md else None, "-")

            data.append({
                'Дата': op.operation_date.strftime('%Y-%m-%d'),
                'Поле': field.name or field.field_code,
                'Культура': md.crop if md else '-',
                'Укос №': md.mowing_number if md else '-',
                'Фаза': phase_label,
                'Зел. масса (т/га)': f"{md.yield_green_mass_t_ha:.1f}" if (md and md.yield_green_mass_t_ha) else '-',
                'Сено (т/га)': f"{md.yield_hay_t_ha:.1f}" if (md and md.yield_hay_t_ha) else '-',
                'Влажность (%)': f"{md.moisture_pct:.0f}" if (md and md.moisture_pct) else '-',
                'Класс': md.quality_class if (md and md.quality_class) else '-',
                'Площадь (га)': op.area_processed_ha
            })

        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

        # Статистика
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Всего операций", len(operations))
        with col2:
            total_area = sum([op.area_processed_ha for op, _, _ in operations if op.area_processed_ha])
            st.metric("Обработано всего", f"{total_area:,.1f} га")
        with col3:
            mowing_ops = [md for _, _, md in operations if md and md.harvest_phase == "mowing"]
            avg_green = sum([md.yield_green_mass_t_ha for md in mowing_ops if md.yield_green_mass_t_ha]) / len(mowing_ops) if mowing_ops else 0
            st.metric("Ср. зел. масса", f"{avg_green:.1f} т/га")
        with col4:
            pickup_ops = [md for _, _, md in operations if md and md.harvest_phase == "pickup"]
            avg_hay = sum([md.yield_hay_t_ha for md in pickup_ops if md.yield_hay_t_ha]) / len(pickup_ops) if pickup_ops else 0
            st.metric("Ср. урож. сена", f"{avg_hay:.1f} т/га")
    else:
        st.info("📭 История пуста")

# Sidebar
with st.sidebar:
    st.markdown("### ℹ️ Справка")
    st.info("""
    **Учет укоса** позволяет:
    - Регистрировать укосы многолетних трав
    - Учитывать двухфазную уборку (укос → подбор)
    - Отслеживать качество сена
    - Анализировать урожайность по укосам

    **Фазы уборки:**
    - **Укос** - скашивание и укладка в валки
    - **Подбор** - подбор высушенных валков

    **Типичные культуры:**
    Люцерна, Эспарцет, Донник, Клевер, Костер, Житняк
    """)
