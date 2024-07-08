from flask import Blueprint
from .get_messages import get_messages
from .send_message import send_message
from .get_conversations import get_conversations

messages_bp = Blueprint("messages_bp", __name__)

messages_bp.add_url_rule("/messages/users/<int:user_id>", view_func=get_messages, methods=["GET"])
messages_bp.add_url_rule("/messages/users/<int:user_id>", view_func=send_message, methods=["POST"])
messages_bp.add_url_rule("/conversations/users/<int:user_id>", view_func=get_conversations, methods=["GET"])
