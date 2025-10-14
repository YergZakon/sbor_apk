#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест работоспособности системы
"""

import sys
import json
from pathlib import Path

def test_imports():
    """Тест импортов модулей"""
    print("=" * 60)
    print("ТЕСТ ИМПОРТОВ МОДУЛЕЙ")
    print("=" * 60)

    try:
        from modules.database import Base, engine, SessionLocal
        from modules.database import Farm, Field, Operation, SowingDetail
        from modules.database import FertilizerApplication, PesticideApplication
        from modules.database import HarvestData, AgrochemicalAnalysis
        from modules.database import PhytosanitaryMonitoring, WeatherData
        from modules.validators import DataValidator
        from modules.config import Settings
        print("✓ Все модули импортированы успешно")
        return True
    except Exception as e:
        print(f"✗ Ошибка импорта: {e}")
        return False

def test_database():
    """Тест базы данных"""
    print("\n" + "=" * 60)
    print("ТЕСТ БАЗЫ ДАННЫХ")
    print("=" * 60)

    try:
        from modules.database import init_db, SessionLocal
        init_db()

        # Тест подключения
        db = SessionLocal()
        db.close()
        print("✓ База данных инициализирована и доступна")
        return True
    except Exception as e:
        print(f"✗ Ошибка БД: {e}")
        return False

def test_reference_data():
    """Тест справочных данных"""
    print("\n" + "=" * 60)
    print("ТЕСТ СПРАВОЧНЫХ ДАННЫХ")
    print("=" * 60)

    data_files = {
        'crops.json': 'Культуры',
        'fertilizers.json': 'Удобрения',
        'pesticides.json': 'Пестициды',
        'diseases.json': 'Болезни',
        'pests.json': 'Вредители',
        'weeds.json': 'Сорняки'
    }

    all_ok = True
    for filename, description in data_files.items():
        try:
            path = Path('data') / filename
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                count = len(data)
                print(f"✓ {description}: {count} записей")
        except Exception as e:
            print(f"✗ {description}: Ошибка - {e}")
            all_ok = False

    return all_ok

def test_pages():
    """Тест наличия страниц"""
    print("\n" + "=" * 60)
    print("ТЕСТ СТРАНИЦ ПРИЛОЖЕНИЯ")
    print("=" * 60)

    pages = [
        ('0_🏢_Farm_Setup.py', 'Регистрация хозяйства'),
        ('1_🏠_Dashboard.py', 'Dashboard'),
        ('2_🌱_Fields.py', 'Управление полями'),
        ('3_📝_Journal.py', 'Журнал операций'),
        ('4_🌾_Sowing.py', 'Учет посева'),
        ('5_💊_Fertilizers.py', 'Учет удобрений'),
        ('6_🛡️_Pesticides.py', 'Учет пестицидов'),
        ('7_🐛_Phytosanitary.py', 'Фитосанитария'),
        ('8_🚜_Harvest.py', 'Учет уборки'),
        ('9_🧪_Agrochemistry.py', 'Агрохимия'),
        ('11_🌤️_Weather.py', 'Погода'),
        ('15_📥_Import.py', 'Импорт данных'),
    ]

    all_ok = True
    for filename, description in pages:
        path = Path('pages') / filename
        if path.exists():
            size_kb = path.stat().st_size / 1024
            print(f"✓ {description}: {size_kb:.1f} KB")
        else:
            print(f"✗ {description}: Файл не найден")
            all_ok = False

    return all_ok

def test_utilities():
    """Тест утилит"""
    print("\n" + "=" * 60)
    print("ТЕСТ УТИЛИТ")
    print("=" * 60)

    utilities = [
        ('modules/config.py', 'Конфигурация'),
        ('modules/database.py', 'База данных'),
        ('modules/validators.py', 'Валидация'),
    ]

    all_ok = True
    for filename, description in utilities:
        path = Path(filename)
        if path.exists():
            size_kb = path.stat().st_size / 1024
            print(f"✓ {description}: {size_kb:.1f} KB")
        else:
            print(f"✗ {description}: Файл не найден")
            all_ok = False

    return all_ok

def main():
    """Главная функция"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "СИСТЕМА СБОРА ДАННЫХ ХОЗЯЙСТВ" + " " * 18 + "║")
    print("║" + " " * 15 + "ТЕСТ РАБОТОСПОСОБНОСТИ" + " " * 21 + "║")
    print("╚" + "═" * 58 + "╝")
    print("\n")

    results = []

    # Запуск тестов
    results.append(("Импорты модулей", test_imports()))
    results.append(("База данных", test_database()))
    results.append(("Справочные данные", test_reference_data()))
    results.append(("Страницы приложения", test_pages()))
    results.append(("Утилиты", test_utilities()))

    # Итоговый отчет
    print("\n" + "=" * 60)
    print("ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 60)

    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ НЕ ПРОЙДЕН"
        print(f"{test_name}: {status}")

    all_passed = all(result for _, result in results)

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("Система готова к запуску:")
        print("\n  streamlit run app.py")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        print("Проверьте ошибки выше")
    print("=" * 60)
    print()

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
