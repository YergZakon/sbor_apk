-- Migration: Add 'mowing' to operations.operation_type CHECK constraint
-- Date: 2025-10-31
-- Description: Allow 'mowing' as a valid operation type for forage crop harvest

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
