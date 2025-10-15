"""
АгроДанные КЗ - Система сбора сельскохозяйственных данных
Главная страница приложения
"""
import streamlit as st
from modules.config import settings
from modules.database import init_db
from modules.auth_widget import show_auth_widget
import os

# Настройка страницы
st.set_page_config(
    page_title=settings.APP_NAME,
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Инициализация БД при первом запуске
if not os.path.exists("farm_data.db"):
    with st.spinner("Инициализация базы данных..."):
        init_db()
        st.success("База данных успешно создана!")

# Стили
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2e7d32;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #558b2f;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f1f8e9;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2e7d32;
    }
    .info-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Заголовок
st.markdown('<div class="main-header">🌾 АгроДанные КЗ</div>', unsafe_allow_html=True)
st.markdown(
    '<p style="text-align: center; font-size: 1.2rem; color: #666;">Система сбора данных для ML в АПК Казахстана</p>',
    unsafe_allow_html=True
)

# Основная информация
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📊 О системе")
    st.info("""
    **Цель:** Сбор качественных сельскохозяйственных данных с полнотой >70%
    для последующего использования в ML моделях

    **Регион:** Акмолинская область, Казахстан

    **Целевые пользователи:**
    - Фермеры и агрономы
    - Районные управления
    - Аналитики и data scientists
    """)

with col2:
    st.markdown("### 🎯 Ключевые метрики")
    st.success("""
    **Целевая полнота данных:** 70%+

    **ML-готовность:** 90%

    **Охват:**
    - 10+ типов данных
    - 16 модулей ввода
    - GPS-телематика
    - Спутниковые данные
    """)

with col3:
    st.markdown("### 🚀 Быстрый старт")
    st.warning("""
    **Шаг 1:** Регистрация хозяйства

    **Шаг 2:** Добавление полей

    **Шаг 3:** Ввод операций

    **Шаг 4:** Импорт существующих данных (Excel)

    **Шаг 5:** Анализ и экспорт
    """)

# Разделитель
st.markdown("---")

# Модули системы
st.markdown('<div class="sub-header">📦 Модули системы</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("#### 🏠 Основные")
    st.markdown("""
    - Dashboard
    - Управление полями
    - Журнал операций
    - Аналитика
    """)

with col2:
    st.markdown("#### 🌱 Агротехнические")
    st.markdown("""
    - Посев
    - Удобрения
    - Средства защиты
    - Уборка урожая
    """)

with col3:
    st.markdown("#### 🔬 Мониторинг")
    st.markdown("""
    - Агрохимия почвы
    - Фитосанитария
    - Метеоданные
    - Спутниковые данные
    """)

with col4:
    st.markdown("#### 🚜 Техника и экономика")
    st.markdown("""
    - Учет техники
    - GPS-треки
    - Экономика
    - Импорт данных
    """)

# Разделитель
st.markdown("---")

# Новые возможности
st.markdown('<div class="sub-header">✨ Новые возможности</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🐛 Фитосанитарный мониторинг")
    st.markdown("""
    **Новый модуль** для учета болезней, вредителей и сорняков:
    - Еженедельные обследования полей
    - База из 50+ вредных объектов
    - Загрузка фото для Computer Vision
    - GPS-координаты очагов
    - Контроль порогов вредоносности
    - Оценка эффективности мер борьбы
    """)

    st.markdown("#### 🛰️ Спутниковые данные")
    st.markdown("""
    **Автоматизация** получения данных дистанционного зондирования:
    - Интеграция с Sentinel Hub API
    - Автозагрузка NDVI и EVI
    - Временные ряды индексов
    - Корреляция с урожайностью
    - Детекция аномалий
    """)

with col2:
    st.markdown("#### 📡 GPS-телематика")
    st.markdown("""
    **Контроль качества** полевых работ:
    - Импорт GPS-треков (.gpx, .shp, CSV)
    - Визуализация маршрутов техники
    - Анализ покрытия полей
    - Контроль перекрытий и пропусков
    - Учет GPS/RTK оборудования
    """)

    st.markdown("#### 📥 Импорт из Excel")
    st.markdown("""
    **Быстрая загрузка** существующих данных:
    - Поддержка 10 типов файлов
    - Валидация перед импортом
    - Превью данных
    - Детальный отчет об ошибках
    - Сопоставление колонок
    """)

# Разделитель
st.markdown("---")

# Справочная информация
st.markdown('<div class="sub-header">📚 Справочная информация</div>', unsafe_allow_html=True)

with st.expander("📖 Встроенные справочники"):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Культуры и сорта**")
        st.markdown("- 9 культур")
        st.markdown("- 40+ сортов")
        st.markdown("- Нормы высева")
        st.markdown("- Потребность в NPK")

    with col2:
        st.markdown("**Агрохимикаты**")
        st.markdown("- 17 удобрений")
        st.markdown("- 25+ СЗР")
        st.markdown("- Действующие вещества")
        st.markdown("- Нормы применения")

    with col3:
        st.markdown("**Вредные объекты**")
        st.markdown("- 30+ болезней")
        st.markdown("- 35+ вредителей")
        st.markdown("- 40+ сорняков")
        st.markdown("- Пороги вредоносности")

with st.expander("🔧 Технические возможности"):
    st.markdown("""
    **База данных:**
    - 15+ таблиц данных
    - 4+ справочные таблицы
    - SQLite (разработка) / PostgreSQL (production)
    - Автоматическая валидация

    **Экспорт данных:**
    - Excel (все форматы)
    - CSV
    - PDF-отчеты
    - ML-готовые датасеты

    **Валидация:**
    - 3 уровня проверки
    - Диапазоны значений
    - Логическая согласованность
    - Предупреждения и рекомендации

    **Производительность:**
    - Кэширование данных
    - Пакетная обработка
    - Офлайн-режим
    """)

with st.expander("📊 ML-готовность данных"):
    st.markdown("""
    Система обеспечивает подготовку данных для следующих ML-моделей:

    **1. Прогнозирование урожайности** ✅
    - Агрометеоданные
    - История урожайности
    - Агрохимические показатели
    - Спутниковые индексы (NDVI/EVI)

    **2. Оптимизация удобрений** ✅
    - Агрохимические анализы
    - Потребности культур
    - История внесения
    - Экономические показатели

    **3. Детекция болезней** ✅ NEW!
    - Фитосанитарный мониторинг
    - Фото для Computer Vision
    - Погодные условия
    - История поражений

    **4. Экономическая оптимизация** ✅
    - Структура затрат
    - Рентабельность
    - Сравнение культур
    - Сценарное моделирование
    """)

# Подвал
st.markdown("---")
st.markdown(
    f'<p style="text-align: center; color: #999;">Версия {settings.VERSION} | © 2025 АгроДанные КЗ</p>',
    unsafe_allow_html=True
)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/200x100/2e7d32/ffffff?text=АгроДанные", use_container_width=True)

    # Виджет авторизации
    show_auth_widget()

    st.markdown("---")
    st.markdown("### 🎯 Навигация")
    st.info("""
    Используйте меню слева для перехода к различным разделам системы.
    """)

    st.markdown("### 📞 Поддержка")
    st.markdown("""
    **Email:** support@agrodata.kz

    **Телефон:** +7 (XXX) XXX-XX-XX

    **Документация:** [docs.agrodata.kz](https://docs.agrodata.kz)
    """)

    st.markdown("### 📈 Статистика")
    st.metric("Версия системы", settings.VERSION)
    st.metric("Справочников", "8")
    st.metric("Модулей", "18")
