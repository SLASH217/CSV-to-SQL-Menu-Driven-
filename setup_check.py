#!/usr/bin/env python3
"""
Quick setup and verification script for CSV to SQL Converter
"""

import os
import sys
import subprocess
from pathlib import Path

def print_status(message, status="info"):
    """Print colored status messages."""
    colors = {
        "info": "\033[34m",    # Blue
        "success": "\033[32m", # Green
        "warning": "\033[33m", # Yellow
        "error": "\033[31m",   # Red
        "reset": "\033[0m"     # Reset
    }

    symbols = {
        "info": "ℹ",
        "success": "✅",
        "warning": "⚠",
        "error": "❌"
    }

    color = colors.get(status, colors["info"])
    symbol = symbols.get(status, "•")

    print(f"{color}{symbol} {message}{colors['reset']}")

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_status(f"Python {version.major}.{version.minor}.{version.micro} - Compatible", "success")
        return True
    else:
        print_status(f"Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+", "error")
        return False

def check_virtual_environment():
    """Check if virtual environment exists and is activated."""
    venv_path = Path("venv")

    if not venv_path.exists():
        print_status("Virtual environment not found", "warning")
        return False

    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_status("Virtual environment is active", "success")
        return True
    else:
        print_status("Virtual environment exists but not activated", "warning")
        return False

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        "pandas", "sqlalchemy", "click", "colorama",
        "tabulate", "tqdm", "pyyaml", "pymysql"
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print_status(f"{package} - Installed", "success")
        except ImportError:
            print_status(f"{package} - Missing", "error")
            missing_packages.append(package)

    return len(missing_packages) == 0, missing_packages

def create_sample_config():
    """Create sample configuration files if they don't exist."""
    config_files = {
        ".env": """# Database Configuration
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=csv_converter

# Logging
LOG_LEVEL=INFO""",

        "config.yaml": """# CSV to SQL Converter Configuration
database:
  type: "mysql"        # mysql, postgresql, sqlite
  host: "localhost"
  port: 3306
  username: "root"
  password: ""         # Set your password here or use environment variables
  database: "csv_converter"

csv:
  encoding: "utf-8"
  chunk_size: 10000
  max_varchar_length: 255

logging:
  level: "INFO"
  file: "csv_converter.log" """
    }

    for filename, content in config_files.items():
        if not Path(filename).exists():
            with open(filename, 'w') as f:
                f.write(content)
            print_status(f"Created {filename}", "success")
        else:
            print_status(f"{filename} already exists", "info")

def run_quick_test():
    """Run a quick functionality test."""
    try:
        # Test import of main modules
        from csv_converter_pro import CSVConverter, DatabaseConfig
        print_status("Core modules import successfully", "success")

        # Test basic functionality
        config = DatabaseConfig()
        print_status("Configuration loading works", "success")

        return True
    except Exception as e:
        print_status(f"Test failed: {e}", "error")
        return False

def main():
    """Main setup function."""
    print("🚀 CSV to SQL Converter - Setup & Verification")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        print_status("Please upgrade to Python 3.8 or higher", "error")
        return False

    # Check virtual environment
    venv_active = check_virtual_environment()
    if not venv_active:
        print_status("To activate virtual environment, run:", "info")
        print("   source venv/bin/activate")
        print("   # or on Windows: venv\\Scripts\\activate")

    # Check dependencies
    deps_ok, missing = check_dependencies()
    if not deps_ok:
        print_status("Missing dependencies detected", "warning")
        print_status("To install missing packages, run:", "info")
        print(f"   pip install {' '.join(missing)}")
        return False

    # Create sample configuration
    print_status("Setting up configuration files...", "info")
    create_sample_config()

    # Run quick test
    print_status("Running functionality test...", "info")
    if run_quick_test():
        print_status("All tests passed!", "success")
    else:
        print_status("Some tests failed", "warning")

    # Provide next steps
    print("\n🎯 Next Steps:")
    print("1. Edit config.yaml or .env with your database credentials")
    print("2. Run: python csv_converter_pro.py --help")
    print("3. Try: python csv_converter_pro.py import-csv sample_employees.csv --analyze-only")
    print("4. Or: python csv_converter_pro.py interactive")

    print_status("Setup complete!", "success")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)