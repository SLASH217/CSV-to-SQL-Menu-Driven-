import csv
from re import match
import mysql.connector as conn

mycon = conn.connect(host="localhost", user="root", password="1234")
cursor = mycon.cursor()

current_db = None  # Global variable to store the current database name


def preliminary():
    """allow user to create their own database or use any existing database"""
    global current_db  # Access the global variable

    name_of_database = input(
        "Enter the name of database you want to create: (enter 'no' to use an existing database): "
    )

    if name_of_database != "no":
        query_create_database = f"create database {name_of_database}"
        cursor.execute(query_create_database)
        query_to_use_new = f"use {name_of_database}"
        cursor.execute(query_to_use_new, multi=True)
        print("Database created successfully")
        current_db = name_of_database  # Update the current database
        return name_of_database
    else:
        val_for_databaselist = list_of_databases_func()
        print(val_for_databaselist)
        which_existing_database = input("Enter the name of your existing database: ")
        if which_existing_database in val_for_databaselist:
            query_to_use_old = f"use {which_existing_database} "
            cursor.execute(query_to_use_old)
            print(
                f"You are currently using the database named {which_existing_database}!"
            )
            current_db = which_existing_database  # Update the current database
            return which_existing_database
        else:
            print("Error! Database not found.")


def current_database():
    """Return the name of the current database"""
    return current_db


def list_of_databases_func():
    """creates a list of databases to be used in other functions"""
    query = "show databases;"
    cursor.execute(query)
    dbs = cursor.fetchall()
    list_of_databases = []
    for i in dbs:
        for j in i:
            list_of_databases.append(j)
    return list_of_databases


def delete_database():
    """allows user option to delete the database they created or any existing database"""
    database_list = list_of_databases_func()
    print(database_list)
    delete_choice = input(
        "Enter database name you want to delete: (enter no to skip): "
    )
    if delete_choice in database_list and delete_choice != "no":
        query_delete_db = f"drop database {delete_choice};"
        cursor.execute(query_delete_db)
        print(f"{delete_choice} has been deleted successfully!")
    elif delete_choice == "no":
        print("you skipped option to delete any database!")
    else:
        print("The entered database does not exist!")


def csv_data(file_path):
    """extract data from csv file to convert to sql"""
    formatted_data = []
    with open(file_path, "r", encoding="utf - 8") as file_obj:
        csv_data_table = csv.reader(file_obj)
        for i in csv_data_table:

            formatted_row = (
                []
            )  # Create an empty list to store formatted values for the row
            # Iterate over each value in the row
            for value in i:
                # Check if the value can be converted to an integer
                if value.isdigit():  # If it's a digit (i.e., an integer)
                    formatted_row.append(
                        int(value)
                    )  # Convert it to an integer and append
                else:
                    formatted_row.append(
                        value
                    )  # Otherwise, keep it as a string and append
            formatted_data.append(
                formatted_row
            )  # Append the formatted row to the new data list

    return formatted_data


def create_table(file_path):
    """main objective function which converts data from csv file to sql table"""
    # taking out data from csv file and organizing their datatypes into a list
    with open(file_path, "r", encoding="utf-8") as file_obj:
        reader_obj = csv.reader(file_obj)
        first_row_data = next(reader_obj)
        second_row_data = next(reader_obj)
        date_pattern = r"\b\d{4}-\d{2}-\d{2}\b"

        data_types = []
        for i in second_row_data:
            if i.isalpha() == True:
                data_types.append("varchar(255)")
            elif i.isdigit() == True:
                data_types.append("int(11)")
            elif i.isnumeric:
                if "." in i:
                    data_types.append("float")
            elif match(date_pattern, i):
                data_types.append("date")
            else:
                data_types.append("str")
    # csv part ends
    # --------------------------------------
    # this part of the code creates the stucture of the table
    get_current_database = current_database()
    print("You are currently using the database: " + get_current_database)
    query_use_current = f"use {get_current_database};"
    cursor.execute(query_use_current)
    list_of_tables = []
    query_view_table = "show tables;"
    cursor.execute(query_view_table)
    result_set = cursor.fetchall()
    for row in result_set:
        for item in row:
            list_of_tables.append(item)
    table_name = (
        input(
            "\nEnter the name of the new table you want to create:(enter no to use exixting:) "
        )
        .strip()
        .lower()
    )
    if table_name != "no":
        query_create_table = (
            f"create table {table_name} ({first_row_data[0]} {data_types[0]})"
        )
        cursor.execute(query_create_table)
        no_of_cols = len(first_row_data)
        for i in range(1, no_of_cols):
            query_correct_table = (
                f"alter table {table_name} add {first_row_data[i]} {data_types[i]}"
            )
            cursor.execute(query_correct_table)
        receive_csv_data = csv_data(file_path)
        for i in receive_csv_data[1:]:
            csv_values = tuple(i)
            query_add_data = f"insert into {table_name} values {csv_values}"
            cursor.execute(query_add_data)
        mycon.commit()
        print("Data added successfully!")

    elif table_name == "no":
        print(list_of_tables)
        newchanges_existingtable_table(file_path)
    else:
        print("Table already exists in the database")
    # table structure created successfully


def newchanges_existingtable_table(file_path):
    """Append new data from the CSV file to an existing table in the database."""
    existing_table = input("\nEnter the name of the existing table: ").strip()
    query_check_existing = f"select * from {existing_table}"
    cursor.execute(query_check_existing)
    existing_data = [list(row) for row in cursor.fetchall()]  
    csv_data_list = csv_data(file_path)
    new_data_to_insert = []
    for row in csv_data_list[1:]:
        if row not in existing_data:
            new_data_to_insert.append(row)

    if new_data_to_insert:
        for row in new_data_to_insert:
            csv_values = tuple(row)
            query_add_data = f"insert into {existing_table} values {csv_values}"
            cursor.execute(query_add_data)
        mycon.commit()
        print("New data added successfully to the existing table!")
    else:
        print("No new data to add to the existing table.")


def main():
    """main menu based program!"""
    while True:
        print("\nMenu:")
        print("1. Execute preliminary (always run 1 first!)")
        print("2. Create table")
        print("3. Delete database")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            preliminary()
        elif choice == "2":
            file_path = input("Enter the path to the CSV file: ").strip()
            create_table(file_path)
        elif choice == "3":
            delete_database()
        elif choice == "4":
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")


if __name__ == "__main__":
    main()
