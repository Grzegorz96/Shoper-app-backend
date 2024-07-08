import base64


def convert_image_to_base64(image_path):
    """Convert an image to a base64 encoded string."""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
    except (FileNotFoundError, IOError, PermissionError, OSError):
        return None
