from io import BytesIO
import os
import zipfile
from flask import jsonify, send_file
from utils.database_connection import database_connect
import mysql.connector


def download_media(announcement_id):
    """Function responsible for downloading media files associated with the announcement. Allowed methods: GET."""
    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)

        # Making query to get main photo path.
        query_main_photo = f"""SELECT announcements_main_photo.path FROM announcements_main_photo
                        WHERE announcements_main_photo.announcement_id={announcement_id} """

        cur.execute(query_main_photo)
        main_photo_path = cur.fetchall()

        # Making query to get media paths.
        query_media = f"""SELECT announcements_media.path FROM announcements_media
                        WHERE announcements_media.announcement_id={announcement_id} """

        cur.execute(query_media)
        media_paths = cur.fetchall()

        # Connecting main photo path with media paths.
        all_paths = main_photo_path + media_paths

        # Create a buffer and save files to ZIP.
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
            for media in all_paths:
                path = media['path']
                if os.path.exists(path):
                    zip_file.write(path, os.path.basename(path))

        # Set the pointer to the beginning of the buffer.
        zip_buffer.seek(0)

        # Prepare response with ZIP file.
        response = send_file(zip_buffer, mimetype='application/zip', as_attachment=True,
                             download_name=f"announcement_{announcement_id}_media.zip")

        # If there is a main photo, add it to the response headers.
        if main_photo_path:
            response.headers['X-Main-Photo'] = os.path.basename(main_photo_path[0]["path"])

    # If an error occurs during database operations, return status 500.
    except mysql.connector.Error as error:
        return jsonify(error=error.msg), 500

    # If an error occurs while creating zip file, return status 500.
    except (zipfile.BadZipFile, FileNotFoundError, IOError, OSError, ValueError, TypeError, EOFError):
        return jsonify(rerror="Error during creating zip file."), 500

    # If successful, return response with status 200.
    else:
        return response, 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()
