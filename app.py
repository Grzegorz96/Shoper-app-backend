from flask import Flask
from dotenv import load_dotenv
from utils.config import Config
from utils.register_blueprints import register_blueprints

# Loading environment variables.
load_dotenv()

# Creating an application object.
app = Flask(__name__)
# Configuring the application object.
app.config.from_object(Config)
# Registering the announcements_bp blueprint.
register_blueprints(app)

# Running the application on the server.
if __name__ == "__main__":
    app.run(debug=True, port=5000)
