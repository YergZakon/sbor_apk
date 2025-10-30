"""
Простой тест путей для диагностики
Запускается ИЗ streamlit_app/ директории (как на Streamlit Cloud)
"""
from pathlib import Path
import os

print("=" * 70)
print("🔍 ДИАГНОСТИКА ПУТЕЙ")
print("=" * 70)

print("\n1️⃣ Текущая рабочая директория:")
print(f"   {Path.cwd()}")

print("\n2️⃣ Путь к этому файлу:")
print(f"   {Path(__file__)}")

print("\n3️⃣ Проверка существования data/ директорий:")

paths_to_check = [
    ("Path.cwd() / 'data'", Path.cwd() / "data"),
    ("Path.cwd() / 'shared/data'", Path.cwd() / "shared" / "data"),
    ("Path.cwd() / 'streamlit_app/data'", Path.cwd() / "streamlit_app" / "data"),
]

for name, path in paths_to_check:
    exists = path.exists()
    marker = "✅" if exists else "❌"
    print(f"\n   {marker} {name}")
    print(f"      {path}")

    if exists:
        # Список JSON файлов
        json_files = list(path.glob("*.json"))
        print(f"      → {len(json_files)} JSON файлов")
        if json_files:
            for f in json_files[:3]:
                print(f"         - {f.name}")
            if len(json_files) > 3:
                print(f"         ... и ещё {len(json_files) - 3}")

print("\n4️⃣ Тест загрузки справочника:")

try:
    from utils.reference_loader import load_reference

    # Тестируем загрузку
    fertilizers = load_reference("fertilizers.json", show_error=False)

    if fertilizers:
        print(f"   ✅ fertilizers.json загружен успешно!")
        print(f"   → {len(fertilizers)} категорий")
        print(f"   → Категории: {', '.join(list(fertilizers.keys())[:3])}, ...")
    else:
        print(f"   ❌ fertilizers.json НЕ загружен")

except Exception as e:
    print(f"   ❌ Ошибка: {e}")

print("\n" + "=" * 70)
print("✅ Тест завершён")
print("=" * 70)
