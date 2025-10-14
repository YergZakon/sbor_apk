# 🚀 Быстрый старт

## ✅ Проблемы исправлены

Все ошибки в базе данных были исправлены:
- ✅ Обновлен импорт `declarative_base`
- ✅ Исправлены все `default=datetime.now` → `server_default=func.now()`
- ✅ База данных успешно инициализирована (184 KB)

## 📦 Установка

```bash
cd farm_data_system

# 1. Активировать виртуальное окружение (если есть)
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 2. Установить зависимости (если еще не установлены)
pip install -r requirements.txt

# 3. Инициализировать базу данных (уже сделано!)
python -m modules.database
```

## ▶️ Запуск приложения

```bash
streamlit run app.py
```

Приложение откроется в браузере: http://localhost:8501

## 📁 Структура БД

База данных содержит **18 таблиц**:

### Основные (11):
1. ✅ farms - хозяйства
2. ✅ fields - поля
3. ✅ operations - операции
4. ✅ sowing_details - детали посева
5. ✅ fertilizer_applications - удобрения
6. ✅ pesticide_applications - СЗР
7. ✅ harvest_data - уборка
8. ✅ agrochemical_analyses - агрохимия
9. ✅ economic_data - экономика
10. ✅ weather_data - метеоданные
11. ✅ machinery - техника

### Новые (4):
12. ✅ phytosanitary_monitoring - фитосанитария 🆕
13. ✅ gps_tracks - GPS-треки 🆕
14. ✅ machinery_equipment - GPS/RTK оборудование 🆕
15. ✅ satellite_data - спутниковые данные 🆕

### Справочные (3):
16. ✅ ref_crops
17. ✅ ref_fertilizers
18. ✅ ref_pesticides

## 🎯 Что дальше?

### Сейчас доступно:
- ✅ Главная страница с описанием системы
- ✅ База данных (18 таблиц)
- ✅ 6 справочников (150+ записей)
- ✅ Валидация данных
- ✅ Конфигурация

### Нужно создать (Этап 1 MVP):
- ⏳ Страницы приложения (pages/)
- ⏳ Dashboard с метриками
- ⏳ Управление полями
- ⏳ Импорт из Excel
- ⏳ Журнал операций

## 📚 Документация

- **[README.md](README.md)** - Полное руководство
- **[../plan.md](../plan.md)** - Обновленный план разработки
- **[../SUMMARY.md](../SUMMARY.md)** - Итоговый отчет

## 🐛 Решение проблем

### Ошибка: "Module not found"
```bash
pip install -r requirements.txt
```

### Ошибка: "Database locked"
Закройте все другие подключения к БД

### Ошибка: "streamlit command not found"
```bash
pip install streamlit
```

## 💡 Полезные команды

```bash
# Проверить таблицы в БД
python -c "from modules.database import Base, engine; print([t.name for t in Base.metadata.sorted_tables])"

# Очистить БД и создать заново
rm farm_data.db
python -m modules.database

# Запустить с отладкой
streamlit run app.py --logger.level=debug
```

## 🎉 Готово!

Система полностью готова к разработке страниц приложения.

**Текущая готовность MVP: ~40%**

Следующий шаг: создание страниц в папке `pages/`
