# Import of database connection function.
from database_connection import database_connect
# Import of a helpers functions.
from helpers import (validation_file_extension, convert_image_to_base64, create_query_for_search_engine,
                     create_query_for_getting_messages)
from werkzeug.utils import secure_filename
# Import of a module operating on a database.
import mysql.connector
# Importing a module for creating APIs.
from flask import Flask, jsonify, request, send_file
# Import of the validating module.
from re import match
# Import of a library that performs operations on the operating system.
import os
# Import of a function that loads environment variables into the module.
from dotenv import load_dotenv
import zipfile
from io import BytesIO

# Loading environment variables.
load_dotenv()
# Creating an application object.
app = Flask(__name__)
# Assigning the folder path with users' media files with the application's UPLOAD_FOLDER key.
app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER")
# Setting the maximum size of files uploaded to the server.
app.config["MAX_CONTENT_LENGTH"] = 3 * 1024 * 1024
# Setting the maximum size of a single file in a ZIP archive.
app.config["MAX_FILE_LENGTH"] = 200 * 1024


@app.route("/media/upload/<user_id>", methods=["POST"])
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
    user_folder = os.path.join(app.config["UPLOAD_FOLDER"], user_id)
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
    
    # If successful, return status 201.
    else:
        return jsonify(result="Media uploaded successfully"), 201

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()


@app.route("/announcements/<int:announcement_id>/media", methods=["GET"])
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


@app.route("/media/delete/<user_id>", methods=["DELETE"])
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
        user_folder = os.path.join(app.config["UPLOAD_FOLDER"], user_id)

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


@app.route("/media/switch/<user_id>", methods=["PUT"])
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
        user_folder = os.path.join(app.config["UPLOAD_FOLDER"], user_id)

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

            query_add_media = f"""INSERT INTO announcements_media(user_id, announcement_id, path)
                                  VALUES(%s, %s, %s)"""
            cur.execute(query_add_media, (user_id, announcement_id, main_photo_path))
        
        if media_photo_filename:
            media_photo_path = os.path.join(user_folder, media_photo_filename)
           
            query_delete_media = f"""DELETE FROM announcements_media
                                     WHERE announcements_media.path=%s"""
            cur.execute(query_delete_media, (media_photo_path,))

            query_add_main = f"""INSERT INTO announcements_main_photo(user_id, announcement_id, path)
                                 VALUES(%s, %s, %s)""" 
            cur.execute(query_add_main, (user_id, announcement_id, media_photo_path))

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


@app.route("/users/register", methods=["POST"])
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


@app.route("/users/login", methods=["GET"])
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


@app.route("/announcements/<int:announcement_id>", methods=["PUT"])
def update_announcement_data(announcement_id):
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


@app.route("/users/<int:user_id>/announcements", methods=["GET"])
def get_user_announcements(user_id):
    """Function responsible for downloading user announcements. Allowed methods: GET."""
    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)

        # Getting the active_flag from the transferred parameter. Parameter validation.
        active_flag = int(request.args.get("active_flag"))
        if not (active_flag == 0 or active_flag == 1):
            raise ValueError

        # Getting the per_page from the transferred parameter. Parameter validation.
        per_page = int(request.args.get("per_page"))
        if not per_page > 0:
            raise ValueError

        # Getting the page from the transferred parameter. Parameter validation.
        page = int(request.args.get("page"))
        if not page > 0:
            raise ValueError

        # Creating an offset after successful validation.
        offset = (page * per_page) - per_page

        # Creating request_data.
        request_data = {
            "user_id": user_id,
            "per_page": per_page,
            "offset": offset
        }

        # Checking whether the user has selected an active announcements.
        if active_flag:
            field = "active_flag"
        else:
            field = "completed_flag"

        # Making query.
        query = f"""SELECT announcements.announcement_id, users.first_name, 
                    announcements.seller_id, categories.name_category,  
                    announcements.category_id, announcements.title,
                    announcements.description, announcements.price, announcements.location,
                    announcements_main_photo.path AS main_photo, announcements.state,
                    announcements.creation_date, announcements.mobile_number
                    FROM announcements 
                    JOIN categories ON announcements.category_id=categories.category_id
                    JOIN users ON announcements.seller_id=users.user_id
                    LEFT JOIN announcements_main_photo
                    ON announcements.announcement_id=announcements_main_photo.announcement_id
                    WHERE announcements.seller_id=%(user_id)s 
                    AND announcements.{field}=True
                    ORDER BY announcements.announcement_id DESC
                    LIMIT %(per_page)s OFFSET %(offset)s """

        # Executing query.
        cur.execute(query, request_data)

    # If an error occurs during database operations, return status 500.
    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    # If an error occurs while validating parameters, return status 400.
    except (KeyError, ValueError, TypeError):
        return jsonify(result="Bad parameters. Required parameters: "
                              "/?page=in:>0&per_page=int:>0&active_flag=int:1/0."), 400

    # If the operation is successful, the program converts the DATETIME object to a string for each announcement and
    # returns JSON with status 200.
    else:
        user_announcements = cur.fetchall()
        for announcement in user_announcements:
            announcement["creation_date"] = str(announcement["creation_date"])
         
            if announcement["main_photo"]:
                announcement["main_photo"] = convert_image_to_base64(announcement["main_photo"])

        return jsonify(result=user_announcements), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()


