# Migration 002: Add New Implement Types

**Date:** 2025-10-23
**Status:** Ready to apply
**Type:** Schema extension

## Overview

This migration adds support for three new implement types to the `implements` table:
- `header` - Жатки (Headers for combines)
- `mower` - Косилки (Mowers)
- `baler` - Пресс-подборщики (Balers)

These types are required to support the implements reference catalog that includes 187 implement models across 10 categories.

## Changes

### Modified Tables
- `implements`: Updated CHECK constraint on `implement_type` column

### Before
```sql
CHECK (implement_type IN (
    'seeder', 'planter', 'plow', 'cultivator', 'harrow', 'disc',
    'deep_loosener', 'roller', 'sprayer_trailer', 'fertilizer_spreader',
    'stubble_breaker', 'snow_plow', 'other'
))
```

### After
```sql
CHECK (implement_type IN (
    'seeder', 'planter', 'plow', 'cultivator', 'harrow', 'disc',
    'deep_loosener', 'roller', 'sprayer_trailer', 'fertilizer_spreader',
    'stubble_breaker', 'snow_plow',
    'header', 'mower', 'baler',  -- NEW TYPES
    'other'
))
```

## How to Apply

### Option 1: Using Python Script (Local Development)
```bash
python apply_migration_002.py
```

### Option 2: Manual Application (Supabase Production)

1. Go to your Supabase project's SQL Editor
2. Copy the contents of `002_add_implement_types.sql`
3. Execute the SQL
4. Verify success by checking the constraint:
   ```sql
   SELECT conname, pg_get_constraintdef(oid)
   FROM pg_constraint
   WHERE conname = 'implements_implement_type_check';
   ```

## Rollback

If you need to rollback this migration (e.g., in case of issues):

1. **IMPORTANT:** First, ensure there are no rows with the new types:
   ```sql
   SELECT COUNT(*) FROM implements
   WHERE implement_type IN ('header', 'mower', 'baler');
   ```

2. If count is 0, you can safely rollback:
   - Run `002_add_implement_types_ROLLBACK.sql`

3. If count > 0, you must first:
   - Delete those rows, OR
   - Update them to use a different type

## Testing

After applying the migration, test by:

1. Go to Equipment page (🚜 Управление техникой и агрегатами)
2. Select "Агрегаты" tab
3. Click "Из справочника" mode
4. Select "Жатка" (header) type
5. Choose a manufacturer and model
6. Submit the form
7. Verify the implement is added successfully

## Dependencies

- Requires: Initial database schema
- Required by: Implements reference catalog integration
- Related commits: `0613955` (feat: add implements reference catalog)

## Notes

- This is a non-breaking change (only adds new values, doesn't remove existing ones)
- Existing data is not affected
- The migration is transactional (uses BEGIN/COMMIT)
- Safe to apply on production database
