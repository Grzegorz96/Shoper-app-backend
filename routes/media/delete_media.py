from flask import request, jsonify, current_app as app
from utils.database_connection import database_connect
import mysql.connector
import os


def delete_media(user_id):
    """Function responsible for deleting files from the server and database. Allowed methods: DELETE."""
    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    # Creating request data from request body.
    request_data = request.get_json()
    files = request_data.get("files")

    # If there are no files in the request_data, return status 400.
    if not files:
        return jsonify({"error": "No files provided"}), 400

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        # Creating user folder path.
        user_folder = os.path.join(app.config["UPLOAD_FOLDER"], str(user_id))

        # For each file in the request_data, the program will check if the file exists on the server and if so,
        # it will delete it.
        for file in files:
            # Request_data validation. If the data does not meet the validation requirements, an error will be thrown.
            filename = file.get("filename")
            if not filename:
                raise ValueError("No filename provided")

            is_main_photo = file.get("is_main_photo")
            if is_main_photo is None:
                raise ValueError("No is_main_photo provided")

            # Creating a full path to the file.
            path = os.path.join(user_folder, filename)

            # If the file exists, the program will delete it from the server and the database.
            if os.path.exists(path):
                table_name = "announcements_main_photo" if is_main_photo else "announcements_media"
                query = f"""DELETE FROM {table_name} WHERE {table_name}.path=%s"""
                cur.execute(query, (path,))
                os.remove(path)
                connection.commit()
            else:
                raise FileNotFoundError("File doesn't exist")

    # If an error occurs during database operations, return status 500.
    except mysql.connector.Error as error:
        return jsonify(error=error.msg), 500

    # If an error occurs while validating the parameters or request_data, return status 400.
    except (ValueError, KeyError, TypeError) as error:
        return jsonify(error=str(error)), 400

    # If it does not find such a file on the server, return status 404.
    except FileNotFoundError as error:
        return jsonify(error=str(error)), 404

    # If successful, return json with status 200.
    else:
        return jsonify({"result": "Files deleted successfully"}), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()
