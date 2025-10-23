"""
Apply migration 002: Add new implement types (header, mower, baler)

This script applies the database migration to add support for new implement types
from the reference catalog.

Usage:
    python apply_migration_002.py
"""

import os
from pathlib import Path
from modules.database import engine
from sqlalchemy import text

def apply_migration():
    """Apply the migration to add new implement types"""

    migration_file = Path(__file__).parent / "migrations" / "002_add_implement_types.sql"

    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        return False

    print("📋 Reading migration file...")
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql = f.read()

    print("🔄 Applying migration...")
    try:
        with engine.begin() as conn:
            conn.execute(text(sql))
        print("✅ Migration applied successfully!")
        print("\n📝 New implement types added:")
        print("   - header (Жатки)")
        print("   - mower (Косилки)")
        print("   - baler (Пресс-подборщики)")
        return True
    except Exception as e:
        print(f"❌ Error applying migration: {e}")
        print("\n💡 If you're running on Supabase, you may need to apply this migration manually:")
        print(f"   1. Go to Supabase SQL Editor")
        print(f"   2. Copy and paste the contents of {migration_file}")
        print(f"   3. Execute the SQL")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Migration 002: Add new implement types")
    print("=" * 60)
    print()

    success = apply_migration()

    if success:
        print("\n✅ Migration completed successfully!")
    else:
        print("\n⚠️  Migration failed. Please apply manually.")

    print()
