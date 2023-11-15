from datetime import datetime

import itsdangerous.exc
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer

from flask import current_app
from flaskblog import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return AppUser.query.get_or_404(int(user_id))


class AppUser(db.Model, UserMixin):
    """Because this name is camelcase, SQLAlchemy will add an _ between 'App' and 'User'.
    The actual table name is 'app_user'.

    This class inherits from db.Model so it can connect with SQLAlchemy.
    UserMixin provides methods that help with logging users in.
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default="default.png")
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship("Post", backref="author", lazy=True)

    def get_reset_token(self):
        # Create a serializer object using our secret key.
        s = Serializer(secret_key=current_app.config["SECRET_KEY"])
        # Serialize the user ID so it can be used as a token.
        return s.dumps({"user_id": self.id})

    # We do not do anything with the instance of AppUser so this method can be static.
    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(secret_key=current_app.config["SECRET_KEY"])
        # If the string cannot be deserialized/has expired we will get an error here.
        try:
            # max_age is the maximum age of the token in seconds.
            user_id = s.loads(token, max_age=expires_sec)["user_id"]
        except itsdangerous.exc.BadSignature:
            return None
        return AppUser.query.get_or_404(user_id)

    def __repr__(self):
        return f"AppUser('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    posted_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("app_user.id"), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.posted_date}'"


