import os.path

import psycopg2
import configparser

config = configparser.ConfigParser()

config.read('config_bot.ini')

db_user = config['database']['db_user']
db_password = config['database']['db_password']
db_name = config['database']['db_name']
table_name = config['database']['table_name']
run_once_filename = config['database']['run_once_filename']


print(db_user, db_password, db_name, table_name, run_once_filename)


# create connection for db
def create_connection():
    connection = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password
    )
    cursor = connection.cursor()
    return connection, cursor


# run once script for initial table
def execute_run_once_sql():
    try:
        with open(run_once_filename, 'r') as file:
            sql_commands = file.read()

        connection, cursor = create_connection()
        cursor.execute(sql_commands)
        connection.commit()
        cursor.close()
        print("run-once.sql commands executed successfully")
        connection.close()
    except Exception as e:
        print("Failed to execute run-once.sql:", e)


# clear all data
def clear_validation_table():
    try:
        connection, cursor = create_connection()
        sql = f"DELETE FROM validations"
        cursor.execute(sql)
        connection.commit()
        cursor.close()
        print(f"Table validation cleared successfully")
    except Exception as e:
        print("Error clearing table:", e)


# get all validations for ALL users
def get_all_validations():
    try:
        connection, cursor = create_connection()
        sql = "SELECT * FROM validations"
        cursor.execute(sql)
        validations = cursor.fetchall()
        cursor.close()
        connection.close()
        return validations
    except Exception as e:
        print("Error fetching validations:", e)
        return None
