from datetime import datetime
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
    image_file = db.Column(db.String(20), nullable=False, default="default.jpg")
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship("Post", backref="author", lazy=True)

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
