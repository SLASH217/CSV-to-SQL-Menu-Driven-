#!/usr/bin/env python3
"""
CSV to SQL Converter - Professional Edition
=============================================

A robust, production-ready tool for converting CSV files to SQL databases
with intelligent data type inference, multiple database support, and
comprehensive error handling.

Features:
- Multiple database support (MySQL, PostgreSQL, SQLite)
- Intelligent data type inference
- Configuration management
- Robust error handling
- Batch processing
- CLI interface
- Logging and monitoring

Author: Enhanced by AI Assistant
Version: 2.0.0
"""

import os
import sys
import logging
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import re
from datetime import datetime

import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
import click
from colorama import init, Fore, Style
from tabulate import tabulate
from tqdm import tqdm

# Initialize colorama for colored output
init(autoreset=True)


@dataclass
class DatabaseConfig:
    """Database configuration dataclass."""
    db_type: str = "mysql"
    host: str = "localhost"
    port: int = 3306
    username: str = "root"
    password: str = ""
    database: str = "csv_converter"

    def get_connection_url(self) -> str:
        """Generate SQLAlchemy connection URL."""
        if self.db_type == "mysql":
            return f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.db_type == "postgresql":
            return f"postgresql+psycopg2://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.db_type == "sqlite":
            return f"sqlite:///{self.database}.db"
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")


class DataTypeInferrer:
    """Intelligent data type inference for CSV columns."""

    def __init__(self):
        self.date_patterns = [
            r'\d{4}-\d{2}-\d{2}',
            r'\d{2}/\d{2}/\d{4}',
            r'\d{2}-\d{2}-\d{4}',
            r'\d{4}/\d{2}/\d{2}'
        ]

    def infer_sql_type(self, series: pd.Series, max_varchar_length: int = 255) -> str:
        """
        Infer SQL data type from pandas Series.

        Args:
            series: Pandas Series to analyze
            max_varchar_length: Maximum VARCHAR length

        Returns:
            SQL data type as string
        """
        # Remove null values for analysis
        non_null_series = series.dropna()

        if len(non_null_series) == 0:
            return "TEXT"

        # Check for boolean
        if self._is_boolean(non_null_series):
            return "BOOLEAN"

        # Check for integers
        if self._is_integer(non_null_series):
            try:
                numeric_series = pd.to_numeric(non_null_series, errors='coerce')
                max_val = numeric_series.max()
                min_val = numeric_series.min()

                if min_val >= -128 and max_val <= 127:
                    return "TINYINT"
                elif min_val >= -32768 and max_val <= 32767:
                    return "SMALLINT"
                elif min_val >= -2147483648 and max_val <= 2147483647:
                    return "INT"
                else:
                    return "BIGINT"
            except:
                return "INT"

        # Check for floating point numbers
        if self._is_float(non_null_series):
            return "DECIMAL(10,2)"

        # Check for dates
        if self._is_date(non_null_series):
            return "DATE"

        # Check for datetime
        if self._is_datetime(non_null_series):
            return "DATETIME"

        # Default to VARCHAR with appropriate length
        try:
            max_length = non_null_series.astype(str).str.len().max()

            if pd.isna(max_length) or max_length > max_varchar_length:
                return "TEXT"
            else:
                return f"VARCHAR({min(int(max_length * 1.2), max_varchar_length)})"
        except:
            return "TEXT"

    def _is_boolean(self, series: pd.Series) -> bool:
        """Check if series contains boolean values."""
        unique_vals = set(series.astype(str).str.lower().unique())
        boolean_vals = {'true', 'false', '1', '0', 'yes', 'no', 'y', 'n'}
        return unique_vals.issubset(boolean_vals)

    def _is_integer(self, series: pd.Series) -> bool:
        """Check if series contains integer values."""
        try:
            # Try to convert to numeric
            numeric_series = pd.to_numeric(series, errors='coerce')

            # Check if all non-null values are integers
            if numeric_series.dropna().empty:
                return False

            return numeric_series.dropna().apply(lambda x: float(x).is_integer()).all()
        except:
            return False

    def _is_float(self, series: pd.Series) -> bool:
        """Check if series contains floating point numbers."""
        try:
            numeric_series = pd.to_numeric(series, errors='coerce')
            if numeric_series.dropna().empty:
                return False
            return not numeric_series.dropna().apply(lambda x: float(x).is_integer()).all()
        except:
            return False

    def _is_date(self, series: pd.Series) -> bool:
        """Check if series contains date values."""
        try:
            sample_str = str(series.iloc[0])
            for pattern in self.date_patterns:
                if re.match(pattern, sample_str):
                    # Try to parse to confirm
                    parsed = pd.to_datetime(series.head(10), errors='coerce')
                    return not parsed.isna().all()
            return False
        except:
            return False

    def _is_datetime(self, series: pd.Series) -> bool:
        """Check if series contains datetime values."""
        try:
            sample_str = str(series.iloc[0])
            datetime_patterns = [
                r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}',
                r'\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}'
            ]

            for pattern in datetime_patterns:
                if re.match(pattern, sample_str):
                    parsed = pd.to_datetime(series.head(10), errors='coerce')
                    return not parsed.isna().all()
            return False
        except:
            return False


