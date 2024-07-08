import os


class Config:
    # Assigning the folder path with users' media files with the application's UPLOAD_FOLDER key.
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")
    # Setting the maximum size of files uploaded to the server.
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024  # 3 MB
    # Setting the maximum size of a single file in a ZIP archive.
    MAX_FILE_LENGTH = 200 * 1024  # 200 KB
