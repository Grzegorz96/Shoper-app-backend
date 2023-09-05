from Database_connection import database_connect
from Query_creator import create_query_for_search_engine, create_query_for_getting_messages
from Media_validator import validation_file
from werkzeug.utils import secure_filename
import mysql.connector
from flask import Flask, jsonify, request, send_file
from pathlib import Path
from re import match
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER")


@app.route("/media/upload/<user_id>", methods=["POST"])
def upload_media(user_id):
    if "file" not in request.files:
        return jsonify(result="Media not provided."), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify(result="No file selected."), 400
    if not (file and validation_file(file.filename)):
        return jsonify(result="Unsupported media type."), 400

    filename = secure_filename(file.filename)
    path = os.path.join(os.getenv("UPLOAD_FOLDER"), user_id)

    if not os.path.exists(path):
        os.mkdir(path)

    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None
    file_path = None

    try:
        main_photo_flag = int(request.args.get("main_photo_flag"))
        if not (main_photo_flag == 1 or main_photo_flag == 0):
            raise ValueError

        announcement_id = int(request.args.get("announcement_id"))
        if not announcement_id > 0:
            raise ValueError

        file_path = os.path.join(path, filename)
        file_path_object = Path(file_path)
        if file_path_object.exists():
            parent = str(file_path_object.parent)
            extension = "".join(file_path_object.suffixes)
            base = str(file_path_object.name).replace(extension, "")

            i = 2
            file_path = os.path.join(parent, f"{base}_{str(i)}{extension}")
            while Path(file_path).exists():
                i += 1
                file_path = os.path.join(parent, f"{base}_{str(i)}{extension}")

        file.save(file_path)

        connection = database_connect()
        cur = connection.cursor(dictionary=True)

        request_data = {
            "announcement_id": announcement_id,
            "user_id": user_id,
            "path": file_path
        }

        if main_photo_flag:
            query = """INSERT INTO announcements_main_photo(user_id, announcement_id, path)
                       VALUES(%(user_id)s, %(announcement_id)s, %(path)s) """
        else:
            query = """INSERT INTO announcements_media(user_id, announcement_id, path)
                       VALUES(%(user_id)s, %(announcement_id)s, %(path)s) """

        cur.execute(query, request_data)
        connection.commit()

    except FileNotFoundError:
        return jsonify(result="Error during saving file, file or path doesn't exist."), 500

    except mysql.connector.Error as message:
        if Path(file_path).exists():
            os.remove(file_path)
        if "announcement_id_UNIQUE" in message.msg:
            return jsonify(result="Profile picture for announcement already exists."), 409

        return jsonify(result=message.msg), 500

    except (KeyError, ValueError, TypeError):
        if Path(file_path).exists():
            os.remove(file_path)

        return jsonify(result="Bad parameters. Required parameters: "
                              "/?announcement_id=int:>0&main_photo_flag=int:1/0."), 400

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
    try:
        request_data = request.get_json()
        # return send_from_directory(app.config["UPLOAD_FOLDER"], "asdf.png", as_attachment=True)
        return send_file(request_data["path"], as_attachment=True), 200

    except FileNotFoundError:
        return jsonify(result="File or path doesn't exist."), 400

    except (KeyError, ValueError, TypeError):
        return jsonify(result="Required json: {path:path}."), 400


