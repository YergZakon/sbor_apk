-- Migration: Add user_farms table for many-to-many user-farm relationship
-- Date: 2025-10-23
-- Description: Allow users to manage multiple farms with different roles

BEGIN;

-- ============================================================
-- Create user_farms association table
-- ============================================================
CREATE TABLE IF NOT EXISTS user_farms (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    farm_id INTEGER NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'viewer',  -- admin, manager, viewer for this specific farm
    is_primary BOOLEAN DEFAULT FALSE,   -- Primary farm for the user
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Unique constraint: user can't be added to same farm twice
    CONSTRAINT uq_user_farm UNIQUE (user_id, farm_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_farms_user_id ON user_farms(user_id);
CREATE INDEX IF NOT EXISTS idx_user_farms_farm_id ON user_farms(farm_id);
CREATE INDEX IF NOT EXISTS idx_user_farms_is_primary ON user_farms(user_id, is_primary) WHERE is_primary = TRUE;

-- Add comments for documentation
COMMENT ON TABLE user_farms IS 'Many-to-many relationship between users and farms';
COMMENT ON COLUMN user_farms.role IS 'User role in this specific farm (admin, manager, viewer)';
COMMENT ON COLUMN user_farms.is_primary IS 'Primary farm shown by default for this user';

-- ============================================================
-- Migrate existing data from users.farm_id to user_farms
-- ============================================================
-- This creates user_farms records for all users that have farm_id set
INSERT INTO user_farms (user_id, farm_id, role, is_primary)
SELECT
    id as user_id,
    farm_id,
    role,  -- Copy existing role from users table
    TRUE as is_primary  -- Make it primary since it's their only farm currently
FROM users
WHERE farm_id IS NOT NULL
ON CONFLICT (user_id, farm_id) DO NOTHING;  -- Skip if already exists

COMMIT;
