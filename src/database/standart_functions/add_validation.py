from database.admin_functions import create_connection


# add validation in to db
def add_validation_for_user(validation_datetime, validation_name, validation_description, user_id):
    try:
        connection, cursor = create_connection()
        sql = """INSERT INTO validations (validation_datetime, validation_name, validation_description, user_id)
                 VALUES (%s, %s, %s, %s) RETURNING validation_id"""
        cursor.execute(sql, (validation_datetime, str(validation_name), str(validation_description), str(user_id)))
        validation_id = cursor.fetchone()[0]
        connection.commit()
        cursor.close()
        print("Data added successfully for user {} with validation_id {}".format(user_id, validation_id))
        connection.close()
        return validation_id
    except Exception as e:
        print("Error adding data for user {}".format(user_id), e)
        return None