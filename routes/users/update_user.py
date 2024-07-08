from re import match
from flask import request, jsonify
from utils.database_connection import database_connect
import mysql.connector


def update_user(user_id):
    """Function responsible for updating individual user data. Allowed methods: PATCH."""
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

        # Validation of entered data into request_data. If validation fails, the program will throw an error.
        if not request_data["column"] in ("first_name", "last_name", "email", "password", "street", "zip_code", "city"):
            raise ValueError

        if request_data["column"] == "first_name":
            if not match("^[A-ZĘÓĄŚŁŻŹĆŃa-zęóąśłżźćń]{2,45}$", request_data["value"]):
                raise ValueError
        elif request_data["column"] == "last_name":
            if not match("^[A-ZĘÓĄŚŁŻŹĆŃa-zęóąśłżźćń]{2,45}$", request_data["value"]):
                raise ValueError
        elif request_data["column"] == "email":
            if not match("^([A-Za-z0-9]+|[A-Za-z0-9][A-Za-z0-9._-]+[A-Za-z0-9])@([A-Za-z0-9]+"
                         "|[A-Za-z0-9._-]+[A-Za-z0-9])\.[A-Za-z0-9]+$", request_data["value"]):
                raise ValueError
        elif request_data["column"] == "password":
            if not match("^[A-ZĘÓĄŚŁŻŹĆŃa-zęóąśłżźćń0-9!@#$%^&*]{7,45}$", request_data["value"]):
                raise ValueError

        # Making query.
        query = f"""UPDATE users SET {request_data["column"]}=%(value)s
                    WHERE user_id=%(user_id)s AND active_flag=True """

        # Executing query.
        cur.execute(query, request_data)
        # Confirmation of changes.
        connection.commit()

    # If an error occurs during database operations.
    except mysql.connector.Error as message:
        # If the user wants to change their email to an email already in the database, return a status of 400.
        if "email_UNIQUE" in message.msg:
            return jsonify(email_error="The user with the given e-mail address is already registered."), 400
        # In any other case of database related error, return status 500.
        else:
            return jsonify(result=message.msg), 500

    # If an error occurs while validating the request_data, return status 400.
    except (ValueError, TypeError, KeyError):
        return jsonify(result="invalid input data."), 400

    # If it succeeds, return 200 status code.
    else:
        return jsonify(result="User successfully updated."), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()