@app.route("/users/<int:user_id>/announcements", methods=["POST"])
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


@app.route("/users/login-verification", methods=["GET"])
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


@app.route("/users/<int:user_id>", methods=["PATCH"])
def update_user_data(user_id):
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


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """Function responsible for deleting the user account. Allowed methods: DELETE."""
    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
       
        # Making query.
        query = f"""UPDATE users SET active_flag=False WHERE user_id={user_id} AND active_flag=True """

        # Executing query.
        cur.execute(query)
        # Confirmation of changes.
        connection.commit()

    # If an error occurs during database operations, return status 500.
    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    # If it succeeds, return 200 status code.
    else:
        return jsonify(result="User successfully deleted."), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()


@app.route("/announcements/<int:announcement_id>/complete", methods=["PATCH"])
def complete_the_announcement(announcement_id):
    """Function responsible for terminating active user announcements. Allowed methods: PATCH."""
    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        # Creating request_data.
        request_data = {"announcement_id": announcement_id}

        # Making query.
        query = """UPDATE announcements SET completed_flag=True, active_flag=False
                   WHERE announcements.announcement_id=%(announcement_id)s AND active_flag=True """

        # Executing query.
        cur.execute(query, request_data)
        # Confirmation of changes.
        connection.commit()

    # If an error occurs during database operations, return status 500.
    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    # If it succeeds, return 200 status code.
    else:
        return jsonify(result="Announcement successfully completed."), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()


@app.route("/announcements/<int:announcement_id>/restore", methods=["PATCH"])
def restore_the_announcement(announcement_id):
    """Function responsible for restoring completed announcements to active ones. Allowed methods: PATCH."""
    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        # Creating request_data.
        request_data = {"announcement_id": announcement_id}
        # Making query.
        query = """UPDATE announcements SET active_flag=True, completed_flag=False
                   WHERE announcements.announcement_id=%(announcement_id)s AND completed_flag=True """

        # Executing query.
        cur.execute(query, request_data)
        # Confirmation of changes.
        connection.commit()

    # If an error occurs during database operations, return status 500.
    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    # If it succeeds, return 200 status code.
    else:
        return jsonify(result="Announcement successfully restored."), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()


@app.route("/announcements/<int:announcement_id>/delete", methods=["PATCH"])
def delete_the_announcement(announcement_id):
    """Function responsible for deleting completed ones. In practice, the announcement will not be deleted,
    only its flag will change to deleted. Allowed methods: PATCH."""
    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        # Creating request_data.
        request_data = {"announcement_id": announcement_id}

        # Making query.
        query = """UPDATE announcements SET deleted_flag=True, completed_flag=False
                   WHERE announcements.announcement_id=%(announcement_id)s AND completed_flag=True """

        # Executing query.
        cur.execute(query, request_data)
        # Confirmation of changes.
        connection.commit()

    # If an error occurs during database operations, return status 500.
    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    # If it succeeds, return 200 status code.
    else:
        return jsonify(result="Announcement successfully deleted."), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()


