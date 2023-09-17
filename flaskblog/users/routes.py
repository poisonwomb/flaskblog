from flask import Blueprint, redirect, url_for, flash, request, render_template
from flask_login import current_user, login_user, logout_user, login_required

from flaskblog import db, bcrypt
from flaskblog.models import AppUser, Post
from flaskblog.users.forms import (
    RegistrationForm,
    LoginForm,
    RequestResetForm,
    ResetPasswordForm,
    UpdateAccountForm,
)
from flaskblog.users.utils import save_picture, send_reset_email

users = Blueprint("users", __name__)


# methods parameter denotes the HTTP methods this route will accept.
@users.route(rule="/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    """This instantiates the form class imported from forms.py that
    is then passed to register.html using Jinja templating."""
    form = RegistrationForm()
    # Validate the input of the form
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = AppUser(
            username=form.username.data, email=form.email.data, password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        """Flash (Flask class) allows you to show a message (message parameter).
        Category parameter is the bootstrap css class 'success' for styling."""
        flash(
            message="Your account has been created! You are now able to log in.",
            category="success",
        )
        # url_for dynamically retrieves the URL of the home route.
        return redirect(url_for("users.login"))
    return render_template("register.html", title="Register", form=form)


@users.route(rule="/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    # If input passes the validation defined in forms.py...
    if form.validate_on_submit():
        # Query the database for the user, using their email.
        user = AppUser.query.filter_by(email=form.email.data).first()
        # Check user exists and password matches hashed password.
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # Log the user in with flask_login.
            login_user(user, remember=form.remember.data)
            # Get the (optional) 'next' argument passed by the prev page.
            next_page = request.args.get("next")
            # If the 'next' argument was provided, redirect to that page, else home.
            return redirect(next_page) if next_page else redirect(url_for("main.home"))
        else:
            flash(
                message="Invalid login credentials!",
                category="danger",
            )
    return render_template("login.html", title="Login", form=form)


@users.route(rule="/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home"))


@users.route(rule="/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash(message="Your account has been updated!", category="success")
        return redirect(url_for("users.account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for("static", filename="profile_pics/" + current_user.image_file)
    return render_template(
        "account.html", title="Account", image_file=image_file, form=form
    )


@users.route(rule="/user/<string:username>")
def user_posts(username):
    user = AppUser.query.filter_by(username=username).first_or_404()
    page = request.args.get("page", default=1, type=int)
    posts = (
        Post.query.filter_by(author=user)
        .order_by(Post.posted_date.desc())
        .paginate(per_page=5, page=page)
    )
    return render_template(
        template_name_or_list="user_posts.html", posts=posts, user=user
    )


@users.route(rule="/reset_password", methods=["GET", "POST"])
def reset_request():
    # If the user is already logged in, redirect them to the homepage.
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = AppUser.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash(
            message="An email has been sent with instructions on resetting your password.",
            category="info",
        )
        return redirect(url_for("users.login"))
    return render_template(
        template_name_or_list="reset_request.html", title="Reset Password", form=form
    )


@users.route(rule="/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    # If the user is already logged in, redirect them to the homepage.
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    user = AppUser.verify_reset_token(token)
    if user is None:
        flash(message="That is an invalid or expired token!", category="warning")
        return redirect(url_for("users.reset_request"))
    form = ResetPasswordForm()
    # Validate the input of the form
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user.password = hashed_password
        db.session.commit()
        """Flash (Flask class) allows you to show a message (message parameter).
        Category parameter is the bootstrap css class 'success' for styling."""
        flash(
            message="Your password has been updated! You are now able to log in.",
            category="success",
        )
        # url_for dynamically retrieves the URL of the home route.
        return redirect(url_for("users.login"))
    return render_template(
        template_name_or_list="reset_token.html", title="Reset Password", form=form
    )
