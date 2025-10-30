-- Migration: Add new implement types (header, mower, baler)
-- Date: 2025-10-23
-- Description: Extend implements table to support headers, mowers, and balers from reference catalog

BEGIN;

-- Drop the existing check constraint
ALTER TABLE implements DROP CONSTRAINT IF EXISTS implements_implement_type_check;

-- Add the new check constraint with additional types
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
    'header',        -- NEW: Жатки
    'mower',         -- NEW: Косилки
    'baler',         -- NEW: Пресс-подборщики
    'other'
));

COMMIT;
