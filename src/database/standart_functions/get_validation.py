from datetime import datetime, timedelta

from database.admin_functions import create_connection


# get validations for next N days for user
def get_validations_for_days(num_days, user_id):
    try:
        connection, cursor = create_connection()
        start_date = datetime.now()
        end_date = start_date + timedelta(days=num_days)
        sql = "SELECT * FROM validations WHERE validation_datetime >= %s AND validation_datetime < %s AND user_id = %s"
        cursor.execute(sql, (start_date, end_date, user_id))
        validations = cursor.fetchall()
        cursor.close()
        connection.close()
        return validations
    except Exception as e:
        print("Error fetching validations:", e)
        return None


# get all validations for user
def get_all_validations_user(user_id):
    try:
        connection, cursor = create_connection()
        sql = "SELECT * FROM validations WHERE user_id = %s"
        cursor.execute(sql, (str(user_id),))
        validations = cursor.fetchall()
        cursor.close()
        connection.close()
        return validations
    except Exception as e:
        print("Error fetching validations:", e)
        return None


# get validation for user by id
def get_validations_by_user_id(user_id, validation_id):
    try:
        connection, cursor = create_connection()
        sql = "SELECT * FROM validations WHERE user_id = %s AND validation_id = %s"
        cursor.execute(sql, (str(user_id), validation_id))
        validations = cursor.fetchall()
        cursor.close()
        connection.close()
        return validations
    except Exception as e:
        print("Error fetching validations:", e)
        return None
