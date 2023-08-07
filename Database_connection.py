# Modules import.
import mysql.connector
import os
from dotenv import load_dotenv
# Load environment variables.
load_dotenv()


# Database connect function.
def database_connect():
    # Creating connection with database. Values are imported from environment variables.
    connection = mysql.connector.connect(host=os.getenv("DATABASE_HOST"), user=os.getenv("DATABASE_USER"),
                                         password=os.getenv("DATABASE_PASSWORD"),
                                         database=os.getenv("DATABASE_DATABASE"))

    # Returning connection.
    return connection