@app.route("/users/<int:user_id>/favorite-announcements", methods=["GET"])
def get_user_favorite_announcements(user_id):
    """Function responsible for downloading the user's favorite announcements. Allowed methods: GET."""
    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)

        # Getting the active_flag from the transferred parameter. Parameter validation.
        active_flag = int(request.args.get("active_flag"))
        if not (active_flag == 0 or active_flag == 1):
            raise ValueError

        # Getting the per_page from the transferred parameter. Parameter validation.
        per_page = int(request.args.get("per_page"))
        if not per_page > 0:
            raise ValueError

        # Getting the page from the transferred parameter. Parameter validation.
        page = int(request.args.get("page"))
        if not page > 0:
            raise ValueError

        # Creating an offset after successful validation.
        offset = (page * per_page) - per_page

        # Creating request_data.
        request_data = {
            "user_id": user_id,
            "per_page": per_page,
            "offset": offset
        }

        # Checking whether the user has selected an active announcements.
        if active_flag:
            field = "active_flag"
        else:
            field = "completed_flag"

        # Making query.
        query = f"""SELECT favorite_announcements.favorite_announcement_id, announcements.announcement_id,
                    users.first_name, announcements.seller_id, announcements.title,   
                    announcements.description, categories.name_category, announcements.price,
                    announcements.location, announcements_main_photo.path AS main_photo,
                    announcements.state, announcements.creation_date, announcements.mobile_number
                    FROM favorite_announcements 
                    JOIN announcements ON favorite_announcements.announcement_id=announcements.announcement_id
                    JOIN categories ON announcements.category_id=categories.category_id
                    JOIN users ON announcements.seller_id=users.user_id
                    LEFT JOIN announcements_main_photo 
                    ON announcements.announcement_id=announcements_main_photo.announcement_id
                    WHERE favorite_announcements.user_id=%(user_id)s 
                    AND announcements.{field}=True
                    ORDER BY favorite_announcements.favorite_announcement_id DESC
                    LIMIT %(per_page)s OFFSET %(offset)s """

        # Executing query.
        cur.execute(query, request_data)

    # If an error occurs during database operations, return status 500.
    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    # If an error occurs while validating parameters, return status 400.
    except (KeyError, ValueError, TypeError):
        return jsonify(result="Bad parameters. Required parameters: "
                              "/?page=int:>0&per_page=int:>0&active_flag=int:1/0."), 400

    # If the operation is successful, the program converts the DATETIME object to a string for each
    # favorite_announcement and returns JSON with status 200.
    else:
        user_favorite_announcements = cur.fetchall()
        for announcement in user_favorite_announcements:
            announcement["creation_date"] = str(announcement["creation_date"])

            if announcement["main_photo"]:
                announcement["main_photo"] = convert_image_to_base64(announcement["main_photo"])

        return jsonify(result=user_favorite_announcements), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()


@app.route("/users/<int:user_id>/favorite-announcements", methods=["POST"])
def add_announcement_to_favorite(user_id):
    """Function responsible for adding announcement to favorites by the user. Allowed methods: POST."""
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

        # If there is no announcement_id key in request_data, throw an error.
        request_data["announcement_id"] = int(request_data["announcement_id"])

        # Making query.
        query_check = """ SELECT favorite_announcement_id FROM favorite_announcements
                          WHERE user_id=%(user_id)s AND announcement_id=%(announcement_id)s """

        # Executing query.
        cur.execute(query_check, request_data)

        # If a record has been downloaded for a specific user and a specific announcement, it means that the user has
        # already liked a given announcement. If an empty list is downloaded, it means that the ad has not been liked
        # before and the program will create a like.
        is_already_liked = cur.fetchall()
        if not is_already_liked:
            query = """ INSERT INTO favorite_announcements(user_id, announcement_id)
                        VALUES(%(user_id)s, %(announcement_id)s) """
            cur.execute(query, request_data)
            connection.commit()
        # When a user wants to like an ad that he or she previously liked, throw an error.
        else:
            raise ReferenceError

    # If an error occurs during database operations, return status 500.
    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    # If an error occurs while validating the request_data, return status 415.
    except (ValueError, TypeError, KeyError):
        return jsonify(result="invalid input data."), 415

    # If it throws an error after downloading favorite announcement, return a status of 400.
    except ReferenceError:
        return jsonify(result="The announcement is already liked"), 400

    # If it succeeds, return 201 status code.
    else:
        return jsonify(result="Successfully added to favorites."), 201

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()


@app.route("/favorite-announcements/<int:favorite_announcement_id>", methods=["DELETE"])
def delete_announcement_from_favorite(favorite_announcement_id):
    """Function responsible for removing an announcement from the user's favorite announcements.
    Allowed methods: DELETE."""
    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        # Creating request_data.
        request_data = {"favorite_announcement_id": favorite_announcement_id}

        # Making query.
        query = """ DELETE FROM favorite_announcements WHERE favorite_announcement_id=%(favorite_announcement_id)s """

        # Executing query.
        cur.execute(query, request_data)
        # Confirmation of changes.
        connection.commit()

    # If an error occurs during database operations, return status 500.
    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    # If it succeeds, return 200 status code.
    else:
        return jsonify(result="Successfully deleted from favorites."), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()


