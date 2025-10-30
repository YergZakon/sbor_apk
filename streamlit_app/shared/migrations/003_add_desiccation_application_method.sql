-- Migration: Add application_method to desiccation_details
-- Date: 2025-10-23
-- Description: Add missing application_method field to desiccation_details table

BEGIN;

-- Add the application_method column
ALTER TABLE desiccation_details
ADD COLUMN IF NOT EXISTS application_method VARCHAR(100);

-- Add comment for documentation
COMMENT ON COLUMN desiccation_details.application_method IS 'Способ применения (Наземное/Авиационное опрыскивание)';

COMMIT;
