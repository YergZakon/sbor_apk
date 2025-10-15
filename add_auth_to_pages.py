"""
Script to add authentication to all pages systematically
"""
import os
import re

# Define auth imports to add
AUTH_IMPORTS = """from modules.auth import (
    require_auth,
    require_farm_binding,
    filter_query_by_farm,
    get_user_display_name,
    can_edit_data,
    can_delete_data
)"""

# List of pages to update (excluding Login, Admin, Dashboard, Farm Setup which are already done)
PAGES_TO_UPDATE = [
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

def add_auth_to_page(filepath):
    """Add authentication to a page file"""
    print(f"Processing: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if already has auth imports
    if 'from modules.auth import' in content:
        print(f"  ✓ Already has auth imports")
        return

    # Find the import section
    import_pattern = r'(from modules\.database import [^\n]+)'
    match = re.search(import_pattern, content)

    if not match:
        print(f"  ✗ Could not find database import")
        return

    # Add auth imports after database import
    content = content.replace(
        match.group(1),
        match.group(1) + '\n' + AUTH_IMPORTS
    )

    # Add require_auth() after st.set_page_config
    config_pattern = r'(st\.set_page_config\([^)]+\))'
    match = re.search(config_pattern, content)

    if match:
        auth_code = '''

# Требуем авторизацию и привязку к хозяйству
require_auth()
require_farm_binding()
'''
        content = content.replace(
            match.group(1),
            match.group(1) + auth_code
        )

    # Add user caption after st.title
    title_pattern = r'(st\.title\([^)]+\))'
    match = re.search(title_pattern, content)

    if match:
        caption_code = '\nst.caption(f"Пользователь: **{get_user_display_name()}**")'
        content = content.replace(
            match.group(1),
            match.group(1) + caption_code
        )

    # Replace db.query patterns with filter_query_by_farm where appropriate
    # This is a simple replacement - manual review recommended
    query_patterns = [
        (r'db\.query\(Farm\)', 'filter_query_by_farm(db.query(Farm), Farm)'),
        (r'db\.query\(Field\)', 'filter_query_by_farm(db.query(Field), Field)'),
        (r'db\.query\(Operation\)', 'filter_query_by_farm(db.query(Operation), Operation)'),
    ]

    for pattern, replacement in query_patterns:
        # Only replace if not already filtered
        if pattern in content and 'filter_query_by_farm' not in content:
            content = re.sub(pattern, replacement, content)

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  ✓ Updated successfully")

if __name__ == "__main__":
    for page in PAGES_TO_UPDATE:
        if os.path.exists(page):
            add_auth_to_page(page)
        else:
            print(f"File not found: {page}")

    print("\n✅ All pages processed!")
    print("\n⚠️  Manual review required:")
    print("  - Check query filtering is comprehensive")
    print("  - Add permission checks around edit/delete forms")
    print("  - Test each page for correct filtering")
