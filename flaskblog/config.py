import os


class Config:
    # App encryption key and database settings.
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")

    # Setting up email credentials.
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = os.environ.get("MAIL_PORT")
    MAIL_USE_TLS = bool(os.environ.get("MAIL_USE_TLS"))
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
