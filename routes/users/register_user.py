from re import match
from flask import request, jsonify
from utils.database_connection import database_connect
import mysql.connector


def register_user():
    """Function responsible for user registration. Sends a query to the database to enter user data.
    Allowed methods: POST."""
    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        # Creating request data from request body.
        request_data = request.get_json()

        # Request_data validation. If the data does not meet the validation requirements, an error will be thrown.
        if (not match("^[A-ZĘÓĄŚŁŻŹĆŃa-zęóąśłżźćń]{2,45}$", request_data["first_name"])
                or not match("^[A-ZĘÓĄŚŁŻŹĆŃa-zęóąśłżźćń]{2,45}$", request_data["last_name"])
                or not match("^([A-Za-z0-9]+|[A-Za-z0-9][A-Za-z0-9._-]+[A-Za-z0-9])@([A-Za-z0-9]+"
                             "|[A-Za-z0-9._-]+[A-Za-z0-9])\.[A-Za-z0-9]+$", request_data["email"])
                or not match("^[A-ZĘÓĄŚŁŻŹĆŃa-zęóąśłżźćń0-9]{5,45}$", request_data["login"])
                or not match("^[A-ZĘÓĄŚŁŻŹĆŃa-zęóąśłżźćń0-9!@#$%^&*]{7,45}$", request_data["password"])
                or not match("^[0-9A-ZĘÓĄŚŁŻŹĆŃa-zęóąśłżźćń-]{10,20}$", request_data["date_of_birth"])):
            raise ValueError

        # Making query.
        query = """INSERT INTO users(first_name, last_name, email, login, password,
                   date_of_birth, street, zip_code, city, active_flag, creation_account_date)
                   VALUES(%(first_name)s, %(last_name)s, %(email)s, %(login)s, %(password)s, %(date_of_birth)s,
                   %(street)s, %(zip_code)s, %(city)s, True, now())"""

        # Execute SELECT query.
        cur.execute(query, request_data)
        # Confirmation of changes.
        connection.commit()

    # If an error occurs during database operations.
    except mysql.connector.Error as message:
        # If "login_UNIQUE" in message.msg it means that user with the given login is already in database, login
        # column has unique key. Returning 400 status.
        if "login_UNIQUE" in message.msg:
            return jsonify(login_error="The user with the given login is already registered."), 400

        # If "email_UNIQUE" in message.msg it means that user with the given email is already in database, email
        # column has unique key. Returning 400 status.
        elif "email_UNIQUE" in message.msg:
            return jsonify(email_error="The user with the given e-mail address is already registered."), 400

        # If other error, returning 500 status.
        else:
            return jsonify(result=message.msg), 500

    # If an error occurs while validating the request_data, return status 400.
    except (ValueError, TypeError, KeyError):
        return jsonify(result="invalid input data."), 400

    # If it succeeds, return 201 status code.
    else:
        return jsonify(result="User successfully created."), 201

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()
