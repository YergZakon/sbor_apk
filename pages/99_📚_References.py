"""
Reference Data Management - Управление справочниками
Для администраторов: управление всеми справочниками системы
"""
import streamlit as st
import pandas as pd
import json
from pathlib import Path
from modules.database import SessionLocal
from modules.auth import require_admin, get_user_display_name
from datetime import datetime

st.set_page_config(page_title="Справочники", page_icon="📚", layout="wide")

# Проверка прав администратора
require_admin()

st.title("📚 Управление справочниками")
st.markdown("Редактирование справочных данных системы")

# Путь к справочникам
DATA_DIR = Path("data")

# Определение справочников
REFERENCES = {
    "crops": {
        "name": "🌾 Культуры и сорта",
        "file": "crops.json",
        "description": "Сельскохозяйственные культуры, сорта, нормы высева",
        "icon": "🌾"
    },
    "tractors": {
        "name": "🚜 Тракторы",
        "file": "tractors.json",
        "description": "Справочник тракторов по производителям и моделям",
        "icon": "🚜"
    },
    "combines": {
        "name": "🌾 Комбайны",
        "file": "combines.json",
        "description": "Справочник зерноуборочных комбайнов",
        "icon": "🌾"
    },
    "implements": {
        "name": "🔧 Агрегаты",
        "file": "implements.json",
        "description": "Прицепное и навесное оборудование",
        "icon": "🔧"
    },
    "pesticides": {
        "name": "🛡️ Пестициды",
        "file": "pesticides.json",
        "description": "Средства защиты растений (пестициды, фунгициды, гербициды)",
        "icon": "🛡️"
    },
    "fertilizers": {
        "name": "💊 Удобрения",
        "file": "fertilizers.json",
        "description": "Минеральные и органические удобрения",
        "icon": "💊"
    },
    "diseases": {
        "name": "🦠 Болезни растений",
        "file": "diseases.json",
        "description": "Болезни сельскохозяйственных культур",
        "icon": "🦠"
    },
    "pests": {
        "name": "🐛 Вредители",
        "file": "pests.json",
        "description": "Вредители сельскохозяйственных культур",
        "icon": "🐛"
    },
    "weeds": {
        "name": "🌿 Сорняки",
        "file": "weeds.json",
        "description": "Сорные растения",
        "icon": "🌿"
    }
}

# Sidebar - выбор справочника
with st.sidebar:
    st.markdown(f"### 👤 {get_user_display_name()}")
    st.markdown("---")
    st.markdown("### 📚 Выберите справочник")

    selected_ref = st.radio(
        "Справочник:",
        options=list(REFERENCES.keys()),
        format_func=lambda x: f"{REFERENCES[x]['icon']} {REFERENCES[x]['name'].split(' ', 1)[1]}"
    )

    st.markdown("---")
    st.markdown("### 📊 Статистика")

    # Подсчет записей в каждом справочнике
    for ref_key, ref_info in REFERENCES.items():
        file_path = DATA_DIR / ref_info['file']
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    count = len(data)
                    st.metric(ref_info['icon'], count, label=ref_info['name'].split(' ', 1)[1][:15])
            except:
                st.metric(ref_info['icon'], "Ошибка")

