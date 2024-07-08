from io import BytesIO
import os
import zipfile
from flask import request, jsonify, current_app as app
from werkzeug.utils import secure_filename
from utils.database_connection import database_connect
import mysql.connector
from utils.helpers import validation_file_extension


def upload_media(user_id):
    """Function responsible for uploading media files to the server and adding paths to the database. Allowed methods:
     POST."""
    # Checking if the request contains a file. If not, return status 400.
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    # Getting the file and request data from the request.
    file = request.files["file"]
    request_data = request.form

    # Validate file extension.
    if not file.filename.endswith('.zip'):
        return jsonify({"error": "Unsupported file type, only zip files are allowed"}), 400

    # Create user-specific directory if it doesn't exist.
    user_folder = os.path.join(app.config["UPLOAD_FOLDER"], str(user_id))
    os.makedirs(user_folder, exist_ok=True)

    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Request_data validation. If the data does not meet the validation requirements, an error will be thrown.
        announcement_id = int(request_data.get("announcement_id"))
        if announcement_id <= 0:
            raise ValueError("Invalid announcement_id")

        main_photo_index = request_data.get("main_photo_index")
        if main_photo_index is not None:
            main_photo_index = int(main_photo_index)
            if main_photo_index < 0:
                raise ValueError("Invalid main_photo_index")

        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)

        # Create a BytesIO object from the uploaded ZIP file content.
        zip_buffer = BytesIO(file.read())

        # Open the ZIP file for reading.
        with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
            # Check if the ZIP file is empty.
            if not zip_ref.namelist():
                raise ValueError("Zip file is empty")

            # Validate each file in the ZIP archive.
            for filename in zip_ref.namelist():
                # Check if the file has an allowed extension.
                if not validation_file_extension(filename):
                    raise ValueError(f"Unsupported media type: {filename}")

                # Check if the file size exceeds the maximum allowed size.
                if zip_ref.getinfo(filename).file_size > app.config["MAX_FILE_LENGTH"]:
                    raise ValueError(f"File '{filename}' exceeds the maximum allowed size of"
                                     f" {app.config['MAX_FILE_LENGTH']} bytes")

            # Process and save each file from the ZIP archive.
            for index, filename in enumerate(zip_ref.namelist()):
                # Secure filename and create full file path.
                secured_filename = secure_filename(filename)
                file_path = os.path.join(user_folder, secured_filename)

                # If a file with this name already exists, add a number to the filename.
                if os.path.exists(file_path):
                    base, extension = os.path.splitext(secured_filename)
                    i = 2

                    while True:
                        new_secured_filename = f"{base}_{i}{extension}"
                        new_file_path = os.path.join(user_folder, new_secured_filename)
                        if not os.path.exists(new_file_path):
                            file_path = new_file_path
                            break
                        i += 1

                # Extract and save the file.
                with zip_ref.open(filename) as source, open(file_path, 'wb') as target:
                    target.write(source.read())

                # Determine the table name based on the index.
                table_name = "announcements_main_photo" if index == main_photo_index else "announcements_media"
                query = f"""INSERT INTO {table_name} (user_id, announcement_id, path)
                            VALUES (%s, %s, %s)"""
                cur.execute(query, (user_id, announcement_id, file_path))
                connection.commit()

    # If an error occurs during database operations, return status 500.
    except mysql.connector.Error as error:
        if os.path.exists(file_path):
            os.remove(file_path)
        # If the user wants to add a second profile picture, which is not allowed, it will return a 409 status.
        if "announcement_id_UNIQUE" in error.msg:
            return jsonify(error="Profile picture for announcement already exists."), 409

        # In any other case, the program will return 500.
        return jsonify(error=error.msg), 500

    # If an error occurs while validating the request_data, return status 400.
    except (ValueError, KeyError, TypeError) as error:
        return jsonify(error=str(error)), 400

    # If an error occurs during processing the ZIP file, return status 400.
    except (zipfile.BadZipFile, zipfile.LargeZipFile, OSError):
        return jsonify(error="Error during processing ZIP file."), 400

    # If successful, return status 201.
    else:
        return jsonify(result="Media uploaded successfully"), 201

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()
