from flask import request, jsonify
from utils.database_connection import database_connect
import mysql.connector
from utils.helpers import create_query_for_getting_messages


def get_messages(user_id):
    """Function responsible for downloading messages using the conversation_id. Allowed methods GET."""
    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        # Creating request_data.
        request_data = request.get_json()
        request_data["user_id"] = user_id

        # Checking whether the conversation_id or announcement_id key is included in request_data.
        if not ("conversation_id" in request_data or "announcement_id" in request_data):
            raise ValueError

        # If conversation_id has been sent, the program will immediately download the list of messages from it.
        if "conversation_id" in request_data:
            messages = create_query_for_getting_messages(cur, request_data)

        # If announcement_id was sent, the program must select conversation_id from the database.
        else:
            # Making query.
            query_check = """SELECT conversation_id FROM conversations
                             WHERE conversations.announcement_id=%(announcement_id)s
                             AND conversations.user_id=%(user_id)s """

            # Executing query.
            cur.execute(query_check, request_data)
            conversation_id = cur.fetchall()
            # If the user has a conversation created for a given announcement, the program will download the messages.
            if conversation_id:
                request_data["conversation_id"] = conversation_id[0]["conversation_id"]
                messages = create_query_for_getting_messages(cur, request_data)
            # If the user does not yet have a conversation for a given ad, an empty list will be returned.
            else:
                messages = []

    # If an error occurs during database operations, return status 500.
    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    # If an error occurs while validating the request_data, return status 400.
    except (ValueError, TypeError, KeyError):
        return jsonify(result="invalid input data."), 400

    # If it succeeds, return JSON with messages and 200 status code.
    else:
        return jsonify(result=messages), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()
