"""
Data validation functions
"""
import re
from datetime import datetime, date
from typing import List, Tuple, Dict, Any
from modules.config import settings


class ValidationError(Exception):
    """Validation error exception"""
    pass


class DataValidator:
    """Data validation class"""

    @staticmethod
    def validate_bin(bin_number: str) -> Tuple[bool, str]:
        """Validate Kazakhstan BIN (Business Identification Number)"""
        if not bin_number:
            return False, "БИН обязателен"

        if len(bin_number) != 12:
            return False, "БИН должен содержать 12 цифр"

        if not bin_number.isdigit():
            return False, "БИН должен содержать только цифры"

        return True, ""

    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """Validate phone number"""
        if not phone:
            return False, "Телефон обязателен"

        pattern = r'^\+7\d{10}$'
        if not re.match(pattern, phone):
            return False, "Телефон должен быть в формате +7XXXXXXXXXX"

        return True, ""

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email address"""
        if not email:
            return True, ""  # Email is optional

        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(pattern, email):
            return False, "Неверный формат email"

        return True, ""

    @staticmethod
    def validate_coordinates(lat: float, lon: float) -> Tuple[bool, str]:
        """Validate GPS coordinates"""
        if lat is None or lon is None:
            return True, ""  # Coordinates are optional

        if not (-90 <= lat <= 90):
            return False, "Широта должна быть от -90 до 90"

        if not (-180 <= lon <= 180):
            return False, "Долгота должна быть от -180 до 180"

        # Check if coordinates are in Kazakhstan (rough bounds)
        if not (40 <= lat <= 56 and 46 <= lon <= 88):
            return False, "Координаты должны находиться на территории Казахстана"

        return True, ""

    @staticmethod
    def validate_area(area: float, max_area: float = None) -> Tuple[bool, str]:
        """Validate area in hectares"""
        if area is None:
            return False, "Площадь обязательна"

        if area <= 0:
            return False, "Площадь должна быть больше 0"

        max_limit = max_area or settings.MAX_FIELD_AREA
        if area > max_limit:
            return False, f"Площадь не может превышать {max_limit} га"

        return True, ""

    @staticmethod
    def validate_date(date_value: date) -> Tuple[bool, str]:
        """Validate date (simple version)"""
        if not date_value:
            return False, "Дата обязательна"

        if date_value > datetime.now().date():
            return False, "Дата не может быть в будущем"

        if date_value.year < 2000:
            return False, "Дата слишком старая"

        return True, ""

    @staticmethod
    def validate_date_range(date_value: date, min_year: int = None, max_year: int = None) -> Tuple[bool, str]:
        """Validate date is within reasonable range"""
        if not date_value:
            return False, "Дата обязательна"

        min_y = min_year or settings.MIN_YEAR
        max_y = max_year or settings.MAX_YEAR

        if date_value.year < min_y:
            return False, f"Год не может быть раньше {min_y}"

        if date_value.year > max_y:
            return False, f"Год не может быть позже {max_y}"

        if date_value > datetime.now().date():
            return False, "Дата не может быть в будущем"

        return True, ""

    @staticmethod
    def validate_ph(ph: float) -> Tuple[bool, str]:
        """Validate pH value"""
        if ph is None:
            return True, ""  # Optional

        min_ph, max_ph = settings.RANGES["ph"]
        if not (min_ph <= ph <= max_ph):
            return False, f"pH должен быть от {min_ph} до {max_ph}"

        return True, ""

    @staticmethod
    def validate_percentage(value: float, field_name: str = "Значение") -> Tuple[bool, str]:
        """Validate percentage value (0-100)"""
        if value is None:
            return True, ""  # Optional

        if not (0 <= value <= 100):
            return False, f"{field_name} должно быть от 0 до 100%"

        return True, ""

    @staticmethod
    def validate_yield(yield_value: float, crop: str = "wheat") -> Tuple[bool, str]:
        """Validate yield value based on crop type"""
        if yield_value is None:
            return False, "Урожайность обязательна"

        if yield_value < 0:
            return False, "Урожайность не может быть отрицательной"

        # Get range for specific crop or use default
        crop_lower = crop.lower()
        range_key = None

        if "пшениц" in crop_lower:
            range_key = "yield_wheat"
        elif "ячмен" in crop_lower:
            range_key = "yield_barley"
        elif "подсолнечник" in crop_lower:
            range_key = "yield_sunflower"
        elif "рапс" in crop_lower:
            range_key = "yield_rapeseed"

        if range_key and range_key in settings.RANGES:
            min_yield, max_yield = settings.RANGES[range_key]
            if yield_value > max_yield:
                return False, f"⚠️ Урожайность {yield_value} т/га очень высокая для {crop} (обычно до {max_yield} т/га). Проверьте правильность."

        return True, ""

    @staticmethod
    def validate_operation_sequence(field_id: int, operation_date: date, operation_type: str, db_session) -> Tuple[bool, str]:
        """Validate operation sequence (e.g., harvest should be after sowing)"""
        # This would query the database to check previous operations
        # Simplified version for now
        return True, ""

    @staticmethod
    def validate_ndvi(ndvi: float) -> Tuple[bool, str]:
        """Validate NDVI value"""
        if ndvi is None:
            return True, ""  # Optional

        min_ndvi, max_ndvi = settings.RANGES["ndvi"]
        if not (min_ndvi <= ndvi <= max_ndvi):
            return False, f"NDVI должен быть от {min_ndvi} до {max_ndvi}"

        return True, ""

    @staticmethod
    def validate_field_data(data: Dict[str, Any]) -> List[str]:
        """Validate complete field data"""
        errors = []
        warnings = []

        # Validate required fields
        if not data.get("field_code"):
            errors.append("Код поля обязателен")

        if not data.get("area_ha"):
            errors.append("Площадь поля обязательна")
        else:
            is_valid, msg = DataValidator.validate_area(data["area_ha"])
            if not is_valid:
                errors.append(msg)
            elif data["area_ha"] > 1000:
                warnings.append(f"⚠️ Площадь поля {data['area_ha']} га очень большая. Проверьте правильность.")

        # Validate coordinates
        if data.get("center_lat") and data.get("center_lon"):
            is_valid, msg = DataValidator.validate_coordinates(
                data["center_lat"], data["center_lon"]
            )
            if not is_valid:
                errors.append(msg)

        # Validate pH
        if data.get("ph_water"):
            is_valid, msg = DataValidator.validate_ph(data["ph_water"])
            if not is_valid:
                errors.append(msg)

        # Check for missing important data
        if not data.get("soil_type"):
            warnings.append("Рекомендуется указать тип почвы")

        if not data.get("last_analysis_year"):
            warnings.append("Рекомендуется провести агрохимический анализ")

        return errors, warnings

    @staticmethod
    def validate_farm_data(data: Dict[str, Any]) -> List[str]:
        """Validate complete farm data"""
        errors = []

        # Validate BIN
        is_valid, msg = DataValidator.validate_bin(data.get("bin", ""))
        if not is_valid:
            errors.append(msg)

        # Validate phone
        is_valid, msg = DataValidator.validate_phone(data.get("phone", ""))
        if not is_valid:
            errors.append(msg)

        # Validate email
        if data.get("email"):
            is_valid, msg = DataValidator.validate_email(data["email"])
            if not is_valid:
                errors.append(msg)

        # Validate areas
        if data.get("total_area") and data.get("arable_area"):
            if data["arable_area"] > data["total_area"]:
                errors.append("Обрабатываемая площадь не может превышать общую площадь")

        return errors

    @staticmethod
    def validate_harvest_data(data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Validate harvest data"""
        errors = []
        warnings = []

        # Validate yield
        if data.get("crop") and data.get("yield_t_ha"):
            is_valid, msg = DataValidator.validate_yield(
                data["crop"], data["yield_t_ha"]
            )
            if not is_valid:
                if "⚠️" in msg:
                    warnings.append(msg)
                else:
                    errors.append(msg)

        # Validate moisture
        if data.get("moisture_pct"):
            is_valid, msg = DataValidator.validate_percentage(
                data["moisture_pct"], "Влажность"
            )
            if not is_valid:
                errors.append(msg)
            elif data["moisture_pct"] > 20:
                warnings.append(f"⚠️ Влажность {data['moisture_pct']}% высокая, требуется сушка")

        # Validate protein (for wheat)
        if data.get("protein_pct") and "пшениц" in data.get("crop", "").lower():
            min_p, max_p = settings.RANGES["protein_wheat"]
            if not (min_p <= data["protein_pct"] <= max_p):
                warnings.append(f"⚠️ Белок {data['protein_pct']}% выходит за типичный диапазон {min_p}-{max_p}%")

        # Validate total yield calculation
        if data.get("yield_t_ha") and data.get("area_ha"):
            expected_total = data["yield_t_ha"] * data["area_ha"]
            if data.get("total_yield_t"):
                diff = abs(data["total_yield_t"] - expected_total)
                if diff > 0.5:  # Allow 0.5t difference
                    errors.append(
                        f"Валовой сбор {data['total_yield_t']} т не соответствует "
                        f"расчетному {expected_total:.1f} т (урожайность × площадь)"
                    )

        return errors, warnings


validator = DataValidator()