# Основная область
if selected_ref:
    ref_info = REFERENCES[selected_ref]
    file_path = DATA_DIR / ref_info['file']

    st.markdown(f"## {ref_info['name']}")
    st.markdown(f"*{ref_info['description']}*")
    st.markdown("---")

    # Проверка существования файла
    if not file_path.exists():
        st.error(f"❌ Файл справочника не найден: {file_path}")

        if st.button("➕ Создать новый справочник"):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            st.success("✅ Справочник создан!")
            st.rerun()
    else:
        # Загрузка данных
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reference_data = json.load(f)
        except Exception as e:
            st.error(f"❌ Ошибка загрузки: {str(e)}")
            reference_data = {}

        # Вкладки для разных действий
        tabs = st.tabs(["📋 Просмотр", "➕ Добавить", "✏️ Редактировать", "📥 Импорт/Экспорт"])

        # ========================================================================
        # ВКЛАДКА: ПРОСМОТР
        # ========================================================================
        with tabs[0]:
            st.markdown("### 📋 Текущие записи")

            if not reference_data:
                st.info("📭 Справочник пуст. Добавьте первую запись во вкладке 'Добавить'.")
            else:
                st.markdown(f"**Всего записей:** {len(reference_data)}")

                # Поиск
                search_query = st.text_input("🔍 Поиск", placeholder="Введите название для поиска...")

                # Фильтрация
                filtered_data = reference_data
                if search_query:
                    filtered_data = {k: v for k, v in reference_data.items()
                                   if search_query.lower() in k.lower()}

                if not filtered_data:
                    st.warning(f"Ничего не найдено по запросу: {search_query}")
                else:
                    # Отображение в виде expandable карточек
                    for idx, (key, value) in enumerate(filtered_data.items()):
                        with st.expander(f"{ref_info['icon']} **{key}**", expanded=idx < 3):
                            # Форматированный вывод JSON
                            st.json(value)

                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("📋 Копировать JSON", key=f"copy_{idx}"):
                                    st.code(json.dumps(value, ensure_ascii=False, indent=2), language="json")

                            with col2:
                                if st.button("🗑️ Удалить", key=f"delete_{idx}"):
                                    if st.session_state.get(f"confirm_delete_{idx}"):
                                        del reference_data[key]
                                        with open(file_path, 'w', encoding='utf-8') as f:
                                            json.dump(reference_data, f, ensure_ascii=False, indent=2)
                                        st.success(f"✅ Удалено: {key}")
                                        st.rerun()
                                    else:
                                        st.session_state[f"confirm_delete_{idx}"] = True
                                        st.warning("⚠️ Нажмите еще раз для подтверждения")

        # ========================================================================
        # ВКЛАДКА: ДОБАВИТЬ
        # ========================================================================
        with tabs[1]:
            st.markdown("### ➕ Добавить новую запись")

            with st.form("add_reference_form"):
                st.markdown("**Способ добавления:**")
                add_method = st.radio(
                    "Выберите способ",
                    ["Через форму (упрощенный)", "JSON (расширенный)"],
                    horizontal=True
                )

                if add_method == "Через форму (упрощенный)":
                    new_key = st.text_input("Название (ключ) *", placeholder="Например: Пшеница яровая")

                    # Упрощенная форма в зависимости от типа справочника
                    if selected_ref == "crops":
                        new_type = st.text_input("Тип культуры", placeholder="Зерновая")
                        new_varieties = st.text_area("Сорта (по одному на строку)", placeholder="Омская 36\nАстана 2")

                        new_data = {
                            "тип": new_type,
                            "сорта": [v.strip() for v in new_varieties.split('\n') if v.strip()]
                        }

                    elif selected_ref in ["tractors", "combines"]:
                        new_manufacturer = st.text_input("Производитель *")
                        new_model = st.text_input("Модель *")
                        new_power = st.number_input("Мощность (л.с.)", min_value=0, step=10)

                        new_data = {
                            "производитель": new_manufacturer,
                            "модель": new_model,
                            "мощность_лс": new_power
                        }

                    else:
                        st.info("💡 Для этого справочника используйте JSON-ввод")
                        new_data = {}

                else:  # JSON ввод
                    new_key = st.text_input("Название (ключ) *", placeholder="Уникальное название записи")
                    new_json = st.text_area(
                        "JSON данные *",
                        height=200,
                        placeholder='{\n  "поле1": "значение1",\n  "поле2": 123\n}'
                    )

                    # Попытка распарсить JSON
                    try:
                        new_data = json.loads(new_json) if new_json else {}
                    except json.JSONDecodeError as e:
                        st.error(f"❌ Ошибка в JSON: {str(e)}")
                        new_data = None

                submitted = st.form_submit_button("➕ Добавить запись", type="primary", use_container_width=True)

                if submitted:
                    if not new_key:
                        st.error("❌ Укажите название записи")
                    elif new_key in reference_data:
                        st.error(f"❌ Запись '{new_key}' уже существует. Используйте вкладку 'Редактировать'")
                    elif new_data is None:
                        st.error("❌ Исправьте ошибки в JSON")
                    elif not new_data:
                        st.error("❌ Данные не могут быть пустыми")
                    else:
                        try:
                            reference_data[new_key] = new_data
                            with open(file_path, 'w', encoding='utf-8') as f:
                                json.dump(reference_data, f, ensure_ascii=False, indent=2)
                            st.success(f"✅ Добавлено: {new_key}")
                            st.balloons()
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Ошибка сохранения: {str(e)}")

        # ========================================================================
        # ВКЛАДКА: РЕДАКТИРОВАТЬ
        # ========================================================================
        with tabs[2]:
            st.markdown("### ✏️ Редактировать запись")

            if not reference_data:
                st.info("📭 Нет записей для редактирования")
            else:
                edit_key = st.selectbox("Выберите запись", options=list(reference_data.keys()))

                if edit_key:
                    st.markdown(f"**Редактирование:** `{edit_key}`")

                    current_data = reference_data[edit_key]

                    with st.form("edit_reference_form"):
                        # JSON редактор
                        edited_json = st.text_area(
                            "JSON данные",
                            value=json.dumps(current_data, ensure_ascii=False, indent=2),
                            height=300
                        )

                        col1, col2 = st.columns(2)

                        with col1:
                            update_submitted = st.form_submit_button("💾 Сохранить изменения", type="primary", use_container_width=True)

                        with col2:
                            delete_submitted = st.form_submit_button("🗑️ Удалить запись", use_container_width=True)

                        if update_submitted:
                            try:
                                new_data = json.loads(edited_json)
                                reference_data[edit_key] = new_data

                                with open(file_path, 'w', encoding='utf-8') as f:
                                    json.dump(reference_data, f, ensure_ascii=False, indent=2)

                                st.success(f"✅ Обновлено: {edit_key}")
                                st.rerun()
                            except json.JSONDecodeError as e:
                                st.error(f"❌ Ошибка в JSON: {str(e)}")
                            except Exception as e:
                                st.error(f"❌ Ошибка сохранения: {str(e)}")

                        if delete_submitted:
                            try:
                                del reference_data[edit_key]
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    json.dump(reference_data, f, ensure_ascii=False, indent=2)
                                st.success(f"✅ Удалено: {edit_key}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Ошибка удаления: {str(e)}")

        # ========================================================================
        # ВКЛАДКА: ИМПОРТ/ЭКСПОРТ
        # ========================================================================
        with tabs[3]:
            st.markdown("### 📥 Импорт/Экспорт данных")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 📥 Импорт")
                st.info("Импортируйте данные из JSON файла. Существующие данные будут объединены.")

                uploaded_file = st.file_uploader("Выберите JSON файл", type=['json'])

                if uploaded_file:
                    try:
                        imported_data = json.load(uploaded_file)

                        st.json(imported_data)
                        st.markdown(f"**Записей в файле:** {len(imported_data)}")

                        import_mode = st.radio(
                            "Режим импорта:",
                            ["Объединить с существующими", "Заменить все данные"],
                            help="Объединить - добавит новые и обновит существующие. Заменить - удалит все текущие данные."
                        )

                        if st.button("🔄 Импортировать", type="primary"):
                            if import_mode == "Заменить все данные":
                                reference_data = imported_data
                            else:
                                reference_data.update(imported_data)

                            with open(file_path, 'w', encoding='utf-8') as f:
                                json.dump(reference_data, f, ensure_ascii=False, indent=2)

                            st.success(f"✅ Импортировано {len(imported_data)} записей!")
                            st.rerun()

                    except Exception as e:
                        st.error(f"❌ Ошибка импорта: {str(e)}")

            with col2:
                st.markdown("#### 📤 Экспорт")
                st.info("Экспортируйте текущий справочник в JSON файл для резервного копирования или обмена.")

                if reference_data:
                    # Подготовка JSON для скачивания
                    json_str = json.dumps(reference_data, ensure_ascii=False, indent=2)

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{selected_ref}_{timestamp}.json"

                    st.download_button(
                        label="📥 Скачать JSON",
                        data=json_str.encode('utf-8'),
                        file_name=filename,
                        mime="application/json",
                        use_container_width=True
                    )

                    st.markdown(f"**Записей:** {len(reference_data)}")
                    st.markdown(f"**Размер:** {len(json_str.encode('utf-8')) / 1024:.1f} KB")
                else:
                    st.warning("📭 Нет данных для экспорта")

# Footer
st.markdown("---")
st.markdown("💡 **Совет:** Используйте вкладку 'Импорт/Экспорт' для резервного копирования перед массовыми изменениями")
