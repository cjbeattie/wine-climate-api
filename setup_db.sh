#!/bin/bash

# Check if PostgreSQL is running
if ! pg_isready -q; then
  echo "PostgreSQL is not running. Please start PostgreSQL."
  exit 1
fi

# Prompt for the password
echo "Please enter the database password:"
read -s DATABASE_PASSWORD

# Create the database if it doesn't exist
psql -U postgres -c "CREATE DATABASE IF NOT EXISTS wine_climate_db;"

# Create the user if it doesn't exist
psql -U postgres -c "CREATE USER IF NOT EXISTS wine_climate_db_user WITH PASSWORD '$DATABASE_PASSWORD';"

# Set up user privileges
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE wine_climate_db TO wine_climate_db_user;"

echo "Database setup complete."