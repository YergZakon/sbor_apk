-- Rollback Migration: Remove added operation detail fields
-- Date: 2025-10-23
-- Description: Rollback addition of missing fields

BEGIN;

-- Remove added columns
ALTER TABLE irrigation_details DROP COLUMN IF EXISTS soil_moisture_before;
ALTER TABLE snow_retention_details DROP COLUMN IF EXISTS snow_depth_cm;
ALTER TABLE snow_retention_details DROP COLUMN IF EXISTS number_of_passes;
ALTER TABLE fallow_details DROP COLUMN IF EXISTS number_of_treatments;
ALTER TABLE tillage_details DROP COLUMN IF EXISTS soil_moisture;

COMMIT;
