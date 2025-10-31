-- Migration: Add mowing_details table for forage crop harvest tracking
-- Date: 2025-10-31
-- Description: Track mowing operations (multi-cut forage crops) with two-phase harvest support

BEGIN;

-- ============================================================
-- Create mowing_details table
-- ============================================================
CREATE TABLE IF NOT EXISTS mowing_details (
    id SERIAL PRIMARY KEY,
    operation_id INTEGER NOT NULL REFERENCES operations(id) ON DELETE CASCADE UNIQUE,
    crop VARCHAR(100),  -- Культура (люцерна, эспарцет и т.д.)
    mowing_number INTEGER,  -- Номер укоса (1, 2, 3, 4)
    yield_green_mass_t_ha FLOAT,  -- Урожайность зеленой массы т/га
    yield_hay_t_ha FLOAT,  -- Урожайность сена т/га (после сушки)
    moisture_pct FLOAT,  -- Влажность при укосе %
    quality_class VARCHAR(20),  -- Класс качества (1-й, 2-й, 3-й)
    harvest_phase VARCHAR(20),  -- mowing (укос) или pickup (подбор)
    linked_operation_id INTEGER REFERENCES operations(id),  -- Связь фаза 1 → фаза 2
    plant_height_cm FLOAT,  -- Высота растений при укосе
    stubble_height_cm FLOAT  -- Высота среза
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_mowing_details_operation_id ON mowing_details(operation_id);
CREATE INDEX IF NOT EXISTS idx_mowing_details_linked_operation_id ON mowing_details(linked_operation_id);
CREATE INDEX IF NOT EXISTS idx_mowing_details_harvest_phase ON mowing_details(harvest_phase);

-- Add comments for documentation
COMMENT ON TABLE mowing_details IS 'Details of mowing operations for forage crops (alfalfa, sainfoin, etc.)';
COMMENT ON COLUMN mowing_details.crop IS 'Forage crop name';
COMMENT ON COLUMN mowing_details.mowing_number IS 'Cut number in season (1st, 2nd, 3rd, 4th)';
COMMENT ON COLUMN mowing_details.yield_green_mass_t_ha IS 'Green mass yield in t/ha (mowing phase)';
COMMENT ON COLUMN mowing_details.yield_hay_t_ha IS 'Hay yield in t/ha (pickup phase after drying)';
COMMENT ON COLUMN mowing_details.harvest_phase IS 'mowing = cut and windrow, pickup = collect dried windrows';
COMMENT ON COLUMN mowing_details.linked_operation_id IS 'Links pickup operation to its mowing operation';

COMMIT;
