from flask import request, jsonify
from utils.database_connection import database_connect
import mysql.connector


def login_user():
    """Function responsible for user login. Retrieves user information from the database and returns it.
    Allowed methods: GET."""
    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        # Creating request data from request body.
        request_data = request.get_json()

        # If the uploaded json did not include the login_or_email and password keys, throw an error.
        if not ("login_or_email" in request_data and "password" in request_data):
            raise ValueError

        # Making query.
        query = """SELECT user_id, first_name, last_name, email, login, password, date_of_birth, street, 
                   zip_code, city, creation_account_date FROM users WHERE 
                   ((login=%(login_or_email)s AND password=%(password)s) OR (email=%(login_or_email)s 
                   AND password=%(password)s)) AND users.active_flag=True"""

        # Executing query.
        cur.execute(query, request_data)

    # If an error occurs during database operations, return status 500.
    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    # If an error occurs while validating the request_data, return status 415.
    except (ValueError, TypeError, KeyError):
        return jsonify(result="invalid input data."), 415

    else:
        # If the user is retrieved, the program will convert the DATETIME object to a string and return the user data
        # with a status of 200.
        user_info = cur.fetchall()
        if user_info:
            for user in user_info:
                user["creation_account_date"] = str(user["creation_account_date"])
            return jsonify(result=user_info[0]), 200
        # If an empty list is retrieved, return status 400.
        else:
            return jsonify(result="The user does not exist in the database."), 400

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()
