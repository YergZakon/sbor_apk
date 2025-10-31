# Migration 007: Add 'mowing' Operation Type

## Issue
The Mowing page fails with a CHECK constraint violation error when trying to save operations:

```
psycopg2.errors.CheckViolation: new row for relation "operations" violates check constraint "operations_operation_type_check"
DETAIL: Failing row contains (..., mowing, ...)
```

## Root Cause
The `operations` table has a CHECK constraint that validates `operation_type` values. The constraint did NOT include 'mowing' as a valid operation type, even though we added the `mowing_details` table in migration 006.

## Solution
Migration 007 updates the CHECK constraint to include 'mowing' as a valid operation type.

## Apply Migration on Streamlit Cloud

### Option 1: Using Streamlit Cloud Database Console (Recommended)

1. Go to your Streamlit Cloud app settings
2. Navigate to **Secrets** or **Database** section
3. Connect to your PostgreSQL database
4. Run the following SQL:

```sql
-- Migration 007: Add 'mowing' to operations.operation_type CHECK constraint
BEGIN;

-- Drop the existing CHECK constraint
ALTER TABLE operations DROP CONSTRAINT IF EXISTS operations_operation_type_check;

-- Add the updated CHECK constraint with 'mowing' included
ALTER TABLE operations ADD CONSTRAINT operations_operation_type_check
    CHECK (operation_type IN (
        'sowing',
        'fertilizing',
        'spraying',
        'harvest',
        'soil_analysis',
        'desiccation',
        'tillage',
        'irrigation',
        'snow_retention',
        'fallow',
        'mowing'
    ));

COMMENT ON CONSTRAINT operations_operation_type_check ON operations IS
    'Valid operation types including mowing for forage crops';

COMMIT;
```

### Option 2: Using psql Command Line

If you have direct database access:

```bash
psql $DATABASE_URL -f migrations/007_add_mowing_operation_type.sql
```

## Verification

After applying the migration, verify it worked:

```sql
-- Check the constraint exists
SELECT conname, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid = 'operations'::regclass
AND conname = 'operations_operation_type_check';

-- Test inserting a mowing operation (should succeed now)
INSERT INTO operations (farm_id, field_id, operation_type, operation_date, area_processed_ha, machine_id)
VALUES (2, 3, 'mowing', CURRENT_DATE, 100.0, 1);

-- Clean up test record
DELETE FROM operations WHERE operation_type = 'mowing' AND operation_date = CURRENT_DATE;
```

## Rollback (if needed)

If you need to rollback this migration:

```bash
psql $DATABASE_URL -f migrations/007_add_mowing_operation_type_ROLLBACK.sql
```

**WARNING**: Rollback will fail if you have existing mowing operations in the database. Delete those records first if you need to rollback.

## Files Changed
- `migrations/007_add_mowing_operation_type.sql` - Migration SQL
- `migrations/007_add_mowing_operation_type_ROLLBACK.sql` - Rollback SQL
- `streamlit_app/modules/database.py` - Updated operation_type comment

## Next Steps
After applying this migration, the Mowing page should work correctly. Test by:
1. Going to the Mowing page
2. Registering a new mowing operation
3. Verifying it saves successfully
4. Checking the History tab displays the operation
