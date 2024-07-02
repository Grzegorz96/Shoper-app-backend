import base64
import os
from dotenv import load_dotenv
# Load environment variables.
load_dotenv()


def convert_image_to_base64(image_path):
    """Convert an image to a base64 encoded string."""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
    except (FileNotFoundError, IOError, PermissionError, OSError):
        return None
    

def validation_file_extension(filename):
    """Function responsible for validating the uploaded graphic file. Validates its extension taking into account
    allowed extensions from the environment variable."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in os.getenv("ALLOWED_EXTENSIONS").split(",")


def create_query_for_search_engine(field, query, column):
    """Function responsible for dynamically creating a query to the database when downloading announcements with
    additional parameters."""
    # Defining an empty list.
    collection = []
    # Create a word list and remove blank space objects from it.
    for element in field.split(" "):
        if element != "":
            collection.append(element)

    # Iterating through the length of the created list, creating a string and adding it to the query.
    for i in range(len(collection)):
        if len(collection) == 1:
            query += f"""AND {column} LIKE "%{collection[i]}%" """
        else:
            if i == 0:
                query += f"""AND ({column} LIKE "%{collection[i]}%" """
            elif i < (len(collection) - 1):
                query += f"""OR {column} LIKE "%{collection[i]}%" """
            else:
                query += f"""OR {column} LIKE "%{collection[i]}%") """

    # Returning the overwritten query.
    return query


def create_query_for_getting_messages(cur, request_data):
    """Function responsible for creating a query about downloading messages for a conversation and converting
    the DATETIME object to a string."""
    # Making query.
    query = """SELECT messages.conversation_id, messages.message_id,
               messages.customer_flag, messages.content, messages.date as post_date,
               messages.user_id, users.first_name
               FROM messages
               JOIN users ON messages.user_id=users.user_id
               WHERE messages.conversation_id=%(conversation_id)s
               ORDER BY messages.message_id DESC"""

    # Executing query.
    cur.execute(query, request_data)

    # Downloading the list of message dictionaries into a variable and converting DATETIME objects to a strings.
    messages = cur.fetchall()
    for message in messages:
        message["post_date"] = str(message["post_date"])

    # Returning list of messages.
    return messages
