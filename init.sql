-- DiamondMind Database Initialization Script
-- This script runs automatically when the Postgres container starts for the first time

-- Create extensions if needed (optional)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Database is already created by POSTGRES_DB env var
-- Users and tables will be created by SQLAlchemy migrations

SELECT 'DiamondMind database initialized successfully' AS status;