#!/usr/bin/env python3
"""
Demo script for CSV to SQL Converter - Professional Edition
Demonstrates the upgraded features without requiring database connection
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import pandas as pd
    from csv_converter_pro import DataTypeInferrer, ConfigManager
    from colorama import init, Fore, Style
    from tabulate import tabulate

    init(autoreset=True)

    def demo_type_inference():
        """Demonstrate intelligent data type inference."""
        print(f"{Fore.CYAN}🧠 Intelligent Data Type Inference Demo{Style.RESET_ALL}")
        print("=" * 50)

        # Load sample data
        if os.path.exists("sample_employees.csv"):
            df = pd.read_csv("sample_employees.csv")

            # Initialize type inferrer
            inferrer = DataTypeInferrer()

            print(f"\n📊 Sample Data Preview:")
            print(df.head(3).to_string(index=False))

            print(f"\n🔍 Inferred SQL Data Types:")
            headers = ['Column', 'Sample Value', 'Inferred SQL Type', 'Reasoning']
            rows = []

            for col in df.columns:
                sample_val = str(df[col].dropna().iloc[0]) if not df[col].dropna().empty else 'N/A'
                sql_type = inferrer.infer_sql_type(df[col])

                # Determine reasoning
                if inferrer._is_boolean(df[col].dropna()):
                    reasoning = "Boolean values detected"
                elif inferrer._is_integer(df[col].dropna()):
                    reasoning = "Integer values detected"
                elif inferrer._is_float(df[col].dropna()):
                    reasoning = "Decimal values detected"
                elif inferrer._is_date(df[col].dropna()):
                    reasoning = "Date format detected"
                else:
                    reasoning = "Text content"

                rows.append([col, sample_val[:20], sql_type, reasoning])

            print(tabulate(rows, headers=headers, tablefmt='grid'))
        else:
            print("❌ Sample CSV file not found. Creating one...")
            create_sample_data()

    def demo_configuration():
        """Demonstrate configuration management."""
        print(f"\n{Fore.CYAN}⚙️ Configuration Management Demo{Style.RESET_ALL}")
        print("=" * 40)

        config_manager = ConfigManager()
        db_config = config_manager.get_database_config()

        print(f"📋 Current Configuration:")
        print(f"   Database Type: {db_config.db_type}")
        print(f"   Host: {db_config.host}:{db_config.port}")
        print(f"   Username: {db_config.username}")
        print(f"   Database: {db_config.database}")

        print(f"\n🔧 Configuration Sources (in priority order):")
        print("   1. Command line arguments")
        print("   2. Environment variables (DB_TYPE, DB_HOST, etc.)")
        print("   3. Configuration file (config.yaml)")
        print("   4. Default values")

    def demo_features():
        """Demonstrate key features."""
        print(f"\n{Fore.CYAN}🚀 Key Features & Improvements{Style.RESET_ALL}")
        print("=" * 45)

        features = [
            ["✅ Multiple Database Support", "MySQL, PostgreSQL, SQLite"],
            ["✅ Intelligent Type Inference", "Automatic SQL type detection"],
            ["✅ Configuration Management", "YAML, ENV vars, CLI options"],
            ["✅ Professional CLI", "Colored output, progress bars"],
            ["✅ Interactive Mode", "Menu-driven interface"],
            ["✅ Error Handling", "Robust error recovery"],
            ["✅ Large File Support", "Chunked processing"],
            ["✅ Data Validation", "CSV analysis before import"],
            ["✅ Security", "No hardcoded credentials"],
            ["✅ Logging", "Comprehensive logging system"]
        ]

        print(tabulate(features, headers=['Feature', 'Description'], tablefmt='grid'))

    def demo_usage_examples():
        """Show usage examples."""
        print(f"\n{Fore.CYAN}💡 Usage Examples{Style.RESET_ALL}")
        print("=" * 30)

        examples = [
            "# Analyze CSV structure",
            "python csv_converter_pro.py import-csv data.csv --analyze-only",
            "",
            "# Import to database",
            "python csv_converter_pro.py import-csv data.csv --table employees",
            "",
            "# Interactive mode",
            "python csv_converter_pro.py interactive",
            "",
            "# List databases",
            "python csv_converter_pro.py list-databases",
            "",
            "# Use custom config",
            "python csv_converter_pro.py -c my_config.yaml import-csv data.csv"
        ]

        for example in examples:
            if example.startswith("#"):
                print(f"{Fore.GREEN}{example}{Style.RESET_ALL}")
            elif example == "":
                print()
            else:
                print(f"  {example}")

    def create_sample_data():
        """Create sample CSV data if it doesn't exist."""
        sample_data = """name,age,salary,hire_date,is_active,department
John Doe,28,75000.50,2023-01-15,true,Engineering
Jane Smith,32,82000.00,2022-08-20,true,Marketing
Bob Johnson,45,95000.75,2021-03-10,false,Sales
Alice Brown,29,68000.25,2023-05-22,true,Engineering"""

        with open("sample_employees.csv", "w") as f:
            f.write(sample_data)
        print("✅ Created sample_employees.csv")

    def main():
        """Main demo function."""
        print(f"{Fore.MAGENTA}🎉 CSV to SQL Converter - Professional Edition Demo{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'=' * 55}{Style.RESET_ALL}")
        print()

        demo_features()
        demo_configuration()
        demo_type_inference()
        demo_usage_examples()

        print(f"\n{Fore.GREEN}🎯 Ready to Use!{Style.RESET_ALL}")
        print("To get started:")
        print(f"  1. Configure database in {Fore.YELLOW}config.yaml{Style.RESET_ALL} or {Fore.YELLOW}.env{Style.RESET_ALL}")
        print(f"  2. Run: {Fore.CYAN}python csv_converter_pro.py --help{Style.RESET_ALL}")
        print(f"  3. Try: {Fore.CYAN}python csv_converter_pro.py interactive{Style.RESET_ALL}")

except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Make sure you've installed all requirements:")
    print("  pip install -r requirements.txt")
    sys.exit(1)

if __name__ == "__main__":
    main()