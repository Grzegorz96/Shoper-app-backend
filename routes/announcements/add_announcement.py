from re import match
from flask import request, jsonify
from utils.database_connection import database_connect
import mysql.connector


def add_announcement(user_id):
    """Function responsible for adding an announcement to the database. Allowed methods: POST."""
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

        # Request_data validation. If the data does not meet the validation requirements, an error will be thrown.
        if (not match("^.{10,45}$", request_data["title"])
                or not match("^[A-ZĘÓĄŚŁŻŹĆŃa-zęóąśłżźćń ]{3,45}$", request_data["location"])
                or not match("^[A-ZĘÓĄŚŁŻŹĆŃa-zęóąśłżźćń]{4,10}$", request_data["state"])
                or not (request_data["mobile_number"] is None or match("^[+]?[0-9]{6,14}$",
                                                                       request_data["mobile_number"]))
                or not (80 <= len(request_data["description"]) <= 400)
                or not (0 <= request_data["price"] <= 9999999)
                or not (1 <= request_data["category_id"] <= 12)):
            raise ValueError

        # Making query.
        query = """INSERT INTO announcements(seller_id, category_id, title, description, price,
                   location, active_flag, completed_flag, deleted_flag, state, creation_date, mobile_number)
                   VALUES(%(user_id)s, %(category_id)s, %(title)s, %(description)s, %(price)s, %(location)s,
                   True, False, False, %(state)s, now(), %(mobile_number)s)"""

        # Executing query.
        cur.execute(query, request_data)
        # Confirmation of changes.
        connection.commit()

    # If an error occurs during database operations, return status 500.
    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    # If an error occurs while validating the request_data, return status 400.
    except (ValueError, TypeError, KeyError):
        return jsonify(result="invalid input data."), 400

    # If the announcement is successfully added to the database, the program will return a JSON with the id of the
    # created announcement and status 201.
    else:
        return jsonify(result={"announcement_id": cur.lastrowid}), 201

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()
