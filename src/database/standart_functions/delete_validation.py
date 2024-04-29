from database.admin_functions import create_connection


def delete_validation_by_id(validation_id, user_id):
    try:
        connection, cursor = create_connection()
        sql = "DELETE FROM validations WHERE validation_id = %s AND user_id = %s"
        cursor.execute(sql, (validation_id, user_id))
        connection.commit()
        cursor.close()
        connection.close()
        print("Validation with id {} deleted successfully".format(validation_id))
    except Exception as e:
        print("Error deleting validation with id {}:".format(validation_id), e)
