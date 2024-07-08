from flask import request, jsonify, current_app as app
from utils.database_connection import database_connect
import mysql.connector
import os


def switch_media(user_id):
    """Function responsible for replacing paths to photos in the database. Moves paths between the main_photo table and
    the media table. Allowed methods: PUT."""
    # Making empty connection and cursor, if connection or cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    # Creating request data from request body.
    request_data = request.get_json()
    main_photo_filename = request_data.get("main_photo_filename")
    media_photo_filename = request_data.get("media_photo_filename")

    # If there are no filenames in the request_data, return status 400.
    if not main_photo_filename and not media_photo_filename:
        return jsonify(error="No filenames provided"), 400

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        user_folder = os.path.join(app.config["UPLOAD_FOLDER"], str(user_id))

        # Request_data validation. If the data does not meet the validation requirements, an error will be thrown.
        announcement_id = int(request_data.get("announcement_id"))
        if announcement_id <= 0:
            raise ValueError("Invalid announcement_id")

        # Making query to switch media.
        if main_photo_filename:
            main_photo_path = os.path.join(user_folder, main_photo_filename)

            query_delete_main = f"""DELETE FROM announcements_main_photo
                                    WHERE announcements_main_photo.path=%s"""
            cur.execute(query_delete_main, (main_photo_path,))
            if cur.rowcount == 0:
                raise ValueError("Main photo not found in the database")

            query_add_media = f"""INSERT INTO announcements_media(user_id, announcement_id, path)
                                  VALUES(%s, %s, %s)"""
            cur.execute(query_add_media, (user_id, announcement_id, main_photo_path))
            if cur.rowcount == 0:
                raise ValueError("Error while adding main photo to media")

        if media_photo_filename:
            media_photo_path = os.path.join(user_folder, media_photo_filename)

            query_delete_media = f"""DELETE FROM announcements_media
                                     WHERE announcements_media.path=%s"""
            cur.execute(query_delete_media, (media_photo_path,))
            if cur.rowcount == 0:
                raise ValueError("Media photo not found in the database")

            query_add_main = f"""INSERT INTO announcements_main_photo(user_id, announcement_id, path)
                                 VALUES(%s, %s, %s)"""
            cur.execute(query_add_main, (user_id, announcement_id, media_photo_path))
            if cur.rowcount == 0:
                raise ValueError("Error while adding media photo to main photo")

        connection.commit()

    # If an error occurs during database operations, return status 500.
    except mysql.connector.Error as error:
        return jsonify(error=error.msg), 500

    # If an error occurs while validating the parameters or request_data, return status 400.
    except (KeyError, ValueError, TypeError) as error:
        return jsonify(error=str(error)), 400

    # If successful, return json with status 200.
    else:
        return jsonify(result="successful operation"), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()
