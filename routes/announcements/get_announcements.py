from flask import request, jsonify
from utils.helpers import create_query_for_search_engine
from utils.formating import convert_image_to_base64
from utils.database_connection import database_connect
import mysql.connector


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