@app.route("/announcements/<int:announcement_id>/media/paths", methods=["GET"])
def get_media_paths(announcement_id):
    connection = None
    cur = None

    # Trying to perform a database operation.
    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        main_photo_flag = int(request.args.get("main_photo_flag"))
        if not (main_photo_flag == 1 or main_photo_flag == 0):
            raise ValueError

        if main_photo_flag:
            query = f"""SELECT announcements_main_photo.path FROM announcements_main_photo
                        WHERE announcements_main_photo.announcement_id={announcement_id} """

        else:
            query = f"""SELECT announcements_media.path FROM announcements_media
                        WHERE announcements_media.announcement_id={announcement_id} """

        # Execute SELECT query.
        cur.execute(query)

    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    except (KeyError, ValueError, TypeError):

        return jsonify(result="Bad parameter. Required parameter: /?main_photo_flag=int:1/0."), 400

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
    connection = None
    cur = None
    try:
        main_photo_flag = int(request.args.get("main_photo_flag"))
        if not (main_photo_flag == 1 or main_photo_flag == 0):
            raise ValueError

        path = request.args.get("path")

        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        request_data = {"path": path}

        if main_photo_flag:
            query = """DELETE FROM announcements_main_photo
                       WHERE announcements_main_photo.path=%(path)s"""

        else:
            query = """DELETE FROM announcements_media
                       WHERE announcements_media.path=%(path)s"""

        # Execute SELECT query.
        cur.execute(query, request_data)

        if os.path.exists(path):
            os.remove(path)
            connection.commit()
        else:
            raise FileNotFoundError

    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    except (KeyError, ValueError, TypeError):

        return jsonify(result="Bad parameter. Required parameter: /?main_photo_flag=int:1/0."), 400

    except FileNotFoundError:
        return jsonify(result="File doesn't exist."), 404

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
    connection = None
    cur = None
    # Trying to perform a database operation.
    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        # Creating request data from request body.
        request_data = request.get_json()
        request_data["user_id"] = user_id

        to_media_flag = int(request.args.get("to_media_flag"))
        if not (to_media_flag == 1 or to_media_flag == 0):
            raise ValueError

        to_main_flag = int(request.args.get("to_main_flag"))
        if not (to_main_flag == 1 or to_main_flag == 0):
            raise ValueError

        if to_media_flag:
            query_delete_main = """DELETE FROM announcements_main_photo
                                    WHERE announcements_main_photo.path=%(main_photo_path)s"""
            cur.execute(query_delete_main, request_data)
            query_add_media = """INSERT INTO announcements_media(user_id, announcement_id, path)
                                 VALUES(%(user_id)s, %(announcement_id)s, %(main_photo_path)s)"""
            cur.execute(query_add_media, request_data)

        if to_main_flag:
            query_delete_media = """DELETE FROM announcements_media
                                    WHERE announcements_media.path=%(media_photo_path)s"""
            cur.execute(query_delete_media, request_data)
            query_add_main = """INSERT INTO announcements_main_photo(user_id, announcement_id, path)
                                VALUES(%(user_id)s, %(announcement_id)s, %(media_photo_path)s)"""
            cur.execute(query_add_main, request_data)

        connection.commit()

    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    except (KeyError, ValueError, TypeError):

        return jsonify(result="Bad parameters. Required parameters: /?to_main_flag=int:1/0&to_media_flag=int:1/0."), 400

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
    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    # Trying to perform a database operation.
    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        # Creating request data from request body.
        request_data = request.get_json()

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
        connection.commit()

    # Return details of error with 500 status code.
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

    except (ValueError, TypeError, KeyError):
        return jsonify(result="invalid input data."), 400
    # If it succeeds, returning 201 status code.
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
    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        # Creating empty request_data.
        request_data = request.get_json()

        # Making query.
        query = """SELECT user_id, first_name, last_name, email, login, password, date_of_birth, street, 
                   zip_code, city, creation_account_date FROM users WHERE 
                   ((login=%(login_or_email)s AND password=%(password)s) OR (email=%(login_or_email)s 
                   AND password=%(password)s)) AND users.active_flag=True"""

        # Executing query.
        cur.execute(query, request_data)

        # # Return details of error with 500 status code.
    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

        # When everything ok, returning 200 status with selected info about user in response body.
    else:
        user_info = cur.fetchall()
        if user_info:
            for user in user_info:
                user["creation_account_date"] = str(user["creation_account_date"])
            return jsonify(result=user_info[0]), 200
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
        connection.commit()

    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    except (ValueError, TypeError, KeyError):
        return jsonify(result="invalid input data."), 400

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
    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        # Creating request_data.
        active_flag = int(request.args.get("active_flag"))
        if not (active_flag == 0 or active_flag == 1):
            raise ValueError
        per_page = int(request.args.get("per_page"))
        if not per_page > 0:
            raise ValueError
        page = int(request.args.get("page"))
        if not page > 0:
            raise ValueError

        offset = (page * per_page) - per_page

        request_data = {
            "user_id": user_id,
            "per_page": per_page,
            "offset": offset
        }

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

    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    except (KeyError, ValueError, TypeError):

        return jsonify(result="Bad parameters. Required parameters: "
                              "/?page=in:>0&per_page=int:>0&active_flag=int:1/0."), 400

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
        connection.commit()

    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    except (ValueError, TypeError, KeyError):
        return jsonify(result="invalid input data."), 400

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
    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        # Creating request_data.
        request_data = request.get_json()
        # Making query.
        query = """SELECT user_id FROM users WHERE login=%(login)s """

        # Executing query.
        cur.execute(query, request_data)

    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    else:
        user_id = cur.fetchall()
        if user_id:
            return jsonify(result="The given login is already taken."), 400

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
        connection.commit()

    except mysql.connector.Error as message:

        if "email_UNIQUE" in message.msg:
            return jsonify(email_error="The user with the given e-mail address is already registered."), 400

        else:
            return jsonify(result=message.msg), 500

    except (ValueError, TypeError, KeyError):
        return jsonify(result="invalid input data."), 400

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
        connection.commit()

    except mysql.connector.Error as message:

        return jsonify(result=message.msg), 500

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
        connection.commit()

    except mysql.connector.Error as message:

        return jsonify(result=message.msg), 500

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
        connection.commit()

    except mysql.connector.Error as message:

        return jsonify(result=message.msg), 500

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
    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        # Creating request_data.
        active_flag = int(request.args.get("active_flag"))
        if not (active_flag == 0 or active_flag == 1):
            raise ValueError
        per_page = int(request.args.get("per_page"))
        if not per_page > 0:
            raise ValueError
        page = int(request.args.get("page"))
        if not page > 0:
            raise ValueError

        offset = (page * per_page) - per_page

        request_data = {
            "user_id": user_id,
            "per_page": per_page,
            "offset": offset
        }

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

    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    except (KeyError, ValueError, TypeError):

        return jsonify(result="Bad parameters. Required parameters: "
                              "/?page=int:>0&per_page=int:>0&active_flag=int:1/0."), 400

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
        # Making query.
        query_check = """ SELECT favorite_announcement_id FROM favorite_announcements
                          WHERE user_id=%(user_id)s AND announcement_id=%(announcement_id)s """
        # Executing query.
        cur.execute(query_check, request_data)

        is_already_liked = cur.fetchall()
        if not is_already_liked:
            query = """ INSERT INTO favorite_announcements(user_id, announcement_id)
                        VALUES(%(user_id)s, %(announcement_id)s) """
            cur.execute(query, request_data)
            connection.commit()

        else:
            raise ReferenceError

    except mysql.connector.Error as message:

        return jsonify(result=message.msg), 500

    except ReferenceError:
        return jsonify(result="The announcement is already liked"), 400

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
        connection.commit()

    except mysql.connector.Error as message:

        return jsonify(result=message.msg), 500

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

        per_page = int(request.args.get("per_page"))
        if not per_page > 0:
            raise ValueError
        page = int(request.args.get("page"))
        if not page > 0:
            raise ValueError

        offset = (page * per_page) - per_page

        content_to_search = request.args.get("q")
        location = request.args.get("l")
        category = request.args.get("c")

        if content_to_search:
            # Init query for search field
            query = create_query_for_search_engine(content_to_search, query, "announcements.title")
        if location:
            # Init query for location field
            query = create_query_for_search_engine(location, query, "announcements.location")
        # Init query for category id
        if category:
            query += f"""AND categories.category_id={category} """

        query += f"""ORDER BY announcements.announcement_id DESC
                     LIMIT {per_page} OFFSET {offset}"""

        # Executing query.
        cur.execute(query)

    except mysql.connector.Error as message:

        return jsonify(result=message.msg), 500

    except (KeyError, ValueError, TypeError):

        return jsonify(result="Bad parameters. Required parameters: /?page=int:>0&per_page=int:>0."
                              " Optional parameters: /?q=str&l=str&c=int:1/12."), 400

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


