from datetime import datetime

from database.admin_functions import create_connection


# update name for validation
def update_validation_name(new_name, validation_id, user_id):
    try:
        connection, cursor = create_connection()
        sql = "UPDATE validations SET validation_name = %s WHERE validation_id = %s AND user_id = %s"
        cursor.execute(sql, (new_name, validation_id, user_id))
        connection.commit()
        cursor.close()
        connection.close()
        print("Validation name updated successfully, new name is {}".format(new_name))
    except Exception as e:
        print("Error updating validation name:", e)


# update date-time for validation
def update_validation_datetime(new_datetime, validation_id, user_id):
    try:
        try:
            datetime.strptime(new_datetime, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            print("Error: Incorrect datetime format. Please use YYYY-MM-DD HH:MM:SS")
            return

        connection, cursor = create_connection()
        cursor = connection.cursor()
        sql = "UPDATE validations SET validation_datetime = %s WHERE validation_id = %s AND user_id = %s"
        cursor.execute(sql, (new_datetime, validation_id, user_id))
        connection.commit()
        cursor.close()
        connection.close()
        print("Validation datetime updated successfully")
    except Exception as e:
        print("Error updating validation datetime:", e)


# update description for validation
def update_validation_description(new_description, validation_id, user_id):
    try:
        connection, cursor = create_connection()
        sql = "UPDATE validations SET validation_description = %s WHERE validation_id = %s AND user_id = %s"
        cursor.execute(sql, (new_description, validation_id, user_id))
        connection.commit()
        cursor.close()
        connection.close()
        print("Validation description updated successfully")
    except Exception as e:
        print("Error updating validation description:", e)
