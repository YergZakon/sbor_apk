-- Rollback Migration: Remove application_method from desiccation_details
-- Date: 2025-10-23
-- Description: Rollback addition of application_method field

BEGIN;

-- Remove the application_method column
ALTER TABLE desiccation_details
DROP COLUMN IF EXISTS application_method;

COMMIT;
