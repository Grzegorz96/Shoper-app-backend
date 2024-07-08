from flask import Flask
from routes.announcements import announcements_bp
from routes.users import users_bp
from routes.media import media_bp
from routes.messages import messages_bp


def register_blueprints(app: Flask):
    app.register_blueprint(announcements_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(media_bp, url_prefix="/media")
