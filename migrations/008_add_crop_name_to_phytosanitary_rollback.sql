-- Migration 008 Rollback: Remove crop_name column from phytosanitary_monitoring table
-- WARNING: This will delete all crop_name data!
-- Date: 2025-10-31

BEGIN;

-- Remove crop_name column from phytosanitary_monitoring table
ALTER TABLE phytosanitary_monitoring
DROP COLUMN IF EXISTS crop_name;

COMMIT;
