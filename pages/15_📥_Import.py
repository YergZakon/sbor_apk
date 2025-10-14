"""
Import - Импорт данных из Excel
Поддержка 10 типов файлов с валидацией
"""
import streamlit as st
import pandas as pd
import io
from datetime import datetime
from sqlalchemy.orm import Session
from modules.database import SessionLocal, Farm, Field, Operation, AgrochemicalAnalysis, EconomicData, HarvestData, SowingDetail, FertilizerApplication
from modules.validators import validator
from modules.config import settings

# Настройка страницы
st.set_page_config(page_title="Импорт данных", page_icon="📥", layout="wide")

# Заголовок
st.title("📥 Импорт данных из Excel")

st.markdown("""
Загрузите Excel-файлы для быстрого импорта данных в систему.
Поддерживаются стандартные шаблоны из папки `examples/`.
""")

# Получение сессии БД
db = SessionLocal()

try:
    # Проверка наличия хозяйства
    farm = db.query(Farm).first()

    if not farm:
        st.warning("⚠️ Рекомендуется сначала зарегистрировать хозяйство на главной странице")

    # ============================================================================
    # ВЫБОР ТИПА ДАННЫХ
    # ============================================================================

    st.markdown("### 📁 Выберите тип данных для импорта")

    data_types = {
        "01 - Общая информация хозяйства": {
            "description": "БИН, название, контакты, площади",
            "template": "01_Общая_информация_хозяйства.xlsx",
            "icon": "🏢"
        },
        "02 - Паспорт полей": {
            "description": "Поля с координатами и характеристиками",
            "template": "02_Паспорт_полей.xlsx",
            "icon": "🌱"
        },
        "03 - Агрохимические анализы": {
            "description": "Результаты анализов почвы",
            "template": "03_Агрохимические_анализы.xlsx",
            "icon": "🧪"
        },
        "04 - Журнал полевых работ": {
            "description": "История всех операций (посев, обработки)",
            "template": "04_Журнал_полевых_работ_2023_2025.xlsx",
            "icon": "📝"
        },
        "05 - Урожайность": {
            "description": "Данные уборки урожая по годам",
            "template": "05_Урожайность_сводная_2023_2025.xlsx",
            "icon": "🌾"
        },
        "06 - Экономические данные": {
            "description": "Затраты, доходы, рентабельность",
            "template": "06_Экономические_данные_2023_2025.xlsx",
            "icon": "💰"
        },
        "07 - Метеоданные": {
            "description": "Погодные данные (температура, осадки)",
            "template": "07_Метеоданные_2023_2025.xlsx",
            "icon": "🌡️"
        },
        "08 - Данные техники (GPS)": {
            "description": "GPS-треки техники",
            "template": "08_Данные_техники_2023_2025.xlsx",
            "icon": "📡"
        },
        "09 - Техническая оснащенность": {
            "description": "GPS/RTK оборудование",
            "template": "09_Техническая_оснащенность.xlsx",
            "icon": "🚜"
        },
        "10 - Спутниковые данные (NDVI)": {
            "description": "Индексы вегетации NDVI/EVI",
            "template": "10_Спутниковые_данные_NDVI_2023_2025.xlsx",
            "icon": "🛰️"
        }
    }

    # Отображение карточек типов данных
    cols = st.columns(2)

    for idx, (data_type, info) in enumerate(data_types.items()):
        with cols[idx % 2]:
            with st.container():
                st.markdown(f"### {info['icon']} {data_type}")
                st.caption(info['description'])
                st.caption(f"📄 Шаблон: `{info['template']}`")

    st.markdown("---")

    # ============================================================================
    # ЗАГРУЗКА ФАЙЛА
    # ============================================================================

    selected_type = st.selectbox(
        "Выберите тип данных",
        options=list(data_types.keys()),
        help="Тип данных должен соответствовать загружаемому файлу"
    )

    st.markdown(f"### {data_types[selected_type]['icon']} Загрузка: {selected_type}")

    uploaded_file = st.file_uploader(
        "Выберите Excel файл",
        type=['xlsx', 'xls'],
        help=f"Загрузите файл в формате {data_types[selected_type]['template']}"
    )

    if uploaded_file:
        try:
            # Чтение файла
            with st.spinner("Чтение файла..."):
                # Определение типа импорта
                if "01 - Общая информация" in selected_type:
                    # Файл с несколькими листами
                    excel_file = pd.ExcelFile(uploaded_file)
                    sheets = excel_file.sheet_names

                    st.success(f"✅ Файл прочитан успешно! Найдено листов: {len(sheets)}")

                    # Показать листы
                    st.markdown("#### 📋 Найденные листы:")
                    for sheet in sheets:
                        st.markdown(f"- {sheet}")

                    # Чтение листа "Идентификация"
                    if "Идентификация" in sheets:
                        df = pd.read_excel(uploaded_file, sheet_name="Идентификация")
                        st.markdown("#### Превью данных (Идентификация):")
                        st.dataframe(df.head(10), use_container_width=True)

                        # Валидация
                        st.markdown("#### ✅ Валидация данных")

                        errors = []
                        warnings = []

                        # Извлечение данных
                        data_dict = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))

                        bin_value = data_dict.get("БИН")
                        if bin_value and not pd.isna(bin_value):
                            is_valid, msg = validator.validate_bin(str(bin_value))
                            if not is_valid:
                                errors.append(f"БИН: {msg}")
                        else:
                            errors.append("БИН не указан или пустой")

                        phone_value = data_dict.get("Телефон")
                        if phone_value and not pd.isna(phone_value):
                            is_valid, msg = validator.validate_phone(str(phone_value))
                            if not is_valid:
                                errors.append(f"Телефон: {msg}")

                        # Показать результаты валидации
                        if errors:
                            st.error(f"❌ Найдено {len(errors)} ошибок:")
                            for error in errors:
                                st.error(f"  • {error}")
                        else:
                            st.success("✅ Критических ошибок не найдено!")

                        if warnings:
                            st.warning(f"⚠️ Предупреждения ({len(warnings)}):")
                            for warning in warnings:
                                st.warning(f"  • {warning}")

                        # Кнопка импорта
                        if not errors:
                            if st.button("📥 Импортировать данные хозяйства", type="primary"):
                                with st.spinner("Импорт данных..."):
                                    try:
                                        # Создание или обновление хозяйства
                                        existing_farm = db.query(Farm).filter(Farm.bin == str(bin_value)).first()

                                        if existing_farm:
                                            st.warning("⚠️ Хозяйство с таким БИН уже существует. Обновление данных...")
                                            farm_to_update = existing_farm
                                        else:
                                            farm_to_update = Farm(bin=str(bin_value))
                                            db.add(farm_to_update)

                                        # Обновление полей
                                        farm_to_update.name = data_dict.get("Полное наименование", "")
                                        farm_to_update.contact_person = data_dict.get("Контактное лицо (ФИО)")
                                        farm_to_update.phone = str(phone_value) if phone_value else None

                                        db.commit()
                                        st.success("✅ Данные хозяйства успешно импортированы!")
                                        st.balloons()

                                    except Exception as e:
                                        db.rollback()
                                        st.error(f"❌ Ошибка при импорте: {str(e)}")

                    else:
                        st.error("❌ Лист 'Идентификация' не найден в файле")

                elif "02 - Паспорт" in selected_type:
                    # Импорт полей
                    df = pd.read_excel(uploaded_file)

                    st.success(f"✅ Файл прочитан! Найдено строк: {len(df)}")

                    # Превью
                    st.markdown("#### Превью данных:")
                    st.dataframe(df.head(10), use_container_width=True)

                    # Валидация
                    st.markdown("#### ✅ Валидация данных")

                    errors = []
                    warnings = []

                    # Проверка обязательных колонок
                    required_cols = ['ID поля', 'Площадь (га)']
                    for col in required_cols:
                        if col not in df.columns:
                            errors.append(f"Отсутствует обязательная колонка: {col}")

                    if not errors:
                        # Проверка данных
                        valid_rows = 0
                        for idx, row in df.iterrows():
                            if pd.isna(row.get('ID поля')) or pd.isna(row.get('Площадь (га)')):
                                continue

                            valid_rows += 1

                            # Валидация площади
                            area = row.get('Площадь (га)')
                            if area and area > 0:
                                is_valid, msg = validator.validate_area(area)
                                if not is_valid:
                                    errors.append(f"Строка {idx + 2}: {msg}")

                        st.info(f"ℹ️ Найдено валидных строк для импорта: {valid_rows}")

                    # Показать результаты
                    if errors:
                        st.error(f"❌ Найдено ошибок: {len(errors)}")
                        for error in errors[:10]:  # Показать первые 10
                            st.error(f"  • {error}")
                        if len(errors) > 10:
                            st.caption(f"... и еще {len(errors) - 10} ошибок")
                    else:
                        st.success("✅ Данные готовы к импорту!")

                    if warnings:
                        st.warning(f"⚠️ Предупреждения: {len(warnings)}")
                        for warning in warnings[:5]:
                            st.warning(f"  • {warning}")

                    # Кнопка импорта
                    if not errors and valid_rows > 0:
                        if st.button("📥 Импортировать поля", type="primary"):
                            with st.spinner(f"Импорт {valid_rows} полей..."):
                                try:
                                    if not farm:
                                        st.error("❌ Сначала импортируйте данные хозяйства (тип 01)")
                                        st.stop()

                                    imported_count = 0

                                    for idx, row in df.iterrows():
                                        if pd.isna(row.get('ID поля')) or pd.isna(row.get('Площадь (га)')):
                                            continue

                                        field_code = str(row['ID поля'])
                                        area = float(row['Площадь (га)'])

                                        # Проверка существования
                                        existing = db.query(Field).filter(Field.field_code == field_code).first()

                                        if not existing:
                                            new_field = Field(
                                                farm_id=farm.id,
                                                field_code=field_code,
                                                name=row.get('Название поля') if not pd.isna(row.get('Название поля')) else None,
                                                area_ha=area,
                                                cadastral_number=row.get('Кадастровый номер') if not pd.isna(row.get('Кадастровый номер')) else None,
                                                center_lat=row.get('Центроид широта') if not pd.isna(row.get('Центроид широта')) else None,
                                                center_lon=row.get('Центроид долгота') if not pd.isna(row.get('Центроид долгота')) else None,
                                                soil_type=row.get('Тип почвы') if not pd.isna(row.get('Тип почвы')) else None,
                                                ph_water=row.get('pH водн') if not pd.isna(row.get('pH водн')) else None,
                                                humus_pct=row.get('Гумус (%)') if not pd.isna(row.get('Гумус (%)')) else None,
                                                p2o5_mg_kg=row.get('P2O5 (мг/кг)') if not pd.isna(row.get('P2O5 (мг/кг)')) else None,
                                                k2o_mg_kg=row.get('K2O (мг/кг)') if not pd.isna(row.get('K2O (мг/кг)')) else None,
                                            )
                                            db.add(new_field)
                                            imported_count += 1

                                    db.commit()
                                    st.success(f"✅ Успешно импортировано {imported_count} полей!")
                                    st.balloons()

                                    # Ссылка на просмотр
                                    if st.button("🌱 Перейти к полям"):
                                        st.switch_page("pages/2_🌱_Fields.py")

                                except Exception as e:
                                    db.rollback()
                                    st.error(f"❌ Ошибка при импорте: {str(e)}")

                elif "03 - Агрохимические" in selected_type:
                    # Импорт агрохимических анализов
                    df = pd.read_excel(uploaded_file)

                    st.success(f"✅ Файл прочитан! Найдено строк: {len(df)}")

                    # Превью
                    st.markdown("#### Превью данных:")
                    st.dataframe(df.head(10), use_container_width=True)

                    # Валидация
                    st.markdown("#### ✅ Валидация данных")

                    errors = []
                    warnings = []

                    # Проверка обязательных колонок
                    required_cols = ['ID поля', 'Дата анализа']
                    for col in required_cols:
                        if col not in df.columns:
                            errors.append(f"Отсутствует обязательная колонка: {col}")

                    if not errors:
                        valid_rows = 0
                        for idx, row in df.iterrows():
                            if pd.isna(row.get('ID поля')) or pd.isna(row.get('Дата анализа')):
                                continue

                            valid_rows += 1

                            # Валидация pH
                            ph = row.get('pH водн')
                            if ph and not pd.isna(ph):
                                is_valid, msg = validator.validate_ph(float(ph))
                                if not is_valid:
                                    warnings.append(f"Строка {idx + 2}: {msg}")

                        st.info(f"ℹ️ Найдено валидных строк: {valid_rows}")

                    # Показать результаты
                    if errors:
                        st.error(f"❌ Найдено ошибок: {len(errors)}")
                        for error in errors:
                            st.error(f"  • {error}")
                    else:
                        st.success("✅ Данные готовы к импорту!")

                    if warnings:
                        st.warning(f"⚠️ Предупреждения: {len(warnings)}")
                        for warning in warnings[:5]:
                            st.warning(f"  • {warning}")

                    # Кнопка импорта
                    if not errors and valid_rows > 0:
                        if st.button("📥 Импортировать анализы", type="primary"):
                            with st.spinner(f"Импорт {valid_rows} анализов..."):
                                try:
                                    if not farm:
                                        st.error("❌ Сначала импортируйте данные хозяйства (тип 01)")
                                        st.stop()

                                    imported_count = 0

                                    for idx, row in df.iterrows():
                                        if pd.isna(row.get('ID поля')) or pd.isna(row.get('Дата анализа')):
                                            continue

                                        field_code = str(row['ID поля'])
                                        field = db.query(Field).filter(Field.field_code == field_code).first()

                                        if not field:
                                            st.warning(f"⚠️ Поле {field_code} не найдено, пропуск...")
                                            continue

                                        # Парсинг даты
                                        analysis_date = pd.to_datetime(row['Дата анализа']).date()

                                        # Создание операции
                                        operation = Operation(
                                            farm_id=farm.id,
                                            field_id=field.id,
                                            operation_type="soil_analysis",
                                            operation_date=analysis_date,
                                            area_processed_ha=field.area_ha
                                        )
                                        db.add(operation)
                                        db.flush()

                                        # Создание анализа
                                        analysis = AgrochemicalAnalysis(
                                            operation_id=operation.id,
                                            sample_depth_cm=row.get('Глубина отбора (см)') if not pd.isna(row.get('Глубина отбора (см)')) else None,
                                            ph_water=row.get('pH водн') if not pd.isna(row.get('pH водн')) else None,
                                            ph_salt=row.get('pH сол') if not pd.isna(row.get('pH сол')) else None,
                                            humus_percent=row.get('Гумус (%)') if not pd.isna(row.get('Гумус (%)')) else None,
                                            nitrogen_total_percent=row.get('N общий (%)') if not pd.isna(row.get('N общий (%)')) else None,
                                            p2o5_mg_kg=row.get('P2O5 (мг/кг)') if not pd.isna(row.get('P2O5 (мг/кг)')) else None,
                                            k2o_mg_kg=row.get('K2O (мг/кг)') if not pd.isna(row.get('K2O (мг/кг)')) else None,
                                            mobile_s_mg_kg=row.get('S подв. (мг/кг)') if not pd.isna(row.get('S подв. (мг/кг)')) else None
                                        )
                                        db.add(analysis)
                                        imported_count += 1

                                    db.commit()
                                    st.success(f"✅ Успешно импортировано {imported_count} анализов!")
                                    st.balloons()

                                except Exception as e:
                                    db.rollback()
                                    st.error(f"❌ Ошибка при импорте: {str(e)}")

                elif "04 - Журнал" in selected_type:
                    # Импорт журнала работ
                    df = pd.read_excel(uploaded_file)

                    st.success(f"✅ Файл прочитан! Найдено строк: {len(df)}")

                    # Превью
                    st.markdown("#### Превью данных:")
                    st.dataframe(df.head(10), use_container_width=True)

                    # Валидация
                    st.markdown("#### ✅ Валидация данных")

                    errors = []
                    valid_rows = 0

                    # Проверка обязательных колонок
                    required_cols = ['ID поля', 'Дата', 'Тип операции']
                    for col in required_cols:
                        if col not in df.columns:
                            errors.append(f"Отсутствует обязательная колонка: {col}")

                    if not errors:
                        for idx, row in df.iterrows():
                            if pd.isna(row.get('ID поля')) or pd.isna(row.get('Дата')) or pd.isna(row.get('Тип операции')):
                                continue
                            valid_rows += 1

                        st.info(f"ℹ️ Найдено валидных строк: {valid_rows}")

                    # Показать результаты
                    if errors:
                        st.error(f"❌ Найдено ошибок: {len(errors)}")
                        for error in errors:
                            st.error(f"  • {error}")
                    else:
                        st.success("✅ Данные готовы к импорту!")

                    # Кнопка импорта
                    if not errors and valid_rows > 0:
                        if st.button("📥 Импортировать операции", type="primary"):
                            with st.spinner(f"Импорт {valid_rows} операций..."):
                                try:
                                    if not farm:
                                        st.error("❌ Сначала импортируйте данные хозяйства (тип 01)")
                                        st.stop()

                                    imported_count = 0
                                    operation_type_map = {
                                        "Посев": "sowing",
                                        "Внесение удобрений": "fertilizing",
                                        "Опрыскивание": "spraying",
                                        "Уборка": "harvest"
                                    }

                                    for idx, row in df.iterrows():
                                        if pd.isna(row.get('ID поля')) or pd.isna(row.get('Дата')) or pd.isna(row.get('Тип операции')):
                                            continue

                                        field_code = str(row['ID поля'])
                                        field = db.query(Field).filter(Field.field_code == field_code).first()

                                        if not field:
                                            continue

                                        # Парсинг даты
                                        op_date = pd.to_datetime(row['Дата']).date()
                                        op_type_ru = str(row['Тип операции'])
                                        op_type = operation_type_map.get(op_type_ru, "other")

                                        # Создание операции
                                        operation = Operation(
                                            farm_id=farm.id,
                                            field_id=field.id,
                                            operation_type=op_type,
                                            operation_date=op_date,
                                            area_processed_ha=row.get('Площадь (га)') if not pd.isna(row.get('Площадь (га)')) else field.area_ha,
                                            notes=row.get('Примечание') if not pd.isna(row.get('Примечание')) else None
                                        )
                                        db.add(operation)
                                        imported_count += 1

                                    db.commit()
                                    st.success(f"✅ Успешно импортировано {imported_count} операций!")
                                    st.balloons()

                                except Exception as e:
                                    db.rollback()
                                    st.error(f"❌ Ошибка при импорте: {str(e)}")

                elif "05 - Урожайность" in selected_type:
                    # Импорт урожайности
                    df = pd.read_excel(uploaded_file)

                    st.success(f"✅ Файл прочитан! Найдено строк: {len(df)}")

                    # Превью
                    st.markdown("#### Превью данных:")
                    st.dataframe(df.head(10), use_container_width=True)

                    # Валидация
                    st.markdown("#### ✅ Валидация данных")

                    errors = []
                    valid_rows = 0

                    # Проверка обязательных колонок
                    required_cols = ['ID поля', 'Год', 'Культура', 'Урожайность (т/га)']
                    for col in required_cols:
                        if col not in df.columns:
                            errors.append(f"Отсутствует обязательная колонка: {col}")

                    if not errors:
                        for idx, row in df.iterrows():
                            if pd.isna(row.get('ID поля')) or pd.isna(row.get('Год')) or pd.isna(row.get('Урожайность (т/га)')):
                                continue

                            valid_rows += 1

                            # Валидация урожайности
                            yield_val = row.get('Урожайность (т/га)')
                            if yield_val:
                                is_valid, msg = validator.validate_yield(float(yield_val), "wheat")
                                if not is_valid:
                                    errors.append(f"Строка {idx + 2}: {msg}")

                        st.info(f"ℹ️ Найдено валидных строк: {valid_rows}")

                    # Показать результаты
                    if errors:
                        st.error(f"❌ Найдено ошибок: {len(errors)}")
                        for error in errors[:10]:
                            st.error(f"  • {error}")
                    else:
                        st.success("✅ Данные готовы к импорту!")

                    # Кнопка импорта
                    if not errors and valid_rows > 0:
                        if st.button("📥 Импортировать урожайность", type="primary"):
                            with st.spinner(f"Импорт {valid_rows} записей..."):
                                try:
                                    if not farm:
                                        st.error("❌ Сначала импортируйте данные хозяйства (тип 01)")
                                        st.stop()

                                    imported_count = 0

                                    for idx, row in df.iterrows():
                                        if pd.isna(row.get('ID поля')) or pd.isna(row.get('Год')) or pd.isna(row.get('Урожайность (т/га)')):
                                            continue

                                        field_code = str(row['ID поля'])
                                        field = db.query(Field).filter(Field.field_code == field_code).first()

                                        if not field:
                                            continue

                                        # Парсинг данных
                                        year = int(row['Год'])
                                        # Предполагаем дату уборки - 15 августа указанного года
                                        harvest_date = datetime(year, 8, 15).date()

                                        yield_t_ha = float(row['Урожайность (т/га)'])
                                        area = row.get('Площадь (га)') if not pd.isna(row.get('Площадь (га)')) else field.area_ha
                                        total_yield = yield_t_ha * area

                                        # Создание операции
                                        operation = Operation(
                                            farm_id=farm.id,
                                            field_id=field.id,
                                            operation_type="harvest",
                                            operation_date=harvest_date,
                                            area_processed_ha=area
                                        )
                                        db.add(operation)
                                        db.flush()

                                        # Создание данных уборки
                                        harvest = HarvestData(
                                            operation_id=operation.id,
                                            crop=row.get('Культура') if not pd.isna(row.get('Культура')) else "Не указано",
                                            variety=row.get('Сорт') if not pd.isna(row.get('Сорт')) else None,
                                            yield_t_ha=yield_t_ha,
                                            total_yield_t=total_yield,
                                            moisture_percent=row.get('Влажность (%)') if not pd.isna(row.get('Влажность (%)')) else None,
                                            protein_percent=row.get('Белок (%)') if not pd.isna(row.get('Белок (%)')) else None,
                                            gluten_percent=row.get('Клейковина (%)') if not pd.isna(row.get('Клейковина (%)')) else None
                                        )
                                        db.add(harvest)
                                        imported_count += 1

                                    db.commit()
                                    st.success(f"✅ Успешно импортировано {imported_count} записей урожайности!")
                                    st.balloons()

                                except Exception as e:
                                    db.rollback()
                                    st.error(f"❌ Ошибка при импорте: {str(e)}")

                else:
                    # Общий импорт для других типов
                    df = pd.read_excel(uploaded_file)

                    st.success(f"✅ Файл прочитан! Найдено строк: {len(df)}, колонок: {len(df.columns)}")

                    # Превью
                    st.markdown("#### Превью данных:")
                    st.dataframe(df.head(20), use_container_width=True)

                    st.info("""
                    💡 **Полная поддержка импорта для этого типа данных будет добавлена в следующей версии.**

                    Сейчас доступен импорт:
                    - ✅ Общая информация хозяйства (тип 01)
                    - ✅ Паспорт полей (тип 02)
                    - ✅ Агрохимические анализы (тип 03)
                    - ✅ Журнал полевых работ (тип 04)
                    - ✅ Урожайность (тип 05)

                    Остальные типы в разработке.
                    """)

        except Exception as e:
            st.error(f"❌ Ошибка при чтении файла: {str(e)}")
            st.exception(e)

    st.markdown("---")

    # ============================================================================
    # ИНФОРМАЦИЯ О ШАБЛОНАХ
    # ============================================================================

    st.markdown("### 📚 Информация о шаблонах")

    with st.expander("Где найти шаблоны?"):
        st.markdown("""
        Шаблоны Excel находятся в папке `examples/` в корне проекта:

        ```
        fsai/examples/
        ├── 01_Общая_информация_хозяйства.xlsx
        ├── 02_Паспорт_полей.xlsx
        ├── 03_Агрохимические_анализы.xlsx
        └── ... (всего 10 файлов)
        ```

        **Рекомендуемый порядок импорта:**
        1. Общая информация хозяйства (01)
        2. Паспорт полей (02)
        3. Агрохимические анализы (03)
        4. Журнал полевых работ (04)
        5. Остальные данные по необходимости
        """)

    with st.expander("Требования к файлам"):
        st.markdown("""
        **Формат файлов:**
        - Excel 2007+ (.xlsx) или Excel 97-2003 (.xls)
        - Кодировка: UTF-8
        - Максимальный размер: 50 МБ

        **Структура данных:**
        - Названия колонок должны совпадать с шаблоном
        - Первая строка - заголовки
        - Обязательные поля не должны быть пустыми
        - Даты в формате YYYY-MM-DD или DD.MM.YYYY

        **Валидация:**
        - БИН: 12 цифр
        - Телефон: +7XXXXXXXXXX
        - Координаты: в пределах Казахстана
        - Площади: положительные числа
        - pH: 4.0-9.5
        """)

finally:
    db.close()

# Sidebar
with st.sidebar:
    st.markdown("### ℹ️ Справка")
    st.info("""
    **Импорт данных** позволяет быстро загрузить существующие данные из Excel.

    **Поддерживаемые типы:**
    - ✅ Общая информация (01)
    - ✅ Паспорт полей (02)
    - ✅ Агрохимия (03)
    - ✅ Журнал работ (04)
    - ✅ Урожайность (05)
    - ⏳ Остальные в разработке

    **Процесс импорта:**
    1. Выберите тип данных
    2. Загрузите Excel файл
    3. Проверьте валидацию
    4. Импортируйте данные
    """)

    st.markdown("### 🎯 Рекомендации")
    st.markdown("""
    - Используйте оригинальные шаблоны
    - Проверьте данные перед импортом
    - Делайте резервные копии
    - Импортируйте поэтапно
    """)

    st.markdown("### 📞 Помощь")
    st.markdown("""
    Если возникли проблемы с импортом:
    - Проверьте формат файла
    - Убедитесь в корректности данных
    - Обратитесь в поддержку
    """)
