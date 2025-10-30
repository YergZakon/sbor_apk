# Reference Loader Module

## 📚 Описание

Универсальный модуль для загрузки JSON-справочников в приложении АгроДанные КЗ.

Решает проблему загрузки справочников из разных путей при запуске Streamlit из различных директорий.

---

## ✨ Возможности

- ✅ **Робастная загрузка** - автоматически ищет файлы в 8+ возможных путях
- ✅ **Кеширование** - опционально кеширует данные для повышения производительности
- ✅ **Понятные ошибки** - показывает все проверенные пути при неудаче
- ✅ **Предопределенные функции** - готовые загрузчики для всех справочников
- ✅ **Типизация** - полная поддержка type hints

---

## 🚀 Быстрый старт

### Базовое использование

```python
from utils.reference_loader import load_fertilizers, load_crops

# Загрузка справочников
fertilizers = load_fertilizers()
crops = load_crops()

# Использование данных
for category, items in fertilizers.items():
    print(f"Категория: {category}")
    for name, details in items.items():
        print(f"  - {name}: N={details['N']}%, P={details['P']}%, K={details['K']}%")
```

### Использование в Streamlit страницах

**До:**
```python
# Старый способ - ненадежный
def load_fertilizers_reference():
    reference_path = Path(__file__).parent.parent / "data" / "fertilizers.json"
    try:
        with open(reference_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Справочник удобрений не найден!")
        return {}

fertilizers_ref = load_fertilizers_reference()
```

**После:**
```python
# Новый способ - робастный
from utils.reference_loader import load_fertilizers, load_tractors

fertilizers_ref = load_fertilizers()
tractors_ref = load_tractors()
```

---

## 📖 API Reference

### Универсальная функция

#### `load_reference(filename: str, show_error: bool = True) -> Dict[str, Any]`

Загрузка любого справочника по имени файла.

**Параметры:**
- `filename` (str) - имя JSON файла (например, "fertilizers.json")
- `show_error` (bool) - показывать ли ошибку в Streamlit при неудаче (по умолчанию True)

**Возвращает:**
- Dict[str, Any] - данные справочника или пустой словарь при ошибке

**Пример:**
```python
from utils.reference_loader import load_reference

# Загрузка кастомного справочника
custom_data = load_reference("my_custom_reference.json")

# Без показа ошибок (для опциональных справочников)
optional_data = load_reference("optional.json", show_error=False)
```

---

### Предопределенные загрузчики

#### Агрономические справочники

```python
from utils.reference_loader import (
    load_crops,        # Культуры
    load_fertilizers,  # Удобрения
    load_pesticides,   # СЗР
)

crops = load_crops()
fertilizers = load_fertilizers()
pesticides = load_pesticides()
```

#### Фитосанитарные справочники

```python
from utils.reference_loader import (
    load_diseases,  # Болезни
    load_pests,     # Вредители
    load_weeds,     # Сорняки
)

diseases = load_diseases()
pests = load_pests()
weeds = load_weeds()
```

#### Справочники техники

```python
from utils.reference_loader import (
    load_tractors,    # Тракторы
    load_combines,    # Комбайны
    load_implements,  # Орудия
)

# Опциональные справочники (без ошибок при отсутствии)
tractors = load_tractors()    # show_error=False по умолчанию
combines = load_combines()
implements = load_implements()
```

---

### Кешированная загрузка

Для повышения производительности можно использовать кешированную версию:

```python
from utils.reference_loader import load_reference_cached

# Данные будут закешированы на 1 час
fertilizers = load_reference_cached("fertilizers.json")
```

**Параметры кеширования:**
- TTL: 3600 секунд (1 час)
- Хранилище: Streamlit cache_data

---

## 🔍 Поддерживаемые пути поиска

Модуль автоматически ищет файлы в следующих директориях (в порядке приоритета):

1. `streamlit_app/data/` - основной путь
2. `streamlit_app/shared/data/` - shared справочники
3. `data/` - корневой data/
4. `shared/data/` - корневой shared/
5. И другие комбинации с учетом рабочей директории

---

## 🧪 Тестирование

Запустите тест для проверки всех справочников:

```bash
cd streamlit_app
python test_references.py
```

**Ожидаемый вывод:**
```
🧪 Тестирование загрузки справочников...

======================================================================
Справочник           Статус               Категорий       Всего элементов
======================================================================
Культуры             ✅ OK                 9               58
Удобрения            ✅ OK                 7               17
СЗР                  ✅ OK                 5               20
Болезни              ✅ OK                 4               24
Вредители            ✅ OK                 4               27
Сорняки              ✅ OK                 5               24
Тракторы             ✅ OK                 132             924
Комбайны             ✅ OK                 66              462
Орудия               ✅ OK                 187             1386
======================================================================

✅ Успешно загружено: 9/9 справочников
🎉 Все справочники загружены успешно!
```

---

## 📂 Структура справочников

Все справочники должны быть в формате JSON и находиться в одной из директорий:

```
farm_data_system/
├── streamlit_app/
│   ├── data/                    # ← Основная директория
│   │   ├── crops.json
│   │   ├── fertilizers.json
│   │   ├── pesticides.json
│   │   ├── diseases.json
│   │   ├── pests.json
│   │   ├── weeds.json
│   │   ├── tractors.json
│   │   ├── combines.json
│   │   └── implements.json
│   └── shared/
│       └── data/                # ← Альтернативная директория
│           └── ...
```

---

## 🐛 Troubleshooting

### Проблема: "Справочник не найден"

**Решение:**
1. Проверьте, что файл существует: `ls streamlit_app/data/fertilizers.json`
2. Проверьте кодировку файла (должна быть UTF-8)
3. Запустите тест: `python test_references.py`

### Проблема: "Ошибка парсинга JSON"

**Решение:**
1. Проверьте валидность JSON: `python -m json.tool < fertilizers.json`
2. Убедитесь в отсутствии BOM в файле
3. Проверьте синтаксис JSON (trailing commas, кавычки и т.д.)

---

## 🔄 Миграция существующего кода

### Шаг 1: Импорт

```python
# Было:
import json
from pathlib import Path

# Стало:
from utils.reference_loader import load_fertilizers, load_crops
```

### Шаг 2: Удаление старого кода

```python
# Было:
def load_fertilizers_reference():
    reference_path = Path(__file__).parent.parent / "data" / "fertilizers.json"
    try:
        with open(reference_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Справочник удобрений не найден!")
        return {}

fertilizers_ref = load_fertilizers_reference()

# Стало:
fertilizers_ref = load_fertilizers()
```

### Шаг 3: Очистка импортов

Удалите неиспользуемые импорты:
- `json` (если использовался только для справочников)
- `Path` (если использовался только для справочников)

---

## 📝 Changelog

### Version 1.0 (2025-10-30)

- ✅ Создан универсальный модуль загрузки справочников
- ✅ Добавлена поддержка 8+ путей поиска
- ✅ Реализовано кеширование для производительности
- ✅ Созданы предопределенные функции для всех справочников
- ✅ Добавлен тестовый скрипт
- ✅ Обновлены страницы: Fertilizers, Pesticides, Phytosanitary, Sowing

---

## 👥 Автор

АгроДанные КЗ - Farm Data System Team

---

## 📄 Лицензия

Internal use - Farm Data System v2.0
