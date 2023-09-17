import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
# Initialising flask_login
login_manager = LoginManager(app)
login_manager.init_app(app)
# Setting the name of the login function/route as the login view.
login_manager.login_view = "login"
# Setting login status messages to use the Bootstrap 'info' category for styling.
login_manager.login_message_category = "info"

# Setting up email credentials.
app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER")
app.config["MAIL_PORT"] = os.environ.get("MAIL_PORT")
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")

mail = Mail(app)

# Routes need to be imported after app is created as routes require app.
from flaskblog import routes  # noqa: E402, F401