class CSVConverter:
    """Main CSV to SQL converter class."""

    def __init__(self, db_config: DatabaseConfig):
        """
        Initialize CSV converter.

        Args:
            db_config: Database configuration
        """
        self.db_config = db_config
        self.engine = None
        self.type_inferrer = DataTypeInferrer()
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # Create console handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def connect(self) -> bool:
        """
        Connect to database.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.engine = create_engine(self.db_config.get_connection_url())
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            self.logger.info("Database connection established successfully")
            return True
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to connect to database: {e}")
            return False

    def disconnect(self):
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            self.logger.info("Database connection closed")

    def list_databases(self) -> List[str]:
        """List all databases."""
        try:
            with self.engine.connect() as conn:
                if self.db_config.db_type == "mysql":
                    result = conn.execute(text("SHOW DATABASES"))
                elif self.db_config.db_type == "postgresql":
                    result = conn.execute(text("SELECT datname FROM pg_database WHERE datistemplate = false"))
                else:  # SQLite
                    return [self.db_config.database]

                return [row[0] for row in result]
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to list databases: {e}")
            return []

    def list_tables(self) -> List[str]:
        """List all tables in current database."""
        try:
            inspector = inspect(self.engine)
            return inspector.get_table_names()
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to list tables: {e}")
            return []

    def create_database(self, db_name: str) -> bool:
        """
        Create a new database.

        Args:
            db_name: Name of database to create

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create temporary connection without database specified
            temp_config = DatabaseConfig(
                db_type=self.db_config.db_type,
                host=self.db_config.host,
                port=self.db_config.port,
                username=self.db_config.username,
                password=self.db_config.password,
                database=""
            )

            if self.db_config.db_type == "mysql":
                url = f"mysql+pymysql://{temp_config.username}:{temp_config.password}@{temp_config.host}:{temp_config.port}/"
            elif self.db_config.db_type == "postgresql":
                url = f"postgresql+psycopg2://{temp_config.username}:{temp_config.password}@{temp_config.host}:{temp_config.port}/postgres"
            else:
                self.logger.info(f"Database creation not needed for SQLite")
                return True

            temp_engine = create_engine(url)

            with temp_engine.connect() as conn:
                conn = conn.execution_options(autocommit=True)
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}`"))

            temp_engine.dispose()
            self.logger.info(f"Database '{db_name}' created successfully")
            return True

        except SQLAlchemyError as e:
            self.logger.error(f"Failed to create database '{db_name}': {e}")
            return False

    def drop_database(self, db_name: str) -> bool:
        """
        Drop a database.

        Args:
            db_name: Name of database to drop

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.engine.connect() as conn:
                conn = conn.execution_options(autocommit=True)
                conn.execute(text(f"DROP DATABASE IF EXISTS `{db_name}`"))

            self.logger.info(f"Database '{db_name}' dropped successfully")
            return True

        except SQLAlchemyError as e:
            self.logger.error(f"Failed to drop database '{db_name}': {e}")
            return False

    def analyze_csv(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze CSV file structure and data types.

        Args:
            file_path: Path to CSV file

        Returns:
            Dictionary with analysis results
        """
        try:
            # Read CSV file
            df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)

            analysis = {
                'file_path': file_path,
                'file_size': os.path.getsize(file_path),
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'columns': {}
            }

            # Analyze each column
            for col in df.columns:
                col_analysis = {
                    'original_name': col,
                    'clean_name': self._clean_column_name(col),
                    'sql_type': self.type_inferrer.infer_sql_type(df[col]),
                    'non_null_count': df[col].count(),
                    'null_count': df[col].isnull().sum(),
                    'unique_values': df[col].nunique(),
                    'sample_values': df[col].dropna().head(3).tolist()
                }

                analysis['columns'][col] = col_analysis

            return analysis

        except Exception as e:
            self.logger.error(f"Failed to analyze CSV file '{file_path}': {e}")
            return {}

    def convert_csv_to_sql(self, csv_file: str, table_name: str,
                          if_exists: str = 'append', chunk_size: int = 10000) -> bool:
        """
        Convert CSV file to SQL table.

        Args:
            csv_file: Path to CSV file
            table_name: Target table name
            if_exists: What to do if table exists ('fail', 'replace', 'append')
            chunk_size: Number of rows to process at once

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Starting conversion: {csv_file} -> {table_name}")

            # Read CSV file
            df = pd.read_csv(csv_file, encoding='utf-8', low_memory=False)

            # Clean column names
            df.columns = [self._clean_column_name(col) for col in df.columns]

            # Convert to SQL with progress bar
            with tqdm(total=len(df), desc="Converting rows") as pbar:
                df.to_sql(
                    name=table_name,
                    con=self.engine,
                    if_exists=if_exists,
                    index=False,
                    chunksize=chunk_size,
                    method='multi'
                )
                pbar.update(len(df))

            self.logger.info(f"Successfully converted {len(df)} rows to table '{table_name}'")
            return True

        except Exception as e:
            self.logger.error(f"Failed to convert CSV to SQL: {e}")
            return False

    def _clean_column_name(self, col_name: str) -> str:
        """Clean column name for database compatibility."""
        # Remove special characters and replace with underscores
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', str(col_name))

        # Remove multiple consecutive underscores
        clean_name = re.sub(r'_+', '_', clean_name)

        # Remove leading/trailing underscores
        clean_name = clean_name.strip('_')

        # Ensure doesn't start with number
        if clean_name and clean_name[0].isdigit():
            clean_name = 'col_' + clean_name

        return clean_name or 'unnamed_column'


class ConfigManager:
    """Configuration manager for the application."""

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager.

        Args:
            config_file: Path to configuration file (YAML or JSON)
        """
        self.config = self._load_default_config()

        if config_file and Path(config_file).exists():
            self._load_config_file(config_file)

        self._load_env_variables()

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration."""
        return {
            'database': {
                'type': 'mysql',
                'host': 'localhost',
                'port': 3306,
                'username': 'root',
                'password': '',
                'database': 'csv_converter'
            },
            'csv': {
                'encoding': 'utf-8',
                'chunk_size': 10000,
                'max_varchar_length': 255
            },
            'logging': {
                'level': 'INFO',
                'file': 'csv_converter.log'
            }
        }

    def _load_config_file(self, config_file: str):
        """Load configuration from file."""
        try:
            with open(config_file, 'r') as f:
                if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                    file_config = yaml.safe_load(f)
                else:
                    file_config = json.load(f)

                # Merge with default config
                self._merge_config(self.config, file_config)
        except Exception as e:
            print(f"Warning: Could not load config file {config_file}: {e}")

    def _load_env_variables(self):
        """Load configuration from environment variables."""
        env_mappings = {
            'DB_TYPE': 'database.type',
            'DB_HOST': 'database.host',
            'DB_PORT': 'database.port',
            'DB_USER': 'database.username',
            'DB_PASSWORD': 'database.password',
            'DB_NAME': 'database.database'
        }

        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                self._set_nested_value(self.config, config_path, value)

    def _merge_config(self, base: Dict, override: Dict):
        """Recursively merge configuration dictionaries."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def _set_nested_value(self, config: Dict, path: str, value: Any):
        """Set nested configuration value using dot notation."""
        keys = path.split('.')
        current = config

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Convert port to int if it's the port setting
        if keys[-1] == 'port':
            value = int(value)

        current[keys[-1]] = value

    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration as DatabaseConfig object."""
        db_config = self.config['database']
        return DatabaseConfig(
            db_type=db_config['type'],
            host=db_config['host'],
            port=db_config['port'],
            username=db_config['username'],
            password=db_config['password'],
            database=db_config['database']
        )


# CLI Implementation
def print_success(message: str):
    """Print success message in green."""
    click.echo(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message: str):
    """Print error message in red."""
    click.echo(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_warning(message: str):
    """Print warning message in yellow."""
    click.echo(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")

def print_info(message: str):
    """Print info message in blue."""
    click.echo(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")


@click.group()
@click.option('--config', '-c', help='Path to configuration file')
@click.pass_context
def cli(ctx, config):
    """CSV to SQL Converter - Professional database import tool."""
    ctx.ensure_object(dict)

    # Load configuration
    config_manager = ConfigManager(config)
    ctx.obj['config'] = config_manager

    # Create converter instance
    db_config = config_manager.get_database_config()
    converter = CSVConverter(db_config)
    ctx.obj['converter'] = converter


@cli.command()
@click.argument('csv_file', type=click.Path(exists=True))
@click.option('--table', '-t', help='Target table name')
@click.option('--if-exists', type=click.Choice(['fail', 'replace', 'append']),
              default='append', help='What to do if table exists')
@click.option('--chunk-size', type=int, default=10000, help='Rows to process at once')
@click.option('--analyze-only', is_flag=True, help='Only analyze the CSV file')
@click.pass_context
def import_csv(ctx, csv_file, table, if_exists, chunk_size, analyze_only):
    """Import CSV file into SQL database."""

    converter = ctx.obj['converter']

    try:
        # Connect to database
        if not converter.connect():
            print_error("Failed to connect to database")
            return

        print_success("Connected to database")

        # Analyze CSV file
        print_info(f"Analyzing CSV file: {csv_file}")
        analysis = converter.analyze_csv(csv_file)

        if not analysis:
            print_error("Failed to analyze CSV file")
            return

        # Display analysis results
        print_info(f"File size: {analysis['file_size']:,} bytes")
        print_info(f"Total rows: {analysis['total_rows']:,}")
        print_info(f"Total columns: {analysis['total_columns']}")

        # Display column information
        headers = ['Column', 'Clean Name', 'SQL Type', 'Non-null', 'Unique', 'Sample']
        rows = []

        for col, info in analysis['columns'].items():
            rows.append([
                col[:20] + '...' if len(col) > 20 else col,
                info['clean_name'][:15] + '...' if len(info['clean_name']) > 15 else info['clean_name'],
                info['sql_type'],
                f"{info['non_null_count']:,}",
                f"{info['unique_values']:,}",
                str(info['sample_values'][0])[:15] + '...' if info['sample_values'] else 'N/A'
            ])

        click.echo(f"\n{Fore.CYAN}Column Analysis:{Style.RESET_ALL}")
        click.echo(tabulate(rows, headers=headers, tablefmt='grid'))

        if analyze_only:
            print_info("Analysis complete (analyze-only mode)")
            return

        # Determine table name
        if not table:
            table = Path(csv_file).stem.lower().replace(' ', '_').replace('-', '_')

        # Confirm import
        if not click.confirm(f"\nImport {analysis['total_rows']:,} rows into table '{table}'?"):
            print_info("Import cancelled")
            return

        # Perform import
        success = converter.convert_csv_to_sql(csv_file, table, if_exists, chunk_size)

        if success:
            print_success(f"Successfully imported data into table '{table}'")
        else:
            print_error("Import failed")

    except Exception as e:
        print_error(f"Error during import: {e}")
    finally:
        converter.disconnect()


@cli.command()
@click.pass_context
def list_databases(ctx):
    """List all databases."""

    converter = ctx.obj['converter']

    try:
        if not converter.connect():
            print_error("Failed to connect to database")
            return

        databases = converter.list_databases()

        if databases:
            print_info("Available databases:")
            for db in databases:
                click.echo(f"  • {db}")
        else:
            print_warning("No databases found")

    finally:
        converter.disconnect()


@cli.command()
@click.pass_context
def list_tables(ctx):
    """List all tables in current database."""

    converter = ctx.obj['converter']

    try:
        if not converter.connect():
            print_error("Failed to connect to database")
            return

        tables = converter.list_tables()

        if tables:
            print_info("Available tables:")
            for table in tables:
                click.echo(f"  • {table}")
        else:
            print_warning("No tables found")

    finally:
        converter.disconnect()


@cli.command()
@click.argument('database_name')
@click.pass_context
def create_database(ctx, database_name):
    """Create a new database."""

    converter = ctx.obj['converter']

    try:
        if not converter.connect():
            print_error("Failed to connect to database")
            return

        if converter.create_database(database_name):
            print_success(f"Database '{database_name}' created successfully")
        else:
            print_error(f"Failed to create database '{database_name}'")

    finally:
        converter.disconnect()


@cli.command()
@click.argument('database_name')
@click.option('--force', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def drop_database(ctx, database_name, force):
    """Drop a database."""

    converter = ctx.obj['converter']

    if not force:
        if not click.confirm(f"Are you sure you want to drop database '{database_name}'?"):
            print_info("Operation cancelled")
            return

    try:
        if not converter.connect():
            print_error("Failed to connect to database")
            return

        if converter.drop_database(database_name):
            print_success(f"Database '{database_name}' dropped successfully")
        else:
            print_error(f"Failed to drop database '{database_name}'")

    finally:
        converter.disconnect()


@cli.command()
@click.pass_context
def interactive(ctx):
    """Start interactive mode with menu-driven interface."""

    converter = ctx.obj['converter']

    while True:
        click.echo(f"\n{Fore.CYAN}=== CSV to SQL Converter - Interactive Mode ==={Style.RESET_ALL}")
        click.echo("1. Import CSV file")
        click.echo("2. Analyze CSV file")
        click.echo("3. List databases")
        click.echo("4. List tables")
        click.echo("5. Create database")
        click.echo("6. Drop database")
        click.echo("7. Exit")

        choice = click.prompt("\nSelect an option", type=int)

        try:
            if choice == 1:
                csv_file = click.prompt("Enter CSV file path", type=click.Path(exists=True))
                table_name = click.prompt("Enter table name (or press Enter for auto)",
                                        default="", show_default=False)

                if not table_name:
                    table_name = Path(csv_file).stem.lower().replace(' ', '_').replace('-', '_')

                if_exists = click.prompt("If table exists",
                                       type=click.Choice(['fail', 'replace', 'append']),
                                       default='append')

                ctx.invoke(import_csv, csv_file=csv_file, table=table_name, if_exists=if_exists)

            elif choice == 2:
                csv_file = click.prompt("Enter CSV file path", type=click.Path(exists=True))
                ctx.invoke(import_csv, csv_file=csv_file, analyze_only=True)

            elif choice == 3:
                ctx.invoke(list_databases)

            elif choice == 4:
                ctx.invoke(list_tables)

            elif choice == 5:
                db_name = click.prompt("Enter database name")
                ctx.invoke(create_database, database_name=db_name)

            elif choice == 6:
                db_name = click.prompt("Enter database name")
                ctx.invoke(drop_database, database_name=db_name)

            elif choice == 7:
                print_info("Goodbye!")
                break

            else:
                print_warning("Invalid choice. Please try again.")

        except KeyboardInterrupt:
            print_info("\nOperation cancelled")
        except Exception as e:
            print_error(f"Error: {e}")


if __name__ == '__main__':
    cli()