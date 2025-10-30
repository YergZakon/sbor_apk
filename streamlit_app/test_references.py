"""
Тест загрузки справочников
Проверяет, что все справочники загружаются корректно
"""
from utils.reference_loader import (
    load_crops,
    load_fertilizers,
    load_pesticides,
    load_diseases,
    load_pests,
    load_weeds,
    load_tractors,
    load_combines,
    load_implements
)

def test_reference_loading():
    """Проверка загрузки всех справочников"""

    print("🧪 Тестирование загрузки справочников...\n")

    references = {
        "Культуры": load_crops,
        "Удобрения": load_fertilizers,
        "СЗР": load_pesticides,
        "Болезни": load_diseases,
        "Вредители": load_pests,
        "Сорняки": load_weeds,
        "Тракторы": load_tractors,
        "Комбайны": load_combines,
        "Орудия": load_implements,
    }

    results = {}

    for name, loader_func in references.items():
        try:
            data = loader_func()
            if data:
                # Подсчитываем количество категорий/элементов
                if isinstance(data, dict):
                    count = len(data)
                    # Для справочников с вложенной структурой
                    total_items = sum(len(v) if isinstance(v, dict) else 1 for v in data.values())
                    results[name] = {
                        "status": "✅ OK",
                        "categories": count,
                        "total_items": total_items
                    }
                else:
                    results[name] = {
                        "status": "✅ OK",
                        "categories": "N/A",
                        "total_items": len(data) if hasattr(data, '__len__') else "N/A"
                    }
            else:
                results[name] = {
                    "status": "⚠️ EMPTY",
                    "categories": 0,
                    "total_items": 0
                }
        except Exception as e:
            results[name] = {
                "status": f"❌ ERROR: {str(e)}",
                "categories": 0,
                "total_items": 0
            }

    # Вывод результатов
    print("=" * 70)
    print(f"{'Справочник':<20} {'Статус':<20} {'Категорий':<15} {'Всего элементов':<15}")
    print("=" * 70)

    for name, result in results.items():
        status = result["status"]
        categories = result.get("categories", "-")
        total = result.get("total_items", "-")
        print(f"{name:<20} {status:<20} {categories:<15} {total:<15}")

    print("=" * 70)

    # Подсчет успешных загрузок
    success_count = sum(1 for r in results.values() if "OK" in r["status"])
    total_count = len(results)

    print(f"\n✅ Успешно загружено: {success_count}/{total_count} справочников")

    if success_count == total_count:
        print("🎉 Все справочники загружены успешно!")
        return True
    else:
        print("⚠️ Некоторые справочники не загрузились")
        return False


if __name__ == "__main__":
    # Запускаем тест
    success = test_reference_loading()

    # Возвращаем код выхода для CI/CD
    import sys
    sys.exit(0 if success else 1)
