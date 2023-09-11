# Import of database connection function.
from Database_connection import database_connect
# Import of functions that create dynamic queries
from Query_creator import create_query_for_search_engine, create_query_for_getting_messages
# Import of a function validating the file entered to the server.
from Media_validator import validation_file
from werkzeug.utils import secure_filename
# Import of a module operating on a database.
import mysql.connector
# Importing a module for creating APIs.
from flask import Flask, jsonify, request, send_file
# Import class for creating a path object.
from pathlib import Path
# Import of the validating module.
from re import match
# Import of a library that performs operations on the operating system.
import os
# Import of a function that loads environment variables into the module.
from dotenv import load_dotenv

# Loading environment variables.
load_dotenv()
# Creating an application object.
app = Flask(__name__)
# Assigning the folder path with users' media files with the application's UPLOAD_FOLDER key.
app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER")


@app.route("/media/upload/<user_id>", methods=["POST"])
def upload_media(user_id):
    """The function responsible for validating the uploaded graphic file, creating its path on the server,
    locating it in the path and adding the path to the database. Allowed methods: POST."""
    # Validation of the received graphic file. If the file does not meet any of the specified conditions,
    # the function will return status 400.
    if "file" not in request.files:
        return jsonify(result="Media not provided."), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify(result="No file selected."), 400
    if not (file and validation_file(file.filename)):
        return jsonify(result="Unsupported media type."), 400

    # If the file passes validation, the program will create a path to the directory where the file will be saved.
    filename = secure_filename(file.filename)
    path = os.path.join(os.getenv("UPLOAD_FOLDER"), user_id)

    # Checking whether a given directory is on the server, if not the program will create it.
    if not os.path.exists(path):
        os.mkdir(path)

    # Making empty connection, cursor and file_path, if connection or cursor won't be created then in finally
    # won't be error.
    connection = None
    cur = None
    file_path = None

    try:
        # Getting the main_photo_flag from the transferred parameter. If a given parameter is missing in the query or
        # its values are other than 1 or 0, the program will throw an error and return the status 400.
        main_photo_flag = int(request.args.get("main_photo_flag"))
        if not (main_photo_flag == 1 or main_photo_flag == 0):
            raise ValueError

        # Getting the announcement_id from the transferred parameter. Parameter validation.
        announcement_id = int(request.args.get("announcement_id"))
        if not announcement_id > 0:
            raise ValueError

        # Creating a file path to save.
        file_path = os.path.join(path, filename)
        # Creating a file path object to save.
        file_path_object = Path(file_path)
        # If a file with this name already exists, the program will create a new file path by adding another
        # digit at the end of the path.
        if file_path_object.exists():
            parent = str(file_path_object.parent)
            extension = "".join(file_path_object.suffixes)
            base = str(file_path_object.name).replace(extension, "")

            i = 2
            file_path = os.path.join(parent, f"{base}_{str(i)}{extension}")
            while Path(file_path).exists():
                i += 1
                file_path = os.path.join(parent, f"{base}_{str(i)}{extension}")

        # Saving the file to the server for the validated path.
        file.save(file_path)

        # Creating a connection to the database and a cursor.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)

        # Creation of request_data.
        request_data = {
            "announcement_id": announcement_id,
            "user_id": user_id,
            "path": file_path
        }

        # Checking whether the user wanted to add a photo to the table with the main photo, and creating
        # an appropriate query.
        if main_photo_flag:
            query = """INSERT INTO announcements_main_photo(user_id, announcement_id, path)
                       VALUES(%(user_id)s, %(announcement_id)s, %(path)s) """
        else:
            query = """INSERT INTO announcements_media(user_id, announcement_id, path)
                       VALUES(%(user_id)s, %(announcement_id)s, %(path)s) """

        # Execution of a query on the database and confirmation of changes.
        cur.execute(query, request_data)
        connection.commit()

    # If a file error occurs while saving the photo on the server, the program will return 500.
    except FileNotFoundError:
        return jsonify(result="Error during saving file, file or path doesn't exist."), 500

    # In case of an error while adding the path to the database, the program will delete the previously added photo on
    # the server and return the appropriate status.
    except mysql.connector.Error as message:
        if Path(file_path).exists():
            os.remove(file_path)
        # If the user wants to add a second profile picture, which is not allowed, it will return a 409 status.
        if "announcement_id_UNIQUE" in message.msg:
            return jsonify(result="Profile picture for announcement already exists."), 409

        # In any other case, the program will return 500.
        return jsonify(result=message.msg), 500

    # In case of an error during parameters validation, the program will check whether the file has been created and,
    # if necessary, delete it and return a json file with the appropriate message and status 400.
    except (KeyError, ValueError, TypeError):
        if Path(file_path).exists():
            os.remove(file_path)

        return jsonify(result="Bad parameters. Required parameters: "
                              "/?announcement_id=int:>0&main_photo_flag=int:1/0."), 400

    # If successfully added to the server and the path to the database is added, the program will return status 201.
    else:
        return jsonify(result="Media uploaded successfully."), 201

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()


