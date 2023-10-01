from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

from flaskblog.config import Config


db = SQLAlchemy()
bcrypt = Bcrypt()
# Initialising flask_login
login_manager = LoginManager()
# Setting the name of the login function/route as the login view.
login_manager.login_view = "users.login"
# Setting login status messages to use the Bootstrap 'info' category for styling.
login_manager.login_message_category = "info"
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    # Importing blueprints
    from flaskblog.main.routes import main  # noqa: E402
    from flaskblog.posts.routes import posts  # noqa: E402
    from flaskblog.users.routes import users  # noqa: E402
    from flaskblog.errors.handlers import errors  # noqa: E402

    # Registering blueprints to the app.
    app.register_blueprint(main)
    app.register_blueprint(posts)
    app.register_blueprint(users)
    app.register_blueprint(errors)

    # Initialising the extensions created outside this function with the app.
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    return app
