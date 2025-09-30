-- Initialize the CSV converter database
CREATE DATABASE IF NOT EXISTS csv_converter;

-- Create a test schema
CREATE SCHEMA IF NOT EXISTS test_data;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE csv_converter TO csvuser;
GRANT ALL PRIVILEGES ON SCHEMA test_data TO csvuser;