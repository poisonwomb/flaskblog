from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config["SECRET_KEY"] = "f0d348adab26c88b0ceb3ad008c478f2"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

"""To make sure the database file is created, you may need to run
the following commands in the python REPL:

from flaskblog import app, db
app.app_context().push()
db.create_all()

Then the .db file is created in a folder called "Instance" in your project. 
"""
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
# Initialising flask_login
login_manager = LoginManager(app)
login_manager.init_app(app)
# Setting the name of the login function/route as the login view.
login_manager.login_view = "login"
# Setting login status messages to use the Bootstrap 'info' category for styling.
login_manager.login_message_category = "info"

# Routes need to be imported after app is created as routes require app.
from flaskblog import routes  # noqa: E402, F401
