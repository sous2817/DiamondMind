-- DM-15: Add User Profile Fields Migration
-- Manual SQL version for direct database execution
-- Run this if you want to apply the migration manually instead of via backend startup

-- Step 1: Add supabase_id column
ALTER TABLE users ADD COLUMN supabase_id VARCHAR(255);

CREATE UNIQUE INDEX ix_users_supabase_id ON users (supabase_id);

-- Step 2: Create age_group enum type
CREATE TYPE agegroup AS ENUM ('10u', '12u', '14u', '16u', '18u', 'college', 'adult');

-- Step 3: Create handedness enum type
CREATE TYPE handedness AS ENUM ('left', 'right', 'switch');

-- Step 4: Add profile columns
ALTER TABLE users ADD COLUMN age_group agegroup;

ALTER TABLE users ADD COLUMN handedness handedness;

ALTER TABLE users ADD COLUMN height_cm INTEGER;

-- Step 5: Update alembic version table (so it knows migration was applied)
-- First, check current version:
-- SELECT version_num FROM alembic_version;

-- Then update to new version:
UPDATE alembic_version SET version_num = '87958b8ee2f6';

-- Verification queries:
-- Check that columns were added:
SELECT column_name, data_type
FROM information_schema.columns
WHERE
    table_name = 'users';

-- Check enum types exist:
SELECT typname
FROM pg_type
WHERE
    typname IN ('agegroup', 'handedness');