from flask import Blueprint
from .login_user import login_user
from .verify_login import verify_login
from .update_user import update_user
from .delete_user import delete_user
from .register_user import register_user

users_bp = Blueprint("users_bp", __name__)

users_bp.add_url_rule("/login", view_func=login_user, methods=["GET"])
users_bp.add_url_rule("/login-verification", view_func=verify_login, methods=["GET"])
users_bp.add_url_rule("/<int:user_id>", view_func=update_user, methods=["PATCH"])
users_bp.add_url_rule("/<int:user_id>", view_func=delete_user, methods=["DELETE"])
users_bp.add_url_rule("/register", view_func=register_user, methods=["POST"])
