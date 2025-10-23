# Database Migrations

This directory contains all database schema migrations for the Farm Data System.

## Migration Files

### Migration 002: Add New Implement Types
**Status:** ⚠️ NEEDS TO BE APPLIED ON SUPABASE
**File:** `002_add_implement_types.sql`
**Date:** 2025-10-23

Adds support for new implement types:
- `header` (Жатки) - Combine headers
- `mower` (Косилки) - Mowers
- `baler` (Пресс-подборщики) - Balers

**To apply:**
```sql
-- Run in Supabase SQL Editor:
-- Copy and execute migrations/002_add_implement_types.sql
```

### Migration 003: Add Desiccation Application Method
**Status:** ⚠️ NEEDS TO BE APPLIED ON SUPABASE
**File:** `003_add_desiccation_application_method.sql`
**Date:** 2025-10-23

Adds missing `application_method` field to `desiccation_details` table.

**To apply:**
```sql
-- Run in Supabase SQL Editor:
-- Copy and execute migrations/003_add_desiccation_application_method.sql
```

## How to Apply Migrations on Supabase

1. Go to your Supabase Dashboard
2. Navigate to **SQL Editor**
3. Click **New query**
4. Copy the migration SQL from the file
5. Click **Run**
6. Verify success (should show "Success. No rows returned")

## Combined Migration Script

If you haven't applied any migrations yet, you can run them all at once:

```sql
-- ============================================================
-- MIGRATION 002: Add new implement types
-- ============================================================
BEGIN;

ALTER TABLE implements DROP CONSTRAINT IF EXISTS implements_implement_type_check;

ALTER TABLE implements ADD CONSTRAINT implements_implement_type_check
CHECK (implement_type IN (
    'seeder', 'planter', 'plow', 'cultivator', 'harrow', 'disc',
    'deep_loosener', 'roller', 'sprayer_trailer', 'fertilizer_spreader',
    'stubble_breaker', 'snow_plow',
    'header', 'mower', 'baler',  -- NEW
    'other'
));

COMMIT;

-- ============================================================
-- MIGRATION 003: Add desiccation application_method
-- ============================================================
BEGIN;

ALTER TABLE desiccation_details
ADD COLUMN IF NOT EXISTS application_method VARCHAR(100);

COMMENT ON COLUMN desiccation_details.application_method
IS 'Способ применения (Наземное/Авиационное опрыскивание)';

COMMIT;
```

## Verification

After applying migrations, verify they were successful:

```sql
-- Check implements constraint
SELECT conname, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conname = 'implements_implement_type_check';

-- Check desiccation_details columns
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'desiccation_details'
ORDER BY ordinal_position;
```

## Migration History

| # | Date | Description | Status |
|---|------|-------------|--------|
| 002 | 2025-10-23 | Add implement types (header, mower, baler) | Pending |
| 003 | 2025-10-23 | Add desiccation application_method field | Pending |

## Rollback Instructions

If you need to rollback a migration:

1. Ensure no data will be lost (check for affected rows)
2. Run the corresponding `*_ROLLBACK.sql` file
3. Update this README to reflect the rollback

## Notes

- All migrations are transactional (use BEGIN/COMMIT)
- Migrations use `IF NOT EXISTS` / `IF EXISTS` for idempotency
- Always test migrations on a development database first
- Keep this README updated with migration status
