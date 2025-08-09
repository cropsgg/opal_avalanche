-- Initialize OPAL Database
-- This script sets up the basic database structure and extensions

-- Enable required PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create schemas if they don't exist
CREATE SCHEMA IF NOT EXISTS public;

-- Grant permissions
GRANT ALL ON SCHEMA public TO opal;
GRANT ALL PRIVILEGES ON DATABASE opal_db TO opal;

-- Set up Row Level Security function
CREATE OR REPLACE FUNCTION current_user_id() RETURNS uuid AS $$
BEGIN
  RETURN COALESCE(
    current_setting('rls.user_id', true)::uuid,
    '00000000-0000-0000-0000-000000000000'::uuid
  );
EXCEPTION
  WHEN OTHERS THEN
    RETURN '00000000-0000-0000-0000-000000000000'::uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a function to set current user context
CREATE OR REPLACE FUNCTION set_current_user_id(user_id uuid) RETURNS void AS $$
BEGIN
  PERFORM set_config('rls.user_id', user_id::text, true);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Log successful initialization
INSERT INTO pg_stat_statements_info (dealloc) VALUES (0) ON CONFLICT DO NOTHING;

COMMENT ON DATABASE opal_db IS 'OPAL - GenAI Co-Counsel Database';

-- Create sample configuration table
CREATE TABLE IF NOT EXISTS app_config (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert initial configuration
INSERT INTO app_config (key, value, description) VALUES 
('version', '0.1.0', 'Application version'),
('max_file_size_mb', '50', 'Maximum file size in MB'),
('max_files_per_matter', '100', 'Maximum files per matter'),
('default_language', 'en', 'Default document language')
ON CONFLICT (key) DO NOTHING;
