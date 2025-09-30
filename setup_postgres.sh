#!/bin/bash
# PostgreSQL Docker Setup Script
# This script helps set up the PostgreSQL container with proper environment configuration

echo "🐳 PostgreSQL Docker Setup for CSV Converter"
echo "============================================="

# Check if .env_postgres exists
if [ ! -f ".env_postgres" ]; then
    echo "⚠️  .env_postgres not found. Creating from template..."
    if [ -f ".env_postgres.example" ]; then
        cp .env_postgres.example .env_postgres
        echo "✅ Created .env_postgres from template"
        echo "📝 Please edit .env_postgres with your desired credentials"
        echo ""
    else
        echo "❌ Template file .env_postgres.example not found"
        exit 1
    fi
fi

# Show current configuration
echo "📋 Current PostgreSQL Configuration:"
echo "------------------------------------"
source .env_postgres
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo "Port: $DB_PORT"
echo "Host: $DB_HOST"
echo ""

# Ask user to confirm
read -p "🚀 Start PostgreSQL container with these settings? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🐳 Starting PostgreSQL container..."
    docker-compose up -d postgres

    if [ $? -eq 0 ]; then
        echo "✅ PostgreSQL container started successfully!"
        echo ""
        echo "📊 Connection Details:"
        echo "  Host: $DB_HOST"
        echo "  Port: $DB_PORT"
        echo "  Database: $DB_NAME"
        echo "  User: $DB_USER"
        echo ""
        echo "🔧 Test the connection with:"
        echo "  python csv_converter_pro.py -c config_postgres.yaml list-databases"
    else
        echo "❌ Failed to start PostgreSQL container"
        exit 1
    fi
else
    echo "❌ Setup cancelled"
fi