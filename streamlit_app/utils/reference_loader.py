"""
Unified reference loader for JSON catalogs
Handles multiple possible file locations for robustness
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
import streamlit as st


def load_reference(filename: str, show_error: bool = True) -> Dict[str, Any]:
    """
    Загрузка справочника из JSON из нескольких возможных путей

    Args:
        filename: имя JSON файла (например, "fertilizers.json")
        show_error: показывать ли ошибку в Streamlit при неудаче

    Returns:
        Словарь с данными или пустой словарь при ошибке
    """
    # Определяем возможные пути поиска справочника
    candidate_paths = [
        # Относительно текущей страницы (работает для pages/)
        Path(__file__).parent.parent / "data" / filename,

        # Относительно корня streamlit_app
        Path(__file__).parent.parent / "streamlit_app" / "data" / filename,

        # Shared data directory
        Path(__file__).parent.parent / "shared" / "data" / filename,

        # Рабочая директория (откуда запущен streamlit)
        Path.cwd() / "data" / filename,
        Path.cwd() / "streamlit_app" / "data" / filename,
        Path.cwd() / "streamlit_app" / "shared" / "data" / filename,

        # Абсолютный путь через корень проекта
        Path(__file__).resolve().parent.parent.parent / "data" / filename,
        Path(__file__).resolve().parent.parent.parent / "shared" / "data" / filename,
    ]

    # Удаляем дубликаты и нормализуем пути
    candidate_paths = list(set(p.resolve() for p in candidate_paths))

    # Пытаемся загрузить из каждого возможного пути
    for path in candidate_paths:
        try:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Успешная загрузка - возвращаем данные
                    return data
        except json.JSONDecodeError as e:
            if show_error:
                st.error(f"❌ Ошибка парсинга JSON в {path.name}: {e}")
            return {}
        except Exception as e:
            # Игнорируем ошибки чтения (файл не существует и т.д.)
            continue

    # Если ни один путь не сработал, показываем ошибку
    if show_error:
        tried_paths = "\n".join(f"  - {p}" for p in candidate_paths[:5])  # Показываем первые 5
        st.error(
            f"❌ Справочник **{filename}** не найден!\n\n"
            f"Искали в:\n{tried_paths}\n\n"
            f"💡 Проверьте, что файл существует в `streamlit_app/data/` или `streamlit_app/shared/data/`"
        )

    return {}


def load_multiple_references(*filenames: str, show_error: bool = True) -> Dict[str, Dict[str, Any]]:
    """
    Загрузка нескольких справочников одновременно

    Args:
        *filenames: имена JSON файлов
        show_error: показывать ли ошибки

    Returns:
        Словарь {filename: data}
    """
    result = {}
    for filename in filenames:
        result[filename] = load_reference(filename, show_error=show_error)
    return result


# Предопределенные загрузчики для часто используемых справочников
def load_crops() -> Dict[str, Any]:
    """Загрузка справочника культур"""
    return load_reference("crops.json")


def load_fertilizers() -> Dict[str, Any]:
    """Загрузка справочника удобрений"""
    return load_reference("fertilizers.json")


def load_pesticides() -> Dict[str, Any]:
    """Загрузка справочника СЗР"""
    return load_reference("pesticides.json")


def load_diseases() -> Dict[str, Any]:
    """Загрузка справочника болезней"""
    return load_reference("diseases.json")


def load_pests() -> Dict[str, Any]:
    """Загрузка справочника вредителей"""
    return load_reference("pests.json")


def load_weeds() -> Dict[str, Any]:
    """Загрузка справочника сорняков"""
    return load_reference("weeds.json")


def load_tractors() -> Dict[str, Any]:
    """Загрузка справочника тракторов"""
    return load_reference("tractors.json", show_error=False)


def load_combines() -> Dict[str, Any]:
    """Загрузка справочника комбайнов"""
    return load_reference("combines.json", show_error=False)


def load_implements() -> Dict[str, Any]:
    """Загрузка справочника орудий"""
    return load_reference("implements.json", show_error=False)


# Кешированные версии для оптимизации производительности
@st.cache_data(ttl=3600)  # Кеш на 1 час
def load_reference_cached(filename: str) -> Dict[str, Any]:
    """Кешированная загрузка справочника"""
    return load_reference(filename, show_error=True)
