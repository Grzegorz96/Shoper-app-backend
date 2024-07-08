from flask import Blueprint
from .get_announcements import get_announcements
from .update_announcement import update_announcement
from .complete_announcement import complete_announcement
from .restore_announcement import restore_announcement
from .delete_announcement import delete_announcement
from .add_announcement import add_announcement
from .get_user_announcements import get_user_announcements
from .get_user_favorite_announcements import get_user_favorite_announcements
from .add_announcement_to_favorites import add_announcement_to_favorites
from .delete_announcement_from_favorites import delete_announcement_from_favorites


announcements_bp = Blueprint("announcements_bp", __name__)

announcements_bp.add_url_rule("/announcements/search", view_func=get_announcements, methods=["GET"])
announcements_bp.add_url_rule("/announcements/<int:announcement_id>", view_func=update_announcement, methods=["PUT"])
announcements_bp.add_url_rule("/announcements/<int:announcement_id>/complete", view_func=complete_announcement,
                              methods=["PATCH"])
announcements_bp.add_url_rule("/announcements/<int:announcement_id>/restore", view_func=restore_announcement,
                              methods=["PATCH"])
announcements_bp.add_url_rule("/announcements/<int:announcement_id>/delete", view_func=delete_announcement,
                              methods=["PATCH"])
announcements_bp.add_url_rule("/announcements/users/<int:user_id>", view_func=add_announcement, methods=["POST"])
announcements_bp.add_url_rule("/announcements/users/<int:user_id>", view_func=get_user_announcements, methods=["GET"])
announcements_bp.add_url_rule("/favorite-announcements/users/<int:user_id>", view_func=get_user_favorite_announcements,
                              methods=["GET"])
announcements_bp.add_url_rule("/favorite-announcements/users/<int:user_id>", view_func=add_announcement_to_favorites,
                              methods=["POST"])
announcements_bp.add_url_rule("/favorite-announcements/<int:favorite_announcement_id>",
                              view_func=delete_announcement_from_favorites, methods=["DELETE"])
