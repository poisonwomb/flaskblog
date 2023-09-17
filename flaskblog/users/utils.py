import secrets
from pathlib import Path

from flask import url_for, current_app
from flask_login import current_user
from flask_mail import Message
from PIL import Image

from flaskblog import mail


def save_picture(form_picture):
    pics_path = Path(current_app.root_path) / "static/profile_pics"
    random_hex = secrets.token_hex(8)
    f_ext = Path(form_picture.filename).suffix

    picture_filename = random_hex + f_ext
    new_picture_path = pics_path / picture_filename
    prev_picture_path = pics_path / current_user.image_file

    output_size = (250, 250)
    # Create a new pillow image object from the uploaded picture.
    image = Image.open(form_picture)
    # Reduce the image to the size in output_size.
    image.thumbnail(output_size)

    if prev_picture_path.exists():
        # Delete the previous picture.
        prev_picture_path.unlink()
    image.save(new_picture_path)
    return picture_filename


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(
        subject="Password Reset", sender="max@suslowicz.co", recipients=[user.email]
    )
    msg.body = f"""To reset yout password, visit the following link:
{url_for(endpoint="users.reset_token", token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made."""
    mail.send(msg)
