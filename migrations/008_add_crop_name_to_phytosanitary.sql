-- Migration 008: Add crop_name column to phytosanitary_monitoring table
-- Purpose: Store the crop name for each phytosanitary inspection
-- Date: 2025-10-31

BEGIN;

-- Add crop_name column to phytosanitary_monitoring table
ALTER TABLE phytosanitary_monitoring
ADD COLUMN IF NOT EXISTS crop_name VARCHAR(100);

-- Add comment to the column
COMMENT ON COLUMN phytosanitary_monitoring.crop_name IS
    'Название культуры на момент обследования';

COMMIT;
