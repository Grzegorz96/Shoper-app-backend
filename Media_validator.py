import os
from dotenv import load_dotenv
# Load environment variables.
load_dotenv()


def validation_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in os.getenv("ALLOWED_EXTENSIONS").split(",")
