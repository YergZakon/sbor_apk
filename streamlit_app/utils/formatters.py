"""
Formatters - Функции форматирования данных
"""
from datetime import datetime, date
from typing import Optional, Union


def format_date(date_value: Optional[Union[datetime, date, str]]) -> str:
    """Форматирование даты в строку"""
    if not date_value:
        return "-"

    if isinstance(date_value, str):
        try:
            date_value = datetime.strptime(date_value, "%Y-%m-%d")
        except:
            return date_value

    if isinstance(date_value, datetime):
        return date_value.strftime("%d.%m.%Y")
    elif isinstance(date_value, date):
        return date_value.strftime("%d.%m.%Y")

    return str(date_value)


def format_number(value: Optional[float], decimals: int = 1, unit: str = "") -> str:
    """Форматирование числа"""
    if value is None:
        return "-"

    try:
        formatted = f"{float(value):,.{decimals}f}"
        if unit:
            return f"{formatted} {unit}"
        return formatted
    except:
        return str(value)


def format_area(area_ha: Optional[float]) -> str:
    """Форматирование площади"""
    return format_number(area_ha, decimals=1, unit="га")


def format_yield(yield_t_ha: Optional[float]) -> str:
    """Форматирование урожайности"""
    return format_number(yield_t_ha, decimals=2, unit="т/га")


def format_percent(value: Optional[float]) -> str:
    """Форматирование процента"""
    return format_number(value, decimals=1, unit="%")


def format_money(amount: Optional[float], currency: str = "тг") -> str:
    """Форматирование денежной суммы"""
    if amount is None:
        return "-"

    try:
        formatted = f"{float(amount):,.0f}"
        return f"{formatted} {currency}"
    except:
        return str(amount)


def format_coordinates(lat: Optional[float], lon: Optional[float]) -> str:
    """Форматирование координат"""
    if not lat or not lon:
        return "Не указаны"

    return f"{lat:.6f}, {lon:.6f}"


def format_phone(phone: Optional[str]) -> str:
    """Форматирование телефона"""
    if not phone:
        return "-"

    # Попытка форматирования
    phone = str(phone).replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

    if phone.startswith("+7") and len(phone) == 12:
        return f"+7 ({phone[2:5]}) {phone[5:8]}-{phone[8:10]}-{phone[10:12]}"
    elif phone.startswith("8") and len(phone) == 11:
        return f"+7 ({phone[1:4]}) {phone[4:7]}-{phone[7:9]}-{phone[9:11]}"

    return phone


def format_operation_type(op_type: Optional[str]) -> str:
    """Форматирование типа операции"""
    operation_types_ru = {
        'sowing': '🌾 Посев',
        'fertilizing': '💊 Внесение удобрений',
        'spraying': '🛡️ Опрыскивание',
        'harvesting': '🚜 Уборка урожая'
    }

    return operation_types_ru.get(op_type, op_type or "-")


def format_field_code(field_code: Optional[str]) -> str:
    """Форматирование кода поля"""
    if not field_code:
        return "-"

    # field_001 -> Поле 001
    if field_code.startswith("field_"):
        number = field_code.replace("field_", "")
        return f"Поле {number}"

    return field_code


def truncate_text(text: Optional[str], max_length: int = 50) -> str:
    """Обрезание текста"""
    if not text:
        return "-"

    text = str(text)
    if len(text) <= max_length:
        return text

    return text[:max_length - 3] + "..."


def format_quality_class(quality_class: Optional[int]) -> str:
    """Форматирование класса качества зерна"""
    if not quality_class:
        return "-"

    classes = {
        1: "1 класс (высший)",
        2: "2 класс (хороший)",
        3: "3 класс (средний)",
        4: "4 класс (низкий)",
        5: "5 класс (фуражный)"
    }

    return classes.get(quality_class, f"{quality_class} класс")


def format_soil_type(soil_type: Optional[str]) -> str:
    """Форматирование типа почвы"""
    if not soil_type:
        return "Не указан"

    return soil_type


def format_boolean(value: Optional[bool], true_text: str = "Да", false_text: str = "Нет") -> str:
    """Форматирование булевого значения"""
    if value is None:
        return "-"

    return true_text if value else false_text


def get_color_by_value(value: float, thresholds: dict) -> str:
    """
    Получение цвета по значению и порогам

    Args:
        value: Значение для проверки
        thresholds: Словарь с порогами {'green': 70, 'orange': 40, 'red': 0}

    Returns:
        Цвет: 'green', 'orange', 'red', 'gray'
    """
    if value is None:
        return 'gray'

    if value >= thresholds.get('green', 70):
        return 'green'
    elif value >= thresholds.get('orange', 40):
        return 'orange'
    else:
        return 'red'


def format_with_color(value: float, thresholds: dict, formatter_func=None) -> tuple:
    """
    Форматирование значения с цветом

    Returns:
        (formatted_value, color)
    """
    if formatter_func:
        formatted = formatter_func(value)
    else:
        formatted = format_number(value)

    color = get_color_by_value(value, thresholds)

    return formatted, color


def format_npk(n: Optional[float], p: Optional[float], k: Optional[float]) -> str:
    """Форматирование NPK"""
    n_val = f"N{n:.0f}" if n else "N-"
    p_val = f"P{p:.0f}" if p else "P-"
    k_val = f"K{k:.0f}" if k else "K-"

    return f"{n_val}:{p_val}:{k_val}"


def format_list(items: list, separator: str = ", ", max_items: int = 5) -> str:
    """Форматирование списка в строку"""
    if not items:
        return "-"

    items_str = [str(item) for item in items]

    if len(items_str) <= max_items:
        return separator.join(items_str)
    else:
        visible = items_str[:max_items]
        remaining = len(items_str) - max_items
        return separator.join(visible) + f" ... (+{remaining})"
