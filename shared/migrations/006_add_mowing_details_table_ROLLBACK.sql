-- Rollback Migration: Remove mowing_details table
-- Date: 2025-10-31

BEGIN;

-- Drop table and indexes (CASCADE will drop foreign key constraints automatically)
DROP TABLE IF EXISTS mowing_details CASCADE;

COMMIT;
