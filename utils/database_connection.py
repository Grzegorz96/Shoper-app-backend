# Modules import.
import mysql.connector
import os


def database_connect():
    """Function responsible for connecting to the database using data from environment variables."""
    connection = mysql.connector.connect(host=os.getenv("DATABASE_HOST"), user=os.getenv("DATABASE_USER"),
                                         password=os.getenv("DATABASE_PASSWORD"),
                                         database=os.getenv("DATABASE_DATABASE"))

    # Returning connection.
    return connection
