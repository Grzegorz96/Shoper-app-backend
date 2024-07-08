from flask import request, jsonify
from utils.database_connection import database_connect
import mysql.connector


def get_conversations(user_id):
    """Function responsible for downloading user conversations. Allowed methods: GET."""
    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)

        # Getting the customer_flag from the transferred parameter. Parameter validation.
        customer_flag = int(request.args.get("customer_flag"))
        if not (customer_flag == 0 or customer_flag == 1):
            raise ValueError

        # Getting the per_page from the transferred parameter. Parameter validation.
        per_page = int(request.args.get("per_page"))
        if not per_page > 0:
            raise ValueError

        # Getting the page from the transferred parameter. Parameter validation.
        page = int(request.args.get("page"))
        if not page > 0:
            raise ValueError

        # Creating an offset after successful validation.
        offset = (page * per_page) - per_page

        # Creating request_data.
        request_data = {
            "user_id": user_id,
            "per_page": per_page,
            "offset": offset
        }

        # If the user wants to download conversations as a customer, the variables will receive the following values.
        if customer_flag:
            on_field = "announcements.seller_id"
            where_field = "conversations.user_id"
        # If the user wants to download conversations as a seller, the variables will receive the following values.
        else:
            on_field = "conversations.user_id"
            where_field = "announcements.seller_id"

        # Making query.
        query = f"""SELECT conversations.conversation_id, 
                    conversations.announcement_id, announcements.title,
                    users.first_name FROM conversations 
                    JOIN announcements ON conversations.announcement_id=
                    announcements.announcement_id
                    JOIN users ON {on_field}=users.user_id
                    WHERE {where_field}=%(user_id)s 
                    AND (announcements.active_flag=True OR 
                    announcements.completed_flag=True)
                    ORDER BY conversations.conversation_id DESC
                    LIMIT %(per_page)s OFFSET %(offset)s """

        # Executing query.
        cur.execute(query, request_data)

    # If an error occurs during database operations, return status 500.
    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    # If an error occurs while validating parameters, return status 400.
    except (KeyError, ValueError, TypeError):
        return jsonify(result="Bad parameters. Required parameters:"
                              " /?page=int:>0&per_page=int:>0&customer_flag=int:1/0."), 400

    # If it succeeds, return JSON with list of conversations and 200 status code.
    else:
        return jsonify(result=cur.fetchall()), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()
