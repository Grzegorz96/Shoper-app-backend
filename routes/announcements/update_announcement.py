from re import match
from flask import request, jsonify
from utils.database_connection import database_connect
import mysql.connector


def update_announcement(announcement_id):
    """Function responsible for updating the announcement. Allowed methods: PUT."""
    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        # Creating request_data.
        request_data = request.get_json()
        request_data["announcement_id"] = announcement_id

        # Request_data validation. If the data does not meet the validation requirements, an error will be thrown.
        if (not match("^.{10,45}$", request_data["title"])
                or not match("^[A-ZĘÓĄŚŁŻŹĆŃa-zęóąśłżźćń ]{3,45}$", request_data["location"])
                or not match("^[A-ZĘÓĄŚŁŻŹĆŃa-zęóąśłżźćń]{4,10}$", request_data["state"])
                or not (request_data["mobile_number"] is None or match("^[+]?[0-9]{6,14}$",
                                                                       request_data["mobile_number"]))
                or not (80 <= len(request_data["description"]) <= 400)
                or not (0 <= request_data["price"] <= 9999999)):
            raise ValueError

        # Making query.
        query = """UPDATE announcements
                   SET announcements.title=%(title)s, announcements.description=%(description)s,
                   announcements.price=%(price)s, announcements.location=%(location)s,
                   announcements.state=%(state)s, announcements.mobile_number=%(mobile_number)s
                   WHERE announcements.announcement_id=%(announcement_id)s """

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

    # If it succeeds, return 200 status code.
    else:
        return jsonify(result="Announcement successfully updated."), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()
