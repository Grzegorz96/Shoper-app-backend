from flask import jsonify
from utils.database_connection import database_connect
import mysql.connector


def delete_announcement(announcement_id):
    """Function responsible for deleting completed ones. In practice, the announcement will not be deleted,
    only its flag will change to deleted. Allowed methods: PATCH."""
    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        # Creating request_data.
        request_data = {"announcement_id": announcement_id}

        # Making query.
        query = """UPDATE announcements SET deleted_flag=True, completed_flag=False
                   WHERE announcements.announcement_id=%(announcement_id)s AND completed_flag=True """

        # Executing query.
        cur.execute(query, request_data)
        # Confirmation of changes.
        connection.commit()

    # If an error occurs during database operations, return status 500.
    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    # If it succeeds, return 200 status code.
    else:
        return jsonify(result="Announcement successfully deleted."), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()