@app.route("/announcements/search", methods=["GET"])
def get_announcements():
    """Function responsible for downloading announcements to the home page. The user can specify additional parameters
    for which he wants to download announcements. Allowed methods: GET."""
    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)

        # Making query.
        query = """ SELECT announcements.announcement_id, users.first_name,
                    announcements.seller_id, categories.name_category, announcements.category_id,
                    announcements.title, announcements.description, 
                    announcements.price, announcements.location, announcements_main_photo.path AS main_photo,
                    announcements.state, announcements.creation_date, announcements.mobile_number
                    FROM announcements 
                    JOIN categories ON announcements.category_id=categories.category_id
                    JOIN users ON announcements.seller_id=users.user_id
                    LEFT JOIN announcements_main_photo
                    ON announcements.announcement_id=announcements_main_photo.announcement_id
                    WHERE announcements.active_flag=True """

        # Getting the per_page from the transferred parameter. Parameter validation.
        per_page = int(request.args.get("per_page"))
        if not per_page > 0:
            raise ValueError

        # Getting the page from the transferred parameter. Parameter validation.
        page = int(request.args.get("page"))
        if not page > 0:
            raise ValueError

        # Creating an offset after successful validation.
        offset = (page * per_page) - per_page

        # Assigning additional optional parameters.
        content_to_search = request.args.get("q")
        location = request.args.get("l")
        category = request.args.get("c")

        # If any of the additional parameters have been sent, the program will dynamically create a query for the given
        # parameter.
        if content_to_search:
            # Init query for search field.
            query = create_query_for_search_engine(content_to_search, query, "announcements.title")

        if location:
            # Init query for location field.
            query = create_query_for_search_engine(location, query, "announcements.location")

        if category:
            # Init query for category id.
            query += f"""AND categories.category_id={category} """

        # Adding the number of announcements and the offset to the query.
        query += f"""ORDER BY announcements.announcement_id DESC
                     LIMIT {per_page} OFFSET {offset}"""

        # Executing query.
        cur.execute(query)

    # If an error occurs during database operations, return status 500.
    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    # If an error occurs while validating parameters, return status 400.
    except (KeyError, ValueError, TypeError):
        return jsonify(result="Bad parameters. Required parameters: /?page=int:>0&per_page=int:>0."
                              " Optional parameters: /?q=str&l=str&c=int:1/12."), 400

    # If the operation is successful, the program converts the DATETIME object to a string for each announcement and
    # returns JSON with status 200.
    else:
        announcements = cur.fetchall()
        for announcement in announcements:
            announcement["creation_date"] = str(announcement["creation_date"])
          
            if announcement["main_photo"]:
                announcement["main_photo"] = convert_image_to_base64(announcement["main_photo"])

        return jsonify(result=announcements), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()


@app.route("/users/<int:user_id>/messages", methods=["GET"])
def get_messages(user_id):
    """Function responsible for downloading messages using the conversation_id. Allowed methods GET."""
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

        # Checking whether the conversation_id or announcement_id key is included in request_data.
        if not ("conversation_id" in request_data or "announcement_id" in request_data):
            raise ValueError

        # If conversation_id has been sent, the program will immediately download the list of messages from it.
        if "conversation_id" in request_data:
            messages = create_query_for_getting_messages(cur, request_data)

        # If announcement_id was sent, the program must select conversation_id from the database.
        else:
            # Making query.
            query_check = """SELECT conversation_id FROM conversations
                             WHERE conversations.announcement_id=%(announcement_id)s
                             AND conversations.user_id=%(user_id)s """

            # Executing query.
            cur.execute(query_check, request_data)
            conversation_id = cur.fetchall()
            # If the user has a conversation created for a given announcement, the program will download the messages.
            if conversation_id:
                request_data["conversation_id"] = conversation_id[0]["conversation_id"]
                messages = create_query_for_getting_messages(cur, request_data)
            # If the user does not yet have a conversation for a given ad, an empty list will be returned.
            else:
                messages = []

    # If an error occurs during database operations, return status 500.
    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    # If an error occurs while validating the request_data, return status 400.
    except (ValueError, TypeError, KeyError):
        return jsonify(result="invalid input data."), 400

    # If it succeeds, return JSON with messages and 200 status code.
    else:
        return jsonify(result=messages), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()


