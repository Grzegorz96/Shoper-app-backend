from flask import jsonify
from utils.database_connection import database_connect
import mysql.connector


def delete_user(user_id):
    """Function responsible for deleting the user account. Allowed methods: DELETE."""
    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)

        # Making query.
        query = f"""UPDATE users SET active_flag=False WHERE user_id={user_id} AND active_flag=True """

        # Executing query.
        cur.execute(query)
        # Confirmation of changes.
        connection.commit()

    # If an error occurs during database operations, return status 500.
    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    # If it succeeds, return 200 status code.
    else:
        return jsonify(result="User successfully deleted."), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()
