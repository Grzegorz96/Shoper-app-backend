from Database_connection import database_connect
from Query_creator import create_query_for_search_engine, create_query_for_getting_messages
import mysql.connector
from flask import Flask, jsonify, request

app = Flask(__name__)


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
        # Making query.
        query = """INSERT INTO users(first_name, last_name, email, login, password, 
                   date_of_birth, street, zip_code, city, active_flag)
                   VALUES(%(first_name)s, %(last_name)s, %(email)s, %(login)s, %(password)s, %(date_of_birth)s, 
                   %(street)s, %(zip_code)s, %(city)s, True)"""
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
                   zip_code, city FROM users WHERE 
                   ((login=%(login_or_email)s AND password=%(password)s) OR (email=%(login_or_email)s 
                   AND password=%(password)s)) AND users.active_flag=True"""

        # Executing query.
        cur.execute(query, request_data)

        # Return details of error with 500 status code.
    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

        # When everything ok, returning 200 status with selected info about user in response body.
    else:
        user_info = cur.fetchall()
        if user_info:
            return jsonify(result=user_info[0]), 200
        else:
            return jsonify(result="The user does not exist in the database."), 400

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()


@app.route("/announcements/<announcement_id>", methods=["PUT"])
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
        # Making query.
        query = """UPDATE announcements 
                   SET announcements.title=%(title)s, announcements.description=%(description)s,
                   announcements.price=%(price)s, announcements.location=%(location)s
                   WHERE announcements.announcement_id=%(announcement_id)s """

        # Executing query.
        cur.execute(query, request_data)
        connection.commit()

    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    else:
        return jsonify(result="Announcement successfully updated."), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()


@app.route("/users/<user_id>/announcements", methods=["GET"])
def get_user_announcements(user_id):
    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        # Creating request_data.
        request_data = {"user_id": user_id}
        # Making query.
        query = """SELECT announcements.announcement_id, users.first_name, 
                   announcements.seller_id, categories.name_category,  
                   announcements.category_id, announcements.title,
                   announcements.description, announcements.price, announcements.location,
                   announcements.active_flag
                   FROM announcements 
                   JOIN categories ON announcements.category_id=categories.category_id
                   JOIN users ON announcements.seller_id=users.user_id
                   WHERE announcements.seller_id=%(user_id)s 
                   AND (announcements.active_flag=True OR announcements.completed_flag=True)
                   ORDER BY announcements.announcement_id DESC
                   LIMIT 16"""

        # Executing query.
        cur.execute(query, request_data)

    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    else:
        return jsonify(result=cur.fetchall()), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()


@app.route("/users/<user_id>/announcements", methods=["POST"])
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

        # Making query.
        query = """INSERT INTO announcements(seller_id, category_id, title, description, price,
                   location, active_flag, completed_flag, deleted_flag)
                   VALUES(%(user_id)s, %(category_id)s, %(title)s,
                   %(description)s, %(price)s, %(location)s, True, False, False)"""

        # Executing query.
        cur.execute(query, request_data)
        connection.commit()

    except mysql.connector.Error as message:
        return jsonify(result=message.msg), 500

    else:
        return jsonify(result="Announcement added successfully."), 201

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


@app.route("/users/<user_id>", methods=["PATCH"])
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

    else:
        return jsonify(result="User successfully updated."), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()


@app.route("/announcements/<announcement_id>/complete", methods=["PATCH"])
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
                   WHERE announcements.announcement_id=%(announcement_id)s """

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


@app.route("/announcements/<announcement_id>/restore", methods=["PATCH"])
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
                   WHERE announcements.announcement_id=%(announcement_id)s """

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


@app.route("/announcements/<announcement_id>/delete", methods=["PATCH"])
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
                   WHERE announcements.announcement_id=%(announcement_id)s """

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


@app.route("/announcements", methods=["GET"])
def get_all_announcements():
    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        # Making query.
        query = """ SELECT announcements.announcement_id, users.first_name,
                    announcements.seller_id, categories.name_category, 
                    announcements.title, announcements.description, 
                    announcements.price, announcements.location
                    FROM announcements 
                    JOIN categories ON announcements.category_id=categories.category_id
                    JOIN users ON announcements.seller_id=users.user_id
                    WHERE announcements.active_flag=True
                    ORDER BY announcements.announcement_id DESC """

        # Executing query.
        cur.execute(query)

    except mysql.connector.Error as message:

        return jsonify(result=message.msg), 500

    else:
        return jsonify(result=cur.fetchall()), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()


