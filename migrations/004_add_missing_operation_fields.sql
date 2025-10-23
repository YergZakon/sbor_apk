-- Migration: Add missing fields to operation detail tables
-- Date: 2025-10-23
-- Description: Add missing fields to irrigation_details, snow_retention_details, fallow_details, and tillage_details

BEGIN;

-- ============================================================
-- Add soil_moisture_before to irrigation_details
-- ============================================================
ALTER TABLE irrigation_details
ADD COLUMN IF NOT EXISTS soil_moisture_before FLOAT;

COMMENT ON COLUMN irrigation_details.soil_moisture_before
IS 'Влажность почвы до орошения (%)';

-- ============================================================
-- Add snow_depth_cm and number_of_passes to snow_retention_details
-- ============================================================
ALTER TABLE snow_retention_details
ADD COLUMN IF NOT EXISTS snow_depth_cm FLOAT;

ALTER TABLE snow_retention_details
ADD COLUMN IF NOT EXISTS number_of_passes INTEGER;

COMMENT ON COLUMN snow_retention_details.snow_depth_cm
IS 'Глубина снежного покрова (см)';

COMMENT ON COLUMN snow_retention_details.number_of_passes
IS 'Количество проходов техники';

-- ============================================================
-- Add number_of_treatments to fallow_details
-- ============================================================
ALTER TABLE fallow_details
ADD COLUMN IF NOT EXISTS number_of_treatments INTEGER;

COMMENT ON COLUMN fallow_details.number_of_treatments
IS 'Количество обработок паровых полей';

-- ============================================================
-- Add soil_moisture to tillage_details
-- ============================================================
ALTER TABLE tillage_details
ADD COLUMN IF NOT EXISTS soil_moisture VARCHAR(50);

COMMENT ON COLUMN tillage_details.soil_moisture
IS 'Влажность почвы (сухая, нормальная, влажная)';

COMMIT;
