from flask import request, jsonify
from utils.database_connection import database_connect
import mysql.connector


def add_announcement_to_favorites(user_id):
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