@app.route("/users/<user_id>/favorite-announcements", methods=["GET"])
def get_user_favorite_announcements(user_id):
    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        # Creating request_data.
        request_data = {"user_id": user_id}
        # Making query.
        query = f"""SELECT favorite_announcements.favorite_announcement_id, announcements.announcement_id,
                    users.first_name, announcements.seller_id, announcements.title,   
                    announcements.description, categories.name_category, announcements.price,
                    announcements.location, announcements.active_flag
                    FROM favorite_announcements 
                    JOIN announcements ON favorite_announcements.announcement_id=announcements.announcement_id
                    JOIN categories ON announcements.category_id=categories.category_id
                    JOIN users ON announcements.seller_id=users.user_id
                    WHERE favorite_announcements.user_id=%(user_id)s 
                    AND (announcements.active_flag=1 OR announcements.completed_flag=1)
                    ORDER BY favorite_announcements.favorite_announcement_id DESC"""

        # Executing query.
        cur.execute(query, request_data)

    except mysql.connector.Error as message:

        return jsonify(result=message.msg), 500

    else:
        return jsonify(result=cur.fetchall()), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()


@app.route("/users/<user_id>/favorite-announcements", methods=["POST"])
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


@app.route("/favorite-announcements/<favorite_announcement_id>", methods=["DELETE"])
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
def get_announcements_by_search_engine():
    categories = ["Elektronika", "Do domu", "Do ogrodu", "Sport i turystyka", "Motoryzacja", "Zdrowie i uroda",
                  "Dla dzieci", "Rolnictwo", "Nieruchomości", "Moda", "Kultura i rozrywka", "Oddam za darmo"]
    # Making empty connection and cursor, if connection and cursor won't be created then in finally won't be error.
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        content_to_search = request.args.get("q")
        location = request.args.get("l")
        category = request.args.get("c")
        # Making query.
        query = """ SELECT announcements.announcement_id, users.first_name,
                    announcements.seller_id, categories.name_category,
                    announcements.title, announcements.description, 
                    announcements.price, announcements.location
                    FROM announcements 
                    JOIN categories ON announcements.category_id=categories.category_id
                    JOIN users ON announcements.seller_id=users.user_id
                    WHERE announcements.active_flag=True """

        if content_to_search is not None:
            # Init query for search field
            query = create_query_for_search_engine(content_to_search, query, "announcements.title")
        if location is not None:
            # Init query for location field
            query = create_query_for_search_engine(location, query, "announcements.location")
        # Init query for category id
        if category in categories:
            category_id = categories.index(category) + 1
            query += f"""AND categories.category_id={category_id} """

        query += "ORDER BY announcements.announcement_id DESC"
        # Executing query.
        cur.execute(query)

    except mysql.connector.Error as message:

        return jsonify(result=message.msg), 500

    else:
        return jsonify(result=cur.fetchall()), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()


#  announcement_id/ conversation_id
@app.route("/users/<user_id>/messages", methods=["GET"])
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


@app.route("/users/<user_id>/messages", methods=["POST"])
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
                       VALUES(%(conversation_id)s, %(user_id)s, %(is_user_customer)s, %(content)s, now())"""

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
                                   VALUES(%(conversation_id)s, %(user_id)s, True, %(content)s, now())"""
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


@app.route("/users/<user_id>/conversations", methods=["GET"])
def get_conversations(user_id):
    connection = None
    cur = None

    try:
        # Making connection and cursor as dictionary.
        connection = database_connect()
        cur = connection.cursor(dictionary=True)
        request_data = {"user_id": user_id}
        # Making query.
        query_get_conversations_as_customer = """SELECT conversations.conversation_id, 
                                                 conversations.announcement_id, announcements.title,
                                                 users.first_name FROM conversations 
                                                 JOIN announcements ON conversations.announcement_id=
                                                 announcements.announcement_id
                                                 JOIN users ON announcements.seller_id=users.user_id
                                                 WHERE conversations.user_id=%(user_id)s """

        # Executing query.
        cur.execute(query_get_conversations_as_customer, request_data)
        conversations_as_customer = cur.fetchall()

        query_get_conversations_as_seller = """SELECT conversations.conversation_id, 
                                               conversations.announcement_id, announcements.title,
                                               users.first_name FROM conversations
                                               JOIN announcements ON conversations.announcement_id=
                                               announcements.announcement_id
                                               JOIN users ON conversations.user_id=users.user_id
                                               WHERE announcements.seller_id=%(user_id)s """

        # Executing query.
        cur.execute(query_get_conversations_as_seller, request_data)
        conversations_as_seller = cur.fetchall()

    except mysql.connector.Error as message:

        return jsonify(result=message.msg), 500

    else:
        return jsonify(as_customer=conversations_as_customer, as_seller=conversations_as_seller), 200

    # Closing connection with database and cursor if it exists.
    finally:
        if connection:
            connection.close()
            if cur:
                cur.close()


if __name__ == "__main__":
    app.run(debug=True, port=5000)