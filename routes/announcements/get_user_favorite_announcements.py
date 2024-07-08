from flask import request, jsonify
from utils.database_connection import database_connect
import mysql.connector
from utils.formating import convert_image_to_base64


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
