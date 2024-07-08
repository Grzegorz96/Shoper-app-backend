from flask import request, jsonify
from utils.database_connection import database_connect
import mysql.connector


# @app.route("/users/login-verification", methods=["GET"])
def verify_login():
    """Function responsible for verifying the login entered by the user and informing the user about its availability.
    Allowed methods: GET."""
    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        # Creating request_data.
        request_data = request.get_json()

        # If there is no login key in request_data, throw an error.
        if "login" not in request_data:
            raise ValueError

        # Making query.
        query = """SELECT user_id FROM users WHERE login=%(login)s """

        # Executing query.
        cur.execute(query, request_data)

    # If an error occurs during database operations, return status 500.
    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    # If an error occurs while validating the request_data, return status 415.
    except (ValueError, TypeError, KeyError):
        return jsonify(result="invalid input data."), 415

    else:
        user_id = cur.fetchall()
        # If the operation is successful and the id of a user is retrieved, it means that the user with the given login
        # is in the database and the given login is not available. The program will return status 400.
        if user_id:
            return jsonify(result="The given login is already taken."), 400
        # Otherwise, the user with the given login does not exist, the program will return status 200.
        else:
            return jsonify(result="The given login is available."), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()
