"""
Application configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings"""

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./farm_data.db")

    # App settings
    APP_NAME = os.getenv("APP_NAME", "АгроДанные КЗ")
    VERSION = os.getenv("VERSION", "1.0.0")
    DEBUG = os.getenv("DEBUG", "True") == "True"

    # Limits and validation
    MAX_FIELD_AREA = 30000  # га
    MAX_YIELD = 10.0  # т/га для зерновых
    MIN_YEAR = 2020
    MAX_YEAR = 2030

    # Validation thresholds
    CRITICAL_COMPLETENESS = 0.7  # 70%
    WARNING_COMPLETENESS = 0.5   # 50%

    # Export settings
    EXPORT_CHUNK_SIZE = 1000
    MAX_EXPORT_ROWS = 100000

    # Upload settings
    MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
    ALLOWED_PHOTO_EXTENSIONS = os.getenv("ALLOWED_PHOTO_EXTENSIONS", "jpg,jpeg,png").split(",")
    ALLOWED_GPS_EXTENSIONS = os.getenv("ALLOWED_GPS_EXTENSIONS", "gpx,csv,shp").split(",")

    # Paths
    UPLOAD_DIR = "./uploads"
    PHOTO_DIR = "./uploads/photos"
    GPS_TRACK_DIR = "./uploads/gps_tracks"
    DATA_DIR = "./data"

    # Sentinel Hub API
    SENTINEL_HUB_CLIENT_ID = os.getenv("SENTINEL_HUB_CLIENT_ID")
    SENTINEL_HUB_CLIENT_SECRET = os.getenv("SENTINEL_HUB_CLIENT_SECRET")

    # Session
    SESSION_TIMEOUT_HOURS = int(os.getenv("SESSION_TIMEOUT_HOURS", "24"))

    # Validation ranges
    RANGES = {
        "ph": (4.0, 9.5),
        "humus": (0.1, 12.0),
        "yield_wheat": (0.5, 7.0),
        "yield_barley": (0.5, 6.0),
        "yield_sunflower": (0.3, 3.5),
        "yield_rapeseed": (0.5, 3.0),
        "moisture": (8.0, 25.0),
        "protein_wheat": (9.0, 18.0),
        "temperature": (-40.0, 45.0),
        "precipitation_daily": (0, 100.0),
        "ndvi": (-1.0, 1.0),
    }

    # Казахстанские регионы
    REGIONS = {
        "Акмолинская область": [
            "Аршалынский район",
            "Астраханский район",
            "Атбасарский район",
            "Буландынский район",
            "Бурабайский район",
            "Егіндікөл район",
            "Енбекшілдер район",
            "Ерейментауский район",
            "Есільский район",
            "Жаксынский район",
            "Жақсы район",
            "Зеренді район",
            "Коргалжынский район",
            "Қыз-кент район",
            "Сандыктауский район",
            "Целиноградский район",
            "Шортандинский район",
        ]
    }

    # Типы почв Акмолинской области
    SOIL_TYPES = [
        "Чернозем обыкновенный",
        "Чернозем южный",
        "Чернозем выщелоченный",
        "Темно-каштановая",
        "Каштановая",
        "Светло-каштановая",
        "Солонец",
        "Солончак",
        "Лугово-черноземная",
    ]

    # Типы рельефа
    RELIEF_TYPES = [
        "Равнинный",
        "Слабоволнистый",
        "Холмистый",
        "Склоновый",
    ]

    # Гранулометрический состав
    SOIL_TEXTURES = [
        "Легкий суглинок",
        "Средний суглинок",
        "Тяжелый суглинок",
        "Супесь",
        "Песок",
        "Глина",
    ]

    # Фазы развития культур
    CROP_STAGES = {
        "Пшеница яровая": [
            "Всходы",
            "Кущение",
            "Выход в трубку",
            "Колошение",
            "Цветение",
            "Налив зерна",
            "Молочная спелость",
            "Восковая спелость",
            "Полная спелость",
        ],
        "Подсолнечник": [
            "Всходы",
            "1-2 пары листьев",
            "3-4 пары листьев",
            "5-6 пар листьев",
            "Бутонизация",
            "Цветение",
            "Налив семян",
            "Созревание",
        ],
    }

    # Классы удобрений
    FERTILIZER_TYPES = [
        "Минеральное азотное",
        "Минеральное фосфорное",
        "Минеральное калийное",
        "Комплексное минеральное",
        "Органическое",
        "Микроудобрение",
        "Жидкое",
    ]

    # Классы СЗР
    PESTICIDE_CLASSES = [
        "Гербицид",
        "Инсектицид",
        "Фунгицид",
        "Протравитель",
        "Десикант",
        "Регулятор роста",
    ]

    # Типы вредных объектов
    PEST_TYPES = [
        "Болезнь",
        "Вредитель",
        "Сорняк",
    ]


settings = Settings()
