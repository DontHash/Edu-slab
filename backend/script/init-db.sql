-- Initial database setup script
-- This script runs automatically when the PostgreSQL container is first created

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Set timezone
SET timezone = 'UTC';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE adaptive_learning TO postgres;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'Database initialized successfully';
END $$;
