# Modules import.
import os
from dotenv import load_dotenv
# Load environment variables.
load_dotenv()


def validation_file(filename):
    """Function responsible for validating the uploaded graphic file. Validates its extension taking into account
    allowed extensions from the environment variable."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in os.getenv("ALLOWED_EXTENSIONS").split(",")
