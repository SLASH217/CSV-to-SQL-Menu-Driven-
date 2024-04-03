# CSV to SQL Converter

This is a Python program that converts CSV files into SQL tables and inserts the data into a MySQL database.

## Features

- Allows users to create their own database or use an existing one.
- Converts CSV data into SQL tables, automatically inferring data types.
- Supports adding new data from CSV files to existing tables without duplicating existing data.
- Provides a user-friendly menu interface for easy navigation.

## Dependencies

- Python 3.x
- MySQL Connector/Python

## Installation

1. Make sure you have Python installed on your system. If not, you can download it from [python.org](https://www.python.org/downloads/).
2. Install MySQL Connector/Python by running `pip install mysql-connector-python` in your terminal.

## Usage

1. Run the program by executing `python csv_to_sql_converter.py` in your terminal.
2. Follow the on-screen prompts:
   - Choose the option to create a new database or use an existing one.
   - Provide the path to the CSV file you want to convert.
   - Optionally, choose to create a new table or append data to an existing one.
3. The program will guide you through the process and provide feedback on the actions taken.

## Example