@app.route("/media/download", methods=["GET"])
def download_media():
    """Function responsible for downloading a graphic file using the received path and returning it to the user.
    Allowed methods: GET."""
    # Trying to return a file from path, if successful, return the file with status 200.
    try:
        request_data = request.get_json()
        return send_file(request_data["path"], as_attachment=True), 200

    # If an incorrect path is provided, return status 404.
    except FileNotFoundError:
        return jsonify(result="File or path doesn't exist."), 404

    # If there is an error with the json being sent, return status 400.
    except (KeyError, ValueError, TypeError):
        return jsonify(result="Required json: {path:path}."), 400


@app.route("/announcements/<int:announcement_id>/media/paths", methods=["GET"])
def get_media_paths(announcement_id):
    """Function responsible for downloading paths to graphic files. The user must specify which advertisement he wants
    to download the paths to. Allowed methods: GET."""
    # Making empty connection and cursor, if connection or cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)

        # Getting the main_photo_flag from the transferred parameter. Parameter validation.
        main_photo_flag = int(request.args.get("main_photo_flag"))
        if not (main_photo_flag == 1 or main_photo_flag == 0):
            raise ValueError

        # If main_photo_flag is True, the operation will take place on the table with the main photos.
        if main_photo_flag:
            query = f"""SELECT announcements_main_photo.path FROM announcements_main_photo
                        WHERE announcements_main_photo.announcement_id={announcement_id} """

        # If main_photo_flag is False, the operation will take place on the table with photos.
        else:
            query = f"""SELECT announcements_media.path FROM announcements_media
                        WHERE announcements_media.announcement_id={announcement_id} """

        # Execute SELECT query.
        cur.execute(query)

    # If an error occurs during database operations, return status 500.
    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    # If an error occurs while validating the parameter, return status 400.
    except (KeyError, ValueError, TypeError):
        return jsonify(result="Bad parameter. Required parameter: /?main_photo_flag=int:1/0."), 400

    # If successful, return json with status 200.
    else:
        return jsonify(result=cur.fetchall()), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()


@app.route("/media/delete", methods=["DELETE"])
def delete_media():
    """Function responsible for deleting photos from the server and their paths from the database.
    Allowed methods: DELETE."""
    # Making empty connection and cursor, if connection or cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Getting the main_photo_flag from the transferred parameter. Parameter validation.
        main_photo_flag = int(request.args.get("main_photo_flag"))
        if not (main_photo_flag == 1 or main_photo_flag == 0):
            raise ValueError

        # Getting the path from the transferred parameter. Parameter validation.
        path = request.args.get("path")
        if not path:
            raise ValueError

        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        # Making request_data.
        request_data = {"path": path}

        # Depending on the flag, removing the path from the tables.
        if main_photo_flag:
            query = """DELETE FROM announcements_main_photo
                       WHERE announcements_main_photo.path=%(path)s"""

        else:
            query = """DELETE FROM announcements_media
                       WHERE announcements_media.path=%(path)s"""

        # Execute SELECT query.
        cur.execute(query, request_data)

        # Trying to delete a file from the server, if the file exists, it will delete itself and the changes will be
        # saved in the database.
        if os.path.exists(path):
            os.remove(path)
            connection.commit()
        # Otherwise, the program throws a 404 error.
        else:
            raise FileNotFoundError

    # If an error occurs during database operations, return status 500.
    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    # If an error occurs while validating the parameters, return status 400.
    except (KeyError, ValueError, TypeError):
        return jsonify(result="Bad parameters. Required parameters: /?main_photo_flag=int:1/0&path=str."), 400

    # If it does not find such a file on the server, return status 404.
    except FileNotFoundError:
        return jsonify(result="File doesn't exist."), 404

    # If successful, return json with status 200.
    else:
        return jsonify(result="successful deletion"), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()