#  announcement_id/ conversation_id
@app.route("/users/<int:user_id>/messages", methods=["GET"])
def get_messages(user_id):
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        request_data = request.get_json()
        request_data["user_id"] = user_id

        if "conversation_id" in request_data:
            messages = create_query_for_getting_messages(cur, request_data)

        else:
            # Making query.
            query_check = """SELECT conversation_id FROM conversations
                             WHERE conversations.announcement_id=%(announcement_id)s
                             AND conversations.user_id=%(user_id)s """
            cur.execute(query_check, request_data)
            conversation_id = cur.fetchall()
            if conversation_id:
                request_data["conversation_id"] = conversation_id[0]["conversation_id"]
                messages = create_query_for_getting_messages(cur, request_data)

            else:
                messages = []

    except mysql.connector.Error as message:

        return jsonify(result=message.msg), 500

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
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        request_data = request.get_json()
        request_data["user_id"] = user_id

        if "conversation_id" in request_data:
            query = """INSERT INTO messages(conversation_id, user_id, customer_flag, content, date)
                       VALUES(%(conversation_id)s, %(user_id)s, %(customer_flag)s, %(content)s, now())"""

            cur.execute(query, request_data)
            connection.commit()

        else:
            query_make_conv = """INSERT INTO conversations(announcement_id, user_id)
                                 VALUES(%(announcement_id)s, %(user_id)s) """
            cur.execute(query_make_conv, request_data)

            query_check_conv_id = """SELECT conversation_id FROM conversations
                                     WHERE conversations.announcement_id=%(announcement_id)s
                                     AND conversations.user_id=%(user_id)s """
            cur.execute(query_check_conv_id, request_data)
            request_data["conversation_id"] = cur.fetchall()[0]["conversation_id"]

            query_add_message = """INSERT INTO messages(conversation_id, user_id, customer_flag, content, date)
                                   VALUES(%(conversation_id)s, %(user_id)s, %(customer_flag)s, %(content)s, now())"""
            cur.execute(query_add_message, request_data)
            connection.commit()

    except mysql.connector.Error as message:

        return jsonify(result=message.msg), 500

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
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)

        customer_flag = int(request.args.get("customer_flag"))
        if not (customer_flag == 0 or customer_flag == 1):
            raise ValueError
        per_page = int(request.args.get("per_page"))
        if not per_page > 0:
            raise ValueError
        page = int(request.args.get("page"))
        if not page > 0:
            raise ValueError

        offset = (page * per_page) - per_page

        request_data = {
            "user_id": user_id,
            "per_page": per_page,
            "offset": offset
        }

        if customer_flag:
            on_field = "announcements.seller_id"
            where_field = "conversations.user_id"
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

    except mysql.connector.Error as message:

        return jsonify(result=message.msg), 500

    except (KeyError, ValueError, TypeError):

        return jsonify(result="Bad parameters. Required parameters:"
                              " /?page=int:>0&per_page=int:>0&customer_flag=int:1/0."), 400

    else:
        return jsonify(result=cur.fetchall()), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
