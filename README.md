# CSV to SQL Converter - Professional Edition

A robust, production-ready command-line tool for converting CSV files to SQL databases with intelligent data type inference, multiple database support, and comprehensive error handling.

## 🚀 Features

### Core Functionality
- **Multiple Database Support**: MySQL, PostgreSQL, SQLite
- **Intelligent Data Type Inference**: Automatically detects optimal SQL data types
- **Batch Processing**: Handles large files with configurable chunk sizes
- **Data Validation**: Comprehensive CSV file validation and analysis
- **Error Handling**: Robust error handling with detailed logging

### User Interface
- **Command Line Interface**: Professional CLI with colored output
- **Interactive Mode**: Menu-driven interface for ease of use
- **Progress Tracking**: Visual progress bars for long operations
- **Detailed Analysis**: Preview data structure before import

### Configuration & Security
- **Flexible Configuration**: YAML files, environment variables, CLI options
- **Security**: No hardcoded credentials, environment variable support
- **Logging**: Comprehensive logging with configurable levels

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Virtual environment (recommended)

### Setup
```bash
# Clone the repository
git clone https://github.com/SLASH217/CSV-to-SQL-Menu-Driven-.git
cd CSV-to-SQL-Menu-Driven-

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Database Setup
Install the appropriate database driver:

```bash
# For MySQL
pip install pymysql

# For PostgreSQL
pip install psycopg2-binary

# SQLite is included with Python
```

## ⚙️ Configuration

### Method 1: Configuration File (Recommended)
Copy and edit the configuration file:
```bash
cp config.yaml my_config.yaml
# Edit my_config.yaml with your settings
```

### Method 2: Environment Variables
```bash
cp .env.example .env
# Edit .env with your database credentials
```

### Method 3: Command Line Arguments
Pass configuration directly via CLI options.

## 🎯 Usage

### Quick Start
```bash
# Analyze a CSV file
python csv_converter_pro.py import-csv sample.csv --analyze-only

# Import CSV to database
python csv_converter_pro.py import-csv sample.csv --table my_table

# Interactive mode
python csv_converter_pro.py interactive
```

### Available Commands

#### Import CSV
```bash
python csv_converter_pro.py import-csv FILE [OPTIONS]

Options:
  -t, --table TEXT          Target table name
  --if-exists [fail|replace|append]  What to do if table exists (default: append)
  --chunk-size INTEGER      Rows to process at once (default: 10000)
  --analyze-only           Only analyze the CSV file
```

#### Database Management
```bash
# List databases
python csv_converter_pro.py list-databases

# List tables
python csv_converter_pro.py list-tables

# Create database
python csv_converter_pro.py create-database DB_NAME

# Drop database
python csv_converter_pro.py drop-database DB_NAME [--force]
```

#### Interactive Mode
```bash
python csv_converter_pro.py interactive
```

### Configuration Options
```bash
# Use custom config file
python csv_converter_pro.py -c my_config.yaml import-csv file.csv

# All commands support the -c/--config option
```

## 📊 Data Type Inference

The tool automatically infers SQL data types based on your CSV content:

| CSV Content | SQL Type | Example |
|-------------|----------|---------|
| Integer numbers | TINYINT/SMALLINT/INT/BIGINT | 42, 1000 |
| Decimal numbers | DECIMAL(10,2) | 3.14, 99.99 |
| Boolean values | BOOLEAN | true, false, 1, 0 |
| Date strings | DATE | 2023-12-25, 25/12/2023 |
| DateTime strings | DATETIME | 2023-12-25 10:30:00 |
| Text content | VARCHAR(n) or TEXT | Names, descriptions |

## 🔧 Advanced Usage

### Large File Processing
```bash
# Process large files with smaller chunks
python csv_converter_pro.py import-csv large_file.csv --chunk-size 5000

# Replace existing table for fresh import
python csv_converter_pro.py import-csv data.csv --if-exists replace
```

### Multiple Database Types
```bash
# MySQL (default)
DB_TYPE=mysql python csv_converter_pro.py import-csv data.csv

# PostgreSQL
DB_TYPE=postgresql python csv_converter_pro.py import-csv data.csv

# SQLite
DB_TYPE=sqlite python csv_converter_pro.py import-csv data.csv
```

## 📋 Examples

### Example 1: Basic CSV Import
```bash
# Analyze first
python csv_converter_pro.py import-csv sales_data.csv --analyze-only

# Import after reviewing
python csv_converter_pro.py import-csv sales_data.csv --table sales
```

### Example 2: Interactive Session
```bash
python csv_converter_pro.py interactive

# Follow the menu prompts:
# 1. Import CSV file
# 2. Analyze CSV file
# 3. List databases
# 4. List tables
# 5. Create database
# 6. Drop database
# 7. Exit
```

### Example 3: Batch Processing
```bash
# Process multiple files
for file in *.csv; do
    python csv_converter_pro.py import-csv "$file" --table "table_$(basename "$file" .csv)"
done
```

## 🛠️ Configuration Reference

### Database Configuration
```yaml
database:
  type: "mysql"           # mysql, postgresql, sqlite
  host: "localhost"
  port: 3306
  username: "root"
  password: ""
  database: "csv_converter"
```

### Processing Configuration
```yaml
csv:
  encoding: "utf-8"       # File encoding
  chunk_size: 10000       # Rows per batch
  max_varchar_length: 255 # Maximum VARCHAR length
```

### Logging Configuration
```yaml
logging:
  level: "INFO"           # DEBUG, INFO, WARNING, ERROR
  file: "csv_converter.log"
```

## 🔍 Troubleshooting

### Common Issues

**Connection Errors**
- Check database credentials in config.yaml or .env
- Ensure database server is running
- Verify network connectivity

**Import Errors**
- Check CSV file encoding (try UTF-8)
- Verify file permissions
- Ensure sufficient disk space

**Memory Issues**
- Reduce chunk_size for large files
- Close other applications
- Consider upgrading system memory

### Debug Mode
```bash
# Enable verbose logging
python csv_converter_pro.py -c config.yaml import-csv file.csv --verbose
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Repository**: https://github.com/SLASH217/CSV-to-SQL-Menu-Driven-
- **Issues**: https://github.com/SLASH217/CSV-to-SQL-Menu-Driven-/issues
- **Documentation**: This README

## 📈 Changelog

### Version 2.0.0
- Complete rewrite with modern Python practices
- Added support for PostgreSQL and SQLite
- Intelligent data type inference
- Professional CLI interface
- Configuration management system
- Comprehensive error handling
- Interactive mode
- Progress tracking
- Detailed logging

### Version 1.0.0
- Basic CSV to MySQL conversion
- Menu-driven interface
- Basic data type detection
