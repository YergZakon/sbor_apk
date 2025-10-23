-- Rollback Migration: Remove new implement types
-- Date: 2025-10-23
-- Description: Rollback addition of header, mower, baler types

BEGIN;

-- Drop the constraint
ALTER TABLE implements DROP CONSTRAINT IF EXISTS implements_implement_type_check;

-- Restore the original constraint (without new types)
ALTER TABLE implements ADD CONSTRAINT implements_implement_type_check
CHECK (implement_type IN (
    'seeder',
    'planter',
    'plow',
    'cultivator',
    'harrow',
    'disc',
    'deep_loosener',
    'roller',
    'sprayer_trailer',
    'fertilizer_spreader',
    'stubble_breaker',
    'snow_plow',
    'other'
));

-- NOTE: This will fail if there are any rows with header, mower, or baler types
-- You must delete or update those rows first

COMMIT;
