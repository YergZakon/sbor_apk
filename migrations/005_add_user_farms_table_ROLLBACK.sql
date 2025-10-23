-- Rollback Migration: Remove user_farms table
-- Date: 2025-10-23
-- Description: Rollback many-to-many user-farm relationship

BEGIN;

-- WARNING: This will delete all user-farm associations
-- Users will fall back to using users.farm_id field

DROP TABLE IF EXISTS user_farms CASCADE;

COMMIT;
