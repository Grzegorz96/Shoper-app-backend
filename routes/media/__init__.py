from flask import Blueprint
from .upload_media import upload_media
from .delete_media import delete_media
from .switch_media import switch_media
from .download_media import download_media

media_bp = Blueprint("media_bp", __name__)

media_bp.add_url_rule("/upload/users/<int:user_id>", view_func=upload_media, methods=["POST"])
media_bp.add_url_rule("/delete/users/<int:user_id>", view_func=delete_media, methods=["DELETE"])
media_bp.add_url_rule("/switch/users/<int:user_id>", view_func=switch_media, methods=["PUT"])
media_bp.add_url_rule("/download/announcements/<int:announcement_id>", view_func=download_media, methods=["GET"])