@app.route("/media/switch/<int:user_id>", methods=["PUT"])
def switch_media(user_id):
    """Function responsible for replacing paths to photos in the database. Moves paths between the main_photo table and
    the media table. Allowed methods: PUT."""
    # Making empty connection and cursor, if connection or cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        # Creating request data from request body.
        request_data = request.get_json()
        request_data["user_id"] = user_id

        # If both keys are missing in request_data, throw an error.
        if not ("main_photo_path" in request_data or "media_photo_path" in request_data):
            raise ValueError

        # If there is no announcement_id key in request_data, throw an error.
        request_data["announcement_id"] = int(request_data["announcement_id"])

        # Getting the to_media_flag from the transferred parameter. Parameter validation.
        to_media_flag = int(request.args.get("to_media_flag"))
        if not (to_media_flag == 1 or to_media_flag == 0):
            raise ValueError

        # Getting the to_main_flag from the transferred parameter. Parameter validation.
        to_main_flag = int(request.args.get("to_main_flag"))
        if not (to_main_flag == 1 or to_main_flag == 0):
            raise ValueError

        # If the imported to_media_flag parameter was true, the program will remove the path from the
        # announcements_main_photo table and place it in the announcements_media table.
        if to_media_flag:
            query_delete_main = """DELETE FROM announcements_main_photo
                                    WHERE announcements_main_photo.path=%(main_photo_path)s"""
            cur.execute(query_delete_main, request_data)
            query_add_media = """INSERT INTO announcements_media(user_id, announcement_id, path)
                                 VALUES(%(user_id)s, %(announcement_id)s, %(main_photo_path)s)"""
            cur.execute(query_add_media, request_data)

        # If the imported to_main_flag parameter was true, the program will remove the path from the announcements_media
        # table and place it in the announcements_main_photo table.
        if to_main_flag:
            query_delete_media = """DELETE FROM announcements_media
                                    WHERE announcements_media.path=%(media_photo_path)s"""
            cur.execute(query_delete_media, request_data)
            query_add_main = """INSERT INTO announcements_main_photo(user_id, announcement_id, path)
                                VALUES(%(user_id)s, %(announcement_id)s, %(media_photo_path)s)"""
            cur.execute(query_add_main, request_data)

        # Saving the changes made.
        connection.commit()

    # If an error occurs during database operations, return status 500.
    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    # If an error occurs while validating the parameters or request_data, return status 400.
    except (KeyError, ValueError, TypeError):
        return jsonify(result="Bad parameters. Required parameters: /?to_main_flag=int:1/0&to_media_flag=int:1/0."), 400

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
def varify_login():
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


@app.route("/announcements/<int:announcement_id>/complete", methods=["PATCH"])
def complete_the_announcement(announcement_id):
    """Function responsible for terminating active user advertisements. Allowed methods: PATCH."""
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

        return jsonify(result=user_favorite_announcements), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()


@app.route("/users/<int:user_id>/favorite-announcements", methods=["POST"])
def add_announcement_to_favorite(user_id):
    """Function responsible for adding advertisements to favorites by the user. Allowed methods: POST."""
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
    Allowed methods: DELETE"""
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
