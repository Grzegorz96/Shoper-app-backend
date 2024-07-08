from flask import request, jsonify
from utils.database_connection import database_connect
import mysql.connector


def send_message(user_id):
    """Function responsible for adding sent messages to the database. Allowed methods: POST."""
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

        # Validation of data downloaded to request_data.
        if not ("conversation_id" in request_data or "announcement_id" in request_data):
            raise ValueError

        if not isinstance(request_data["customer_flag"], bool):
            raise ValueError

        if request_data["content"] == "":
            raise ValueError

        # If the conversation_id key has been sent, the program can directly add the message to the database.
        if "conversation_id" in request_data:
            query = """INSERT INTO messages(conversation_id, user_id, customer_flag, content, date)
                       VALUES(%(conversation_id)s, %(user_id)s, %(customer_flag)s, %(content)s, now())"""

            # Executing query.
            cur.execute(query, request_data)
            # Confirmation of changes.
            connection.commit()

        # If the announcement_id key was sent, it means that the program must first create a conversation and then
        # create a message for it.
        else:
            # Create a conversation.
            query_make_conv = """INSERT INTO conversations(announcement_id, user_id)
                                 VALUES(%(announcement_id)s, %(user_id)s) """
            cur.execute(query_make_conv, request_data)

            # Retrieving the id of the created conversation.
            query_check_conv_id = """SELECT conversation_id FROM conversations
                                     WHERE conversations.announcement_id=%(announcement_id)s
                                     AND conversations.user_id=%(user_id)s """
            cur.execute(query_check_conv_id, request_data)

            # Create a message for the conversation created.
            request_data["conversation_id"] = cur.fetchall()[0]["conversation_id"]
            query_add_message = """INSERT INTO messages(conversation_id, user_id, customer_flag, content, date)
                                   VALUES(%(conversation_id)s, %(user_id)s, %(customer_flag)s, %(content)s, now())"""
            cur.execute(query_add_message, request_data)
            # If everything is successful, accept the changes.
            connection.commit()

    # If an error occurs during database operations, return status 500.
    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    # If an error occurs while validating the request_data, return status 400.
    except (ValueError, TypeError, KeyError):
        return jsonify(result="invalid input data."), 400

    # If it succeeds, return 201 status code.
    else:
        return jsonify(result="Message successfully sent."), 201

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()