@app.route("/users/<int:user_id>/messages", methods=["POST"])
def send_message(user_id):
    """Function responsible for adding sent messages to the database. Allowed methods: POST."""
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

        # Validation of data downloaded to request_data.
        if not ("conversation_id" in request_data or "announcement_id" in request_data):
            raise ValueError

        if not isinstance(request_data["customer_flag"], bool):
            raise ValueError

        if request_data["content"] == "":
            raise ValueError

        # If the conversation_id key has been sent, the program can directly add the message to the database.
        if "conversation_id" in request_data:
            query = """INSERT INTO messages(conversation_id, user_id, customer_flag, content, date)
                       VALUES(%(conversation_id)s, %(user_id)s, %(customer_flag)s, %(content)s, now())"""

            # Executing query.
            cur.execute(query, request_data)
            # Confirmation of changes.
            connection.commit()

        # If the announcement_id key was sent, it means that the program must first create a conversation and then
        # create a message for it.
        else:
            # Create a conversation.
            query_make_conv = """INSERT INTO conversations(announcement_id, user_id)
                                 VALUES(%(announcement_id)s, %(user_id)s) """
            cur.execute(query_make_conv, request_data)

            # Retrieving the id of the created conversation.
            query_check_conv_id = """SELECT conversation_id FROM conversations
                                     WHERE conversations.announcement_id=%(announcement_id)s
                                     AND conversations.user_id=%(user_id)s """
            cur.execute(query_check_conv_id, request_data)

            # Create a message for the conversation created.
            request_data["conversation_id"] = cur.fetchall()[0]["conversation_id"]
            query_add_message = """INSERT INTO messages(conversation_id, user_id, customer_flag, content, date)
                                   VALUES(%(conversation_id)s, %(user_id)s, %(customer_flag)s, %(content)s, now())"""
            cur.execute(query_add_message, request_data)
            # If everything is successful, accept the changes.
            connection.commit()

    # If an error occurs during database operations, return status 500.
    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    # If an error occurs while validating the request_data, return status 400.
    except (ValueError, TypeError, KeyError):
        return jsonify(result="invalid input data."), 400

    # If it succeeds, return 201 status code.
    else:
        return jsonify(result="Message successfully sent."), 201

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()


@app.route("/users/<int:user_id>/conversations", methods=["GET"])
def get_conversations(user_id):
    """Function responsible for downloading user conversations. Allowed methods: GET."""
    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)

        # Getting the customer_flag from the transferred parameter. Parameter validation.
        customer_flag = int(request.args.get("customer_flag"))
        if not (customer_flag == 0 or customer_flag == 1):
            raise ValueError

        # Getting the per_page from the transferred parameter. Parameter validation.
        per_page = int(request.args.get("per_page"))
        if not per_page > 0:
            raise ValueError

        # Getting the page from the transferred parameter. Parameter validation.
        page = int(request.args.get("page"))
        if not page > 0:
            raise ValueError

        # Creating an offset after successful validation.
        offset = (page * per_page) - per_page

        # Creating request_data.
        request_data = {
            "user_id": user_id,
            "per_page": per_page,
            "offset": offset
        }

        # If the user wants to download conversations as a customer, the variables will receive the following values.
        if customer_flag:
            on_field = "announcements.seller_id"
            where_field = "conversations.user_id"
        # If the user wants to download conversations as a seller, the variables will receive the following values.
        else:
            on_field = "conversations.user_id"
            where_field = "announcements.seller_id"

        # Making query.
        query = f"""SELECT conversations.conversation_id, 
                    conversations.announcement_id, announcements.title,
                    users.first_name FROM conversations 
                    JOIN announcements ON conversations.announcement_id=
                    announcements.announcement_id
                    JOIN users ON {on_field}=users.user_id
                    WHERE {where_field}=%(user_id)s 
                    AND (announcements.active_flag=True OR 
                    announcements.completed_flag=True)
                    ORDER BY conversations.conversation_id DESC
                    LIMIT %(per_page)s OFFSET %(offset)s """

        # Executing query.
        cur.execute(query, request_data)

    # If an error occurs during database operations, return status 500.
    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    # If an error occurs while validating parameters, return status 400.
    except (KeyError, ValueError, TypeError):
        return jsonify(result="Bad parameters. Required parameters:"
                              " /?page=int:>0&per_page=int:>0&customer_flag=int:1/0."), 400

    # If it succeeds, return JSON with list of conversations and 200 status code.
    else:
        return jsonify(result=cur.fetchall()), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()


# Running the application on the server.
if __name__ == "__main__":
    app.run(debug=True, port=5000)
