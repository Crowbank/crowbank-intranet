-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schema
CREATE SCHEMA IF NOT EXISTS crowbank;

-- Set search path
ALTER DATABASE crowbank SET search_path TO crowbank, public; 