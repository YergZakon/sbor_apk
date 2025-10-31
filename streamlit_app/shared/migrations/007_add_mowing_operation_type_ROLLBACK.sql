-- Rollback Migration: Remove 'mowing' from operations.operation_type CHECK constraint
-- Date: 2025-10-31

BEGIN;

-- Drop the constraint with 'mowing'
ALTER TABLE operations DROP CONSTRAINT IF EXISTS operations_operation_type_check;

-- Restore the original constraint without 'mowing'
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
        'fallow'
    ));

COMMIT;
