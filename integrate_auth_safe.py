"""
Безопасная интеграция аутентификации в страницы
Делает минимальные изменения только в ключевых местах
"""
import re
import sys

def add_auth_to_file(filepath):
    """Добавить аутентификацию в файл"""
    print(f"\n{'='*60}")
    print(f"Обработка: {filepath}")
    print('='*60)

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # 1. Проверка что файл еще не обработан
        if 'from modules.auth import' in content:
            print("  ✓ Уже имеет импорты auth")
            return False

        # 2. Добавить импорты после modules.database
        auth_imports = """from modules.auth import (
    require_auth,
    require_farm_binding,
    filter_query_by_farm,
    get_user_display_name,
    can_edit_data,
    can_delete_data
)"""

        # Найти строку с импортом database
        pattern = r'(from modules\.database import [^\n]+)'
        match = re.search(pattern, content)
        if match:
            content = content.replace(
                match.group(0),
                match.group(0) + '\n' + auth_imports
            )
            print("  ✓ Добавлены импорты auth")
        else:
            print("  ✗ Не найден импорт database")
            return False

        # 3. Добавить require_auth() после st.set_page_config
        pattern = r'(st\.set_page_config\([^)]+\))'
        match = re.search(pattern, content)
        if match:
            auth_code = '''

# Требуем авторизацию и привязку к хозяйству
require_auth()
require_farm_binding()'''
            content = content.replace(
                match.group(0),
                match.group(0) + auth_code
            )
            print("  ✓ Добавлен require_auth()")

        # 4. Добавить caption после st.title
        pattern = r'(st\.title\([^)]+\))'
        match = re.search(pattern, content)
        if match:
            caption = '\nst.caption(f"Пользователь: **{get_user_display_name()}**")'
            content = content.replace(
                match.group(0),
                match.group(0) + caption
            )
            print("  ✓ Добавлен caption с пользователем")

        # 5. Заменить db.query(Farm).first() на filter_query_by_farm
        content = re.sub(
            r'farm = db\.query\(Farm\)\.first\(\)',
            'farm = filter_query_by_farm(db.query(Farm), Farm).first()',
            content
        )
        if 'filter_query_by_farm(db.query(Farm)' in content:
            print("  ✓ Обновлен запрос Farm")

        # 6. Заменить db.query(Field).filter(Field.farm_id == farm.id) на filter
        content = re.sub(
            r'db\.query\(Field\)\.filter\(Field\.farm_id == farm\.id\)',
            'filter_query_by_farm(db.query(Field), Field)',
            content
        )
        if 'filter_query_by_farm(db.query(Field)' in content:
            print("  ✓ Обновлен запрос Field")

        # 7. Обновить сообщение об ошибке отсутствия хозяйства
        content = content.replace(
            'st.error("❌ Сначала необходимо зарегистрировать хозяйство на главной странице!")',
            'st.error("❌ Хозяйство не найдено. Обратитесь к администратору для привязки к хозяйству.")'
        )

        # 8. Сохранить если были изменения
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n✅ Файл успешно обновлен!")
            return True
        else:
            print(f"\n⚠️  Нет изменений")
            return False

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False

def main():
    """Основная функция"""
    files = [
        "pages/2_🌱_Fields.py",
        "pages/3_📝_Journal.py",
        "pages/4_🌾_Sowing.py",
        "pages/5_💊_Fertilizers.py",
        "pages/6_🛡️_Pesticides.py",
        "pages/7_🐛_Phytosanitary.py",
        "pages/8_🚜_Harvest.py",
        "pages/9_🧪_Agrochemistry.py",
        "pages/11_🌤️_Weather.py",
        "pages/15_📥_Import.py",
    ]

    print("\n" + "="*60)
    print("БЕЗОПАСНАЯ ИНТЕГРАЦИЯ АУТЕНТИФИКАЦИИ")
    print("="*60)
    print(f"\nФайлов для обработки: {len(files)}")

    updated = 0
    skipped = 0
    errors = 0

    for filepath in files:
        result = add_auth_to_file(filepath)
        if result:
            updated += 1
        elif result is False:
            skipped += 1
        else:
            errors += 1

    print("\n" + "="*60)
    print("ИТОГИ")
    print("="*60)
    print(f"✅ Обновлено: {updated}")
    print(f"⏭️  Пропущено: {skipped}")
    print(f"❌ Ошибок: {errors}")
    print("\n⚠️  ВАЖНО: После обновления проверьте синтаксис:")
    print("python -m py_compile pages/*.py")

if __name__ == "__main__":
    main()
